"""Real local model smoke test, isolated from all user history and all cloud calls."""
import os
import sys
import json
import tempfile
import time
from pathlib import Path
from uuid import uuid4
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'backend'))
from fastapi.testclient import TestClient
from samjha import config,api
report={'scope':'P1 real local model smoke, synthetic inputs only','cases':[]}
with tempfile.TemporaryDirectory(prefix='samjha-live-') as folder:
 config.DB_PATH=Path(folder)/'legacy.sqlite3'
 os.environ['SAMJHA_CHAT_DB']=str(Path(folder)/'chat.sqlite3')
 os.environ['CI_ENABLED']='false'
 with TestClient(api.app,headers={'X-Samjha-Local':'1'}) as c:
  r=c.post('/api/v1/auth/register',json={'username':'smoke_user','password':'synthetic-test-password'})
  assert r.status_code==200,r.text
  report['capability']=c.get('/api/v1/capabilities').json()['local']
  for prompt in ['Write one short caption for a photo of a sunrise.','Recursion ko Hinglish mein do chhote sentences mein samjhao.']:
   key=c.post('/api/v1/conversations',json={'route':'local'}).json()['id']
   started=time.monotonic()
   r=c.post('/api/v1/conversations/'+key+'/messages',json={'request_id':str(uuid4()),'content':prompt,'effort':'quick'})
   case={'prompt':prompt,'http_status':r.status_code}
   if r.status_code==200:
    stream=c.get('/api/v1/runs/'+r.json()['id']+'/events')
    data=[json.loads(line[6:]) for line in stream.text.splitlines() if line.startswith('data: ')]
    saved=c.get('/api/v1/conversations/'+key).json()
    case.update({'terminal_event':data[-1] if data else None,'messages':saved['messages'],'run':saved['runs'][-1] if saved['runs'] else None})
   else:case['error']=r.json()
   case['seconds']=round(time.monotonic()-started,2)
   report['cases'].append(case)
report['passed']=all(c.get('terminal_event',{}).get('type')=='run.completed' and len(c.get('messages',[]))==2 for c in report['cases'])
out=ROOT/'artifacts'/'p1-live-smoke.json'
out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'passed':report['passed'],'model':report['capability'],'cases':[{'seconds':c['seconds'],'status':c.get('terminal_event',{}).get('type',c['http_status'])} for c in report['cases']],'report':str(out)},ensure_ascii=False))
sys.exit(0 if report['passed'] else 1)
