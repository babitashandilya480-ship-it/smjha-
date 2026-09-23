"""Deterministic P1 fixtures. Provider responses below are mocks, not quality evidence."""
import asyncio
import importlib.util
import json
import sys
from pathlib import Path
from uuid import uuid4
import httpx
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'backend'))
from fastapi.testclient import TestClient
from samjha import api,config,foundation_api as chat,foundation_store as store,foundation_provider as provider,cloud_provider as cloud
HEAD={'X-Samjha-Local':'1'}
PASSWORD='test-password-1234'

@pytest.fixture
def client(tmp_path,monkeypatch):
    monkeypatch.setattr(config,'DB_PATH',tmp_path/'legacy.sqlite3')
    monkeypatch.setenv('SAMJHA_CHAT_DB',str(tmp_path/'chat.sqlite3'))
    monkeypatch.setenv('CI_ENABLED','false')
    monkeypatch.setenv('CI_API_KEY','')
    monkeypatch.setenv('CI_MAX_REQUESTS','0')
    chat.attempts.clear()
    api.gate=asyncio.Lock()
    async def info(mode="chat",effort="quick"): return {'available':True,'model':'fixture-local','digest':'fixture-digest'}
    async def stream(messages,effort,mode="chat"):
        yield {'text':'नमस्ते — fixture '}
        yield {'text':'answer'}
        yield {'usage':{'prompt_eval_count':10,'eval_count':4,'done_reason':'stop'}}
    monkeypatch.setattr(provider,'model_info',info)
    monkeypatch.setattr(provider,'stream',stream)
    with TestClient(api.app,headers=HEAD) as value:
        yield value

def account(c,name='alice'):
    r=c.post('/api/v1/auth/register',json={'username':name,'password':PASSWORD})
    assert r.status_code==200,r.text
    return r

def conversation(c,route='local'):
    r=c.post('/api/v1/conversations',json={'route':route})
    assert r.status_code==200,r.text
    return r.json()['id']

def submit(c,key,content='Explain recursion',request_id=None):
    return c.post('/api/v1/conversations/'+key+'/messages',json={'request_id':request_id or str(uuid4()),'content':content})

def events(c,key,headers=None):
    response=c.get('/api/v1/runs/'+key+'/events',headers=headers)
    assert response.status_code==200,response.text
    return [json.loads(line[6:]) for line in response.text.splitlines() if line.startswith('data: ')]

def test_auth_cookie_logout_and_revocation(client):
    assert client.get('/api/v1/conversations').status_code==401
    r=account(client)
    assert 'HttpOnly' in r.headers['set-cookie'] and 'SameSite=strict' in r.headers['set-cookie']
    old=client.cookies.get(chat.COOKIE)
    assert client.get('/api/v1/auth/me').json()['username']=='alice'
    client.post('/api/v1/auth/logout')
    assert client.get('/api/v1/conversations',headers={'Cookie':chat.COOKIE+'='+old}).status_code==401
    assert client.post('/api/v1/auth/login',json={'username':'alice','password':PASSWORD+'bad'}).status_code==401
    assert client.post('/api/v1/auth/login',json={'username':'alice','password':PASSWORD}).status_code==200


def test_guest_can_chat_without_signup_and_shares_local_history(client):
    response=client.post('/api/v1/auth/guest')
    assert response.status_code==200,response.text
    guest=response.json()
    assert guest['username']=='guest'
    assert client.get('/api/v1/auth/me').json()==guest
    assert client.post('/api/v1/auth/register',json={'username':'guest','password':PASSWORD}).status_code==409
    key=conversation(client)
    run=submit(client,key,'Tell me a useful fact').json()['id']
    assert events(client,run)[-1]['type']=='run.completed'
    other=TestClient(api.app,headers=HEAD)
    with other:
        second=other.post('/api/v1/auth/guest')
        assert second.status_code==200 and second.json()==guest
        assert other.get('/api/v1/conversations').json()[0]['id']==key
        assert other.get('/api/v1/conversations/'+key).json()['messages'][0]['content']=='Tell me a useful fact'

def test_public_guest_sessions_are_isolated_and_legacy_api_is_closed(client,monkeypatch):
    monkeypatch.setattr(config,'PUBLIC_MODE',True)
    with TestClient(api.app,headers=HEAD,base_url='https://testserver') as first, TestClient(api.app,headers=HEAD,base_url='https://testserver') as second:
        assert first.get('/api/health').status_code==503
        one=first.post('/api/v1/auth/guest')
        two=second.post('/api/v1/auth/guest')
        assert one.status_code==two.status_code==200
        assert one.json()['id']!=two.json()['id']
        assert 'Secure' in one.headers['set-cookie']
        assert first.get('/api/v1/auth/me').json()['username']=='guest'
        key=conversation(first)
        assert second.get('/api/v1/conversations').json()==[]
        assert second.get('/api/v1/conversations/'+key).status_code==404
        assert first.get('/api/history').status_code==404

def test_cross_user_conversations_runs_stream_cancel_export(client):
    account(client)
    key=conversation(client)
    run=submit(client,key).json()['id']
    events(client,run)
    client.cookies.clear()
    account(client,'bob')
    assert client.get('/api/v1/conversations').json()==[]
    for url in ['/conversations/'+key,'/runs/'+run,'/runs/'+run+'/events']:
        assert client.get('/api/v1'+url).status_code==404
    assert client.post('/api/v1/runs/'+run+'/cancel').status_code==404
    assert submit(client,key).status_code==404
    assert client.get('/api/v1/export').json()['conversations']==[]

def test_stream_persistence_replay_idempotency(client):
    account(client)
    key=conversation(client)
    rid=str(uuid4())
    run=submit(client,key,request_id=rid).json()['id']
    stream=events(client,run)
    assert stream[-1]['type']=='run.completed'
    assert [e['seq'] for e in stream]==list(range(1,len(stream)+1))
    assert all(e['schema_version']==1 and e['run_id']==run for e in stream)
    assert submit(client,key,request_id=rid).json()['id']==run
    assert submit(client,key,'changed',rid).status_code==409
    replay=events(client,run,{'Last-Event-ID':'2'})
    assert all(e['seq']>2 for e in replay)
    saved=client.get('/api/v1/conversations/'+key).json()
    assert len(saved['messages'])==2
    assert saved['messages'][1]['content']=='नमस्ते — fixture answer'
    assert saved['runs'][0]['model_digest']=='fixture-digest'

def test_failure_retains_user_and_partial_not_final(client,monkeypatch):
    async def broken(*args):
        yield {'text':'Partial'}
        raise provider.ProviderError('provider_error','Provider unavailable')
    monkeypatch.setattr(provider,'stream',broken)
    account(client)
    key=conversation(client)
    run=submit(client,key).json()['id']
    stream=events(client,run)
    assert stream[-1]['type']=='run.failed'
    assert client.get('/api/v1/conversations/'+key).json()['messages'][0]['role']=='user'
    assert len(client.get('/api/v1/conversations/'+key).json()['messages'])==1

def test_cancel_and_gate_release(client,monkeypatch):
    async def slow(*args):
        yield {'text':'Partial'}
        await asyncio.sleep(10)
        yield {'text':'Late'}
    monkeypatch.setattr(provider,'stream',slow)
    account(client)
    key=conversation(client)
    run=submit(client,key).json()['id']
    assert submit(client,key).status_code==429
    assert client.post('/api/v1/runs/'+run+'/cancel').json()['state']=='cancelled'
    stream=events(client,run)
    assert stream[-1]['type']=='run.cancelled'
    assert not any(e['data'].get('text')=='Late' for e in stream)
    assert not api.gate.locked()

def test_context_and_mode_fail_closed(client,monkeypatch):
    account(client);key=conversation(client)
    monkeypatch.setattr(provider,'MAX_INPUT_BYTES',100)
    assert submit(client,key,'a'*200).status_code==422
    assert client.get('/api/v1/conversations/'+key).json()['messages']==[]
    assert client.post('/api/v1/conversations/'+key+'/messages',json={'request_id':str(uuid4()),'content':'hello','mode':'hyper'}).status_code==422

def test_disabled_cloud_and_local_no_fallback(client,monkeypatch):
    account(client)
    assert client.post('/api/v1/conversations',json={'route':'cloud'}).status_code==503
    def forbidden(*args): raise AssertionError('cloud was called')
    monkeypatch.setattr(cloud,'stream',forbidden)
    key=conversation(client)
    assert events(client,submit(client,key).json()['id'])[-1]['type']=='run.completed'

def test_csrf_body_limits_and_validation(client):
    assert client.post('/api/v1/auth/register',headers={'Origin':'https://evil.example'},json={}).status_code==403
    assert client.post('/api/v1/auth/register',headers={'X-Samjha-Local':'0'},json={}).status_code==403
    assert client.post('/api/v1/auth/register',json={'username':'x','password':'short'}).status_code==422
    assert client.post('/api/v1/auth/register',content='x'*70000).status_code==413

def test_delete_cascade_and_legacy_preservation(client):
    account(client);key=conversation(client)
    events(client,submit(client,key).json()['id'])
    assert client.get('/api/v1/export').json()['conversations']
    assert client.delete('/api/v1/account').status_code==200
    assert client.get('/api/v1/auth/me').status_code==401
    with store.connect() as c:
        for table in ['users','sessions','conversations','runs','messages','events']:
            assert c.execute('SELECT count(*) FROM '+table).fetchone()[0]==0

def test_restart_marks_interrupted_once(client):
    account(client);key=conversation(client)
    with store.connect() as c:
        c.execute('INSERT INTO runs VALUES(?,?,?,?,?,?,?,?,?)',('interrupted',key,str(uuid4()),'hash','running','fixture','digest','quick',store.now()))
    store.init();store.init()
    with store.connect() as c:
        assert c.execute("SELECT state FROM runs WHERE id='interrupted'").fetchone()[0]=='failed'
        assert c.execute("SELECT count(*) FROM events WHERE run_id='interrupted'").fetchone()[0]==1

@pytest.fixture
def cloud_setup(tmp_path,monkeypatch):
    monkeypatch.setenv('SAMJHA_CHAT_DB',str(tmp_path/'cloud.sqlite3'))
    monkeypatch.setenv('CI_ENABLED','true');monkeypatch.setenv('CI_API_KEY','synthetic-test-key')
    monkeypatch.setenv('CI_MAX_REQUESTS','2')
    monkeypatch.setenv('CI_MODEL','fixture-model')
    return monkeypatch

def cloud_mock(monkeypatch,handler):
    original=httpx.AsyncClient
    monkeypatch.setattr(cloud.httpx,'AsyncClient',lambda **kwargs:original(transport=httpx.MockTransport(handler),**kwargs))

async def collect():
    return [x async for x in cloud.stream([{'role':'user','content':'hello'}],'quick')]

def test_cloud_sse_contract_and_allowance(cloud_setup):
    requests=[]
    def handler(request):
        requests.append(request)
        payload=json.loads(request.content)
        assert payload['model']=='fixture-model' and payload['max_tokens']==256
        assert payload['zdr'] is True and 'tools' not in payload
        assert request.headers['authorization']=='Bearer synthetic-test-key'
        return httpx.Response(200,text='data: {"choices":[{"delta":{"content":"Hello"},"finish_reason":null}]}\n\ndata: {"choices":[{"delta":{},"finish_reason":"stop"}],"usage":{"prompt_tokens":2,"completion_tokens":1}}\n\ndata: [DONE]\n\n')
    cloud_mock(cloud_setup,handler)
    assert asyncio.run(collect())[0]['text']=='Hello'
    asyncio.run(collect())
    with pytest.raises(provider.ProviderError,match='allowance'): asyncio.run(collect())
    assert len(requests)==2

@pytest.mark.parametrize('status,code',[(401,'authentication'),(402,'quota'),(403,'permission'),(404,'model_missing'),(429,'rate_limit'),(503,'provider_error')])
def test_cloud_error_redaction_no_retry(cloud_setup,status,code):
    calls=[]
    def handler(request):
        calls.append(request)
        return httpx.Response(status,text='private prompt and synthetic-test-key')
    cloud_mock(cloud_setup,handler)
    with pytest.raises(provider.ProviderError) as exc: asyncio.run(collect())
    assert exc.value.code==code and 'synthetic-test-key' not in str(exc.value)
    assert len(calls)==1

@pytest.mark.parametrize('body',['data: not-json\n\n','data: {"error":{"message":"private"}}\n\n','data: {"choices":[{"delta":{"content":"Partial"}}]}\n\n'])
def test_cloud_malformed_or_incomplete(cloud_setup,body):
    cloud_mock(cloud_setup,lambda _:httpx.Response(200,text=body))
    with pytest.raises(provider.ProviderError): asyncio.run(collect())

def test_local_route_rejects_external(monkeypatch):
    monkeypatch.setattr(config,'OLLAMA_URL','https://example.com')
    with pytest.raises(provider.ProviderError): provider.endpoint()

def test_review_helper_rejects_secret_and_outside_paths():
    path=Path(__file__).resolve().parents[1]/'scripts'/'design_review.py'
    spec=importlib.util.spec_from_file_location('design_review',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    with pytest.raises(ValueError):module.prepare('review',['backend/.env.cloud'])
    with pytest.raises(ValueError):module.prepare('review',['../private.txt'])
    with pytest.raises(ValueError):module.prepare('ci_live_'+'a'*32,[])
    assert module.prepare('Review this proposed button label',[])[1]['role']=='user'


def test_modes_are_routed_and_recorded(client,monkeypatch):
    seen=[]
    async def info(mode='chat',effort='quick'):
        return {'available':True,'model':'fixture-'+mode}
    async def stream(messages,effort,mode='chat'):
        seen.append((mode,messages[0]['content']))
        yield {'text':'Mode verified'}
    monkeypatch.setattr(provider,'model_info',info)
    monkeypatch.setattr(provider,'stream',stream)
    account(client)
    caps=client.get('/api/v1/capabilities').json()
    assert set(caps['local'])=={'chat','hyper','work'}
    for mode in ('chat','hyper','work'):
        key=conversation(client)
        r=client.post('/api/v1/conversations/'+key+'/messages',json={'request_id':str(uuid4()),'content':'Help me plan','mode':mode})
        assert events(client,r.json()['id'])[-1]['type']=='run.completed'
        view=client.get('/api/v1/conversations/'+key).json()
        assert view['runs'][0]['model']=='fixture-'+mode
        assert seen[-1]==(mode,provider.SYSTEM_PROMPTS[mode])

def test_pdf_ownership_retrieval_and_source_persistence(client,monkeypatch):
    from samjha import chat_documents
    account(client)
    identity=client.get('/api/v1/auth/me').json()
    doc=chat_documents.save(identity,'Test reference',[{'pdf_page':2,'text':'A regression benchmark measures accuracy and latency against a fixed evaluation dataset.'}],'fixture')
    captured=[]
    async def stream(messages,effort,mode='chat'):
        captured.append(messages)
        yield {'text':'Use a fixed evaluation dataset [PDF p. 2].'}
    monkeypatch.setattr(provider,'stream',stream)
    key=conversation(client)
    r=client.post('/api/v1/conversations/'+key+'/messages',json={'request_id':str(uuid4()),'content':'What does a regression benchmark measure?','document_id':doc['id']})
    assert r.status_code==200,r.text
    assert events(client,r.json()['id'])[-1]['type']=='run.completed'
    assert '[PDF p. 2]' in captured[0][0]['content']
    view=client.get('/api/v1/conversations/'+key).json()
    assert view['sources'][r.json()['id']][0]['pdf_page']==2
    client.cookies.clear()
    account(client,'bob')
    assert client.get('/api/v1/documents').json()==[]
    assert client.delete('/api/v1/documents/'+doc['id']).status_code==404
    other=conversation(client)
    assert client.post('/api/v1/conversations/'+other+'/messages',json={'request_id':str(uuid4()),'content':'benchmark','document_id':doc['id']}).status_code==404

def test_invalid_pdf_and_unmatched_query(client):
    from samjha import chat_documents
    account(client)
    assert client.post('/api/v1/documents',files={'file':('bad.pdf',b'not a pdf','application/pdf')}).status_code==422
    identity=client.get('/api/v1/auth/me').json()
    doc=chat_documents.save(identity,'Reference',[{'pdf_page':1,'text':'The evaluation dataset measures latency.'}],'testdoc')
    key=conversation(client)
    assert client.post('/api/v1/conversations/'+key+'/messages',json={'request_id':str(uuid4()),'content':'zebras','document_id':doc['id']}).status_code==422
    assert client.get('/api/v1/conversations/'+key).json()['messages']==[]
    assert client.delete('/api/v1/documents/'+doc['id']).status_code==200

def test_pdf_upload_roundtrip_duplicate_and_cascade(client):
    from test_boundaries import pdf
    account(client)
    raw=pdf(["Accuracy equals correct predictions divided by all predictions in this evaluation.", "Latency measures the time needed to produce an answer."])
    response=client.post('/api/v1/documents',files={'file':('reference.pdf',raw,'application/pdf')})
    assert response.status_code==200,response.text
    key=response.json()['id']
    duplicate=client.post('/api/v1/documents',files={'file':('same.pdf',raw,'application/pdf')})
    assert duplicate.json()['id']==key
    assert client.get('/api/v1/documents').json()[0]['pages']==2
    assert client.delete('/api/v1/account').status_code==200
    with store.connect() as c:
        assert c.execute('SELECT count(*) FROM chat_documents').fetchone()[0]==0
        assert c.execute('SELECT count(*) FROM chat_chunks').fetchone()[0]==0


def test_supplied_pdfs_idempotent_and_cross_document_citations(client):
    account(client)
    client.post('/api/v1/documents/reference').raise_for_status()
    response=client.post('/api/v1/documents/supplied')
    assert response.status_code==200,response.text
    docs=response.json()
    assert [d['pages'] for d in docs]==[3,4,5,5,10]
    assert client.post('/api/v1/documents/supplied').json()==docs
    assert len(client.get('/api/v1/documents').json())==5
    key=conversation(client)
    response=client.post('/api/v1/conversations/'+key+'/messages',json={
        'request_id':str(uuid4()),'content':'Summarize model training and evaluation.',
        'document_ids':[d['id'] for d in docs]})
    assert response.status_code==200,response.text
    run=response.json()['id']
    events(client,run)
    view=client.get('/api/v1/conversations/'+key).json()
    assert len({s['title'] for s in view['sources'][run]})==4
    assert len(view['sources'][run])<=4
    from samjha import chat_documents
    identity=client.get('/api/v1/auth/me').json()
    passages=chat_documents.retrieve(docs[2]['id'],'Name the three main stages in How Frontier LLMs Are Built',identity)
    assert any('Pretraining' in p['text'] and 'Post-training' in p['text'] and 'Reasoning / agentic RL' in p['text'] for p in passages)
    passages=chat_documents.retrieve(docs[3]['id'],'What are ROLE CAPABILITIES OPERATING MODE STANDARDS OUTPUT FORMAT?',identity)
    assert any(p['pdf_page']==3 and 'OPERATING MODE' in p['text'] for p in passages)
    assert all(p['pdf_page']!=2 for p in passages)
    foreign_id=docs[0]['id']
    client.cookies.clear();account(client,'reader_two')
    key=conversation(client)
    response=client.post('/api/v1/conversations/'+key+'/messages',json={
        'request_id':str(uuid4()),'content':'Summarize','document_ids':[foreign_id]})
    assert response.status_code==404


def test_batched_stream_loses_no_text_and_persists_metrics(client,monkeypatch):
    async def fast(*args):
        for part in ['a','b','c','d']:
            yield {'text':part}
        yield {'usage':{'eval_count':4,'eval_duration':200000000,'load_duration':1000000,'done_reason':'stop'}}
    monkeypatch.setattr(provider,'stream',fast)
    account(client);key=conversation(client)
    run=submit(client,key).json()['id']
    stream=events(client,run)
    deltas=[e['data']['text'] for e in stream if e['type']=='text.delta']
    assert ''.join(deltas)=='abcd'
    assert len(deltas)<4
    view=client.get('/api/v1/conversations/'+key).json()
    assert view['messages'][-1]['content']=='abcd'
    assert view['metrics'][run]['tokens_per_second']==20
    assert 0<=view['metrics'][run]['first_text_ms']<=view['metrics'][run]['total_ms']


def test_quick_and_reasoning_models_are_routed_without_retries(monkeypatch):
    original=httpx.AsyncClient
    seen=[]
    def handler(request):
        payload=json.loads(request.content);seen.append(payload)
        return httpx.Response(200,text=json.dumps({'message':{'content':'Answer'},'done':True,'eval_duration':20,'load_duration':10})+'\n')
    monkeypatch.setattr(provider.httpx,'AsyncClient',lambda **kwargs:original(transport=httpx.MockTransport(handler),**kwargs))
    monkeypatch.setattr(config,'MODELS',{'chat':'fast','hyper':'deep','work':'fast'})
    monkeypatch.setattr(config,'HYPER_QUICK_MODEL','fast')
    async def check():
        for effort in ('quick','balanced'):
            output=[item async for item in provider.stream([{'role':'user','content':'Question'}],effort,'hyper')]
            assert output[-1]['usage']['load_duration']==10
    asyncio.run(check())
    assert [(p['model'],p['think']) for p in seen]==[('fast',False),('deep',True)]
