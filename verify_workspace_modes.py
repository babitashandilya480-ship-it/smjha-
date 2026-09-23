"""Small live smoke check, not a benchmark or training run."""
import json,time,uuid
from pathlib import Path
import httpx

root=Path(__file__).resolve().parents[1]
results=[]
with httpx.Client(base_url='http://127.0.0.1:8000/api/v1',headers={'X-Samjha-Local':'1'},timeout=100) as client:
    response=client.post('/auth/register',json={'username':'qa_modes_'+uuid.uuid4().hex[:12],'password':uuid.uuid4().hex})
    response.raise_for_status()
    try:
        doc=client.post('/documents/reference').json()
        for mode,prompt in [('chat','According to the PDF, what is accuracy? Answer in one sentence with a page citation.'),('work','Draft a concise three-step plan to evaluate a chatbot. Use the PDF and cite pages.'),('hyper','A classifier gets 18 out of 20 examples correct. Calculate its accuracy, then explain why accuracy alone is insufficient. Use the PDF and cite pages.')]:
            key=client.post('/conversations',json={'route':'local'}).json()['id']
            start=time.monotonic()
            response=client.post('/conversations/'+key+'/messages',json={'request_id':str(uuid.uuid4()),'content':prompt,'mode':mode,'effort':'quick','document_id':doc['id']})
            response.raise_for_status()
            run=response.json()['id']
            first=None
            terminal=None
            with client.stream('GET','/runs/'+run+'/events') as stream:
                stream.raise_for_status()
                for line in stream.iter_lines():
                    if not line.startswith('data: '): continue
                    event=json.loads(line[6:])
                    if event['type']=='text.delta' and first is None: first=round(time.monotonic()-start,3)
                    if event['type'] in ('run.completed','run.failed','run.cancelled'): terminal=event
            view=client.get('/conversations/'+key).json()
            answer=next((m['content'] for m in view['messages'] if m['role']=='assistant'),'')
            result={'mode':mode,'model':view['runs'][0]['model'],'first_text_seconds':first,'total_seconds':round(time.monotonic()-start,3),'terminal':terminal,'answer':answer,'source_count':len(view.get('sources',{}).get(run,[]))}
            results.append(result)
            print(json.dumps({k:v for k,v in result.items() if k not in ('terminal','answer')})+' '+answer[:250],flush=True)
    finally:
        client.delete('/account')
(root/'artifacts/live-workspace-modes.json').write_text(json.dumps(results,indent=2,ensure_ascii=False),encoding='utf-8')
assert all(r['terminal']['type']=='run.completed' and r['answer'] and r['source_count'] for r in results), 'A live mode failed'
