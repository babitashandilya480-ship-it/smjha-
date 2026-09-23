"""Live local smoke checks for the three user-supplied references, isolated data."""
import json
import os
import re
import sys
import tempfile
from pathlib import Path
from uuid import uuid4

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'backend'))
from fastapi.testclient import TestClient
from samjha import config,api

def validate(results):
    for result in results:
        # Models may use equivalent parenthesized or square-bracket page references.
        cited={int(page) for page in re.findall(r'(?:PDF\s+p\.|&\s*p\.)\s*(\d+)',result['answer'])}
        available={source['pdf_page'] for source in result['sources']}
        result['has_page_citation']=bool(cited) and cited.issubset(available)
    assert all(r['state']=='run.completed' and r['answer'] and r['sources'] and r['has_page_citation'] for r in results)
    assert 'reasoning' in results[1]['answer'].lower() or 'agentic' in results[1]['answer'].lower(), 'Third training stage omitted'

if '--validate-existing' in sys.argv:
    report=ROOT/'artifacts/supplied-pdf-live-check.json'
    results=json.loads(report.read_text(encoding='utf-8'))
    validate(results)
    report.write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
    print('All 5 recorded live cases completed with source-backed page references; the training-stage check passed.')
    raise SystemExit(0)

cases=[
    ('chat','quick',0,'According to the evaluation guide, what is accuracy? Give one sentence with a PDF page citation.'),
    ('work','quick',2,'According to How Frontier LLMs Are Built, name the three main stages. Be concise and cite the PDF page.'),
    ('hyper','quick',1,'According to the supplied system card summary, does it publish the model architecture or training formulas? Answer briefly and cite a PDF page.'),
    ('hyper','balanced',0,'A classifier gets 18 out of 20 cases correct. Give its accuracy as a percentage, using the PDF formula and a page citation. Keep the answer brief.'),
    ('chat','quick',None,'Summarize what each of the three supplied documents covers. Name each document, keep it brief, and cite pages.'),
]
results=[]
with tempfile.TemporaryDirectory(prefix='samjha-pdf-check-') as folder:
    config.DB_PATH=Path(folder)/'legacy.sqlite3'
    os.environ['SAMJHA_CHAT_DB']=str(Path(folder)/'chat.sqlite3')
    os.environ['CI_ENABLED']='false'
    with TestClient(api.app,headers={'X-Samjha-Local':'1'}) as client:
        client.post('/api/v1/auth/register',json={'username':'pdf_test','password':'synthetic-pdf-test-password'}).raise_for_status()
        response=client.post('/api/v1/documents/supplied');response.raise_for_status();docs=response.json()
        for mode,effort,index,prompt in cases:
            key=client.post('/api/v1/conversations',json={'route':'local'}).json()['id']
            payload={'request_id':str(uuid4()),'content':prompt,'mode':mode,'effort':effort}
            payload.update({'document_id':docs[index]['id']} if index is not None else {'document_ids':[doc['id'] for doc in docs]})
            response=client.post('/api/v1/conversations/'+key+'/messages',json=payload)
            response.raise_for_status();run=response.json()['id']
            stream=client.get('/api/v1/runs/'+run+'/events')
            events=[json.loads(line[6:]) for line in stream.text.splitlines() if line.startswith('data: ')]
            view=client.get('/api/v1/conversations/'+key).json()
            answer=next((m['content'] for m in view['messages'] if m['role']=='assistant'),'')
            result={'mode':mode,'effort':effort,'reference':docs[index]['title'] if index is not None else 'all three',
                    'state':events[-1]['type'],'answer':answer,'model':view['runs'][0]['model'],
                    'metrics':view['metrics'].get(run),'sources':view['sources'].get(run,[]),
                    'has_page_citation':'[PDF p.' in answer}
            results.append(result)
            print(json.dumps({k:v for k,v in result.items() if k!='sources'},ensure_ascii=False),flush=True)
validate(results)
(ROOT/'artifacts/supplied-pdf-live-check.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
