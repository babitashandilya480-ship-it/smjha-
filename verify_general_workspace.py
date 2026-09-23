"""Real local model checks for general learning and the fourth supplied PDF."""
import json
import os
import sys
import tempfile
from pathlib import Path
from uuid import uuid4

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'backend'))
from fastapi.testclient import TestClient
from samjha import api,config

report={}
with tempfile.TemporaryDirectory(prefix='samjha-general-check-') as folder:
    config.DB_PATH=Path(folder)/'legacy.sqlite3'
    os.environ['SAMJHA_CHAT_DB']=str(Path(folder)/'chat.sqlite3')
    os.environ['CI_ENABLED']='false'
    with TestClient(api.app,headers={'X-Samjha-Local':'1'}) as client:
        response=client.post('/api/learn',json={
            'request_id':str(uuid4()),'conversation_id':str(uuid4()),'task':'doubt',
            'question':'Explain what a Python dictionary is, with one short example.',
            'language':'English'})
        response.raise_for_status()
        report['general_learning']=response.json()
        print(json.dumps({'general_learning':report['general_learning']['feedback']['samjho']},ensure_ascii=False),flush=True)
        response=client.post('/api/v1/auth/register',json={'username':'general_check','password':'synthetic-workspace-test-password'})
        response.raise_for_status()
        response=client.post('/api/v1/documents/supplied');response.raise_for_status()
        docs=response.json()
        guide=next(d for d in docs if 'Astra-Style Agent' in d['title'])
        conversation=client.post('/api/v1/conversations',json={'route':'local'}).json()['id']
        response=client.post('/api/v1/conversations/'+conversation+'/messages',json={
            'request_id':str(uuid4()),'mode':'work','effort':'quick','document_id':guide['id'],
            'content':'According to the prompting guide, list the five framework parts: use the exact section labels and cite the PDF page. Keep it brief.'})
        response.raise_for_status();run=response.json()['id']
        events=client.get('/api/v1/runs/'+run+'/events')
        view=client.get('/api/v1/conversations/'+conversation).json()
        answer=next((m['content'] for m in view['messages'] if m['role']=='assistant'),'')
        report['prompting_guide']={'answer':answer,'sources':view['sources'].get(run,[]),'metrics':view['metrics'].get(run),
                                  'state':view['runs'][0]['state'],'document_count':len(docs)}
        print(json.dumps({k:v for k,v in report['prompting_guide'].items() if k!='sources'},ensure_ascii=False),flush=True)
(ROOT/'artifacts/general-workspace-live-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
explanation=report['general_learning']['feedback']['samjho'].lower()
assert 'dictionary' in explanation and 'force and laws' not in explanation
assert report['prompting_guide']['state']=='completed'
assert all(label in answer.upper() for label in ('ROLE','CAPABILITIES','OPERATING MODE','STANDARDS','OUTPUT FORMAT'))
assert any(source['pdf_page']==3 for source in report['prompting_guide']['sources'])
