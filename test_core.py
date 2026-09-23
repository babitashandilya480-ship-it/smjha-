import asyncio
import json
import sys
from pathlib import Path
from uuid import uuid4
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"backend"))
from fastapi.testclient import TestClient
from samjha import api,config,db,inference,physics
from samjha.schemas import LearnRequest

Q="A 2 kg object accelerates at 3 m/s². Find the force."
HEAD={"X-Samjha-Local":"1"}
@pytest.fixture
def client(tmp_path,monkeypatch):
    monkeypatch.setattr(config,"DB_PATH",tmp_path/"test.sqlite3")
    api.gate=asyncio.Lock()
    with TestClient(api.app,headers=HEAD) as c:
        yield c
def request(answer="6 J"):
    return {"request_id":str(uuid4()),"conversation_id":str(uuid4()),"task":"check","question":Q,"answer":answer,"language":"English"}
@pytest.mark.parametrize("answer,verdict,category",[("6 N","correct","Needs clarification"),("2 * 3 N","correct","Needs clarification"),("(12 / 2) N","correct","Needs clarification"),("6 J","incorrect","Units"),("5 N","incorrect","Calculation"),("F = m/a = 0.66 N","incorrect","Formula"),("","clarify","Needs clarification")])
def test_calculations(answer,verdict,category):
    result=physics.check(Q,answer)
    assert result.verdict==verdict and result.category==category
def test_decimals_negative_conversion():
    assert physics.check("A 500 g mass has acceleration -2.5 m/s². Find force.","-1.25 N").verdict=="correct"
@pytest.mark.parametrize("language",["Hindi","Hinglish"])
def test_languages(language):
    assert physics.check(Q,"6 J",language).verdict=="incorrect"
def test_ambiguity_and_untrusted_expression():
    assert physics.check("Find the force.","6 N") is None
    with pytest.raises(ValueError): physics.arithmetic("__import__('os').system('dir')")
    assert physics.check(Q,"6 N or 8 N").verdict=="clarify"
def test_duplicate_save_retry_delete(client):
    req=request()
    r=client.post("/api/learn",json=req); assert r.status_code==200,r.text
    assert client.post("/api/learn",json=req).json()==r.json()
    req["answer"]="12 N"; assert client.post("/api/learn",json=req).status_code==409
    save={"interaction_id":r.json()["id"]}
    m=client.post("/api/mistakes",json=save).json()
    assert client.post("/api/mistakes",json=save).json()==m
    assert len(client.get("/api/mistakes").json())==1
    rev=client.post("/api/revisions",json={"request_id":str(uuid4())}).json()
    retry={"request_id":str(uuid4()),"revision_id":rev["id"],"answer":"6 N","language":"English"}
    t=client.post("/api/mistakes/"+m["id"]+"/retry",json=retry);assert t.status_code==200,t.text
    assert client.post("/api/mistakes/"+m["id"]+"/retry",json=retry).json()==t.json()
    assert client.post("/api/revisions/"+rev["id"]+"/complete").status_code==200
    p=client.get("/api/progress").json()
    assert p["questions_attempted"]==2 and p["retry_questions_correct"]==1 and p["revision_sessions_completed"]==1
    assert client.delete("/api/mistakes/"+m["id"]).status_code==200
    p=client.get("/api/progress").json()
    assert p["mistakes_saved"]==0 and p["retry_attempts"]==0 and p["revision_sessions_completed"]==0
def test_failed_model_not_counted(client,monkeypatch):
    async def missing(*args,**kwargs): raise inference.ModelError("model_not_found","Model missing")
    monkeypatch.setattr(inference,"generate",missing)
    req=request();req["task"]="doubt"
    assert client.post("/api/learn",json=req).status_code==503
    assert client.get("/api/history").json()==[]
def test_edit_invalidates_old_retries(client):
    r=client.post("/api/learn",json=request()).json()
    m=client.post("/api/mistakes",json={"interaction_id":r["id"]}).json()
    rev=client.post("/api/revisions",json={"request_id":str(uuid4())}).json()
    client.post("/api/mistakes/"+m["id"]+"/retry",json={"request_id":str(uuid4()),"revision_id":rev["id"],"answer":"6 N"})
    item=client.get("/api/mistakes").json()[0]
    payload={k:item[k] for k in ("question","student_answer","issue","correction","retry_question","category")}
    assert client.put("/api/mistakes/"+m["id"],json=payload).status_code==200
    assert client.get("/api/progress").json()["retry_attempts"]==0
def test_local_security(client):
    assert client.post("/api/learn",json=request(),headers={"Origin":"https://evil.example"}).status_code==403
    assert client.post("/api/learn",json={"question":"x"*70000}).status_code==413
def test_full_deletion(client):
    client.post("/api/learn",json=request())
    assert client.delete("/api/history").status_code==200
    assert client.get("/api/history").json()==[]
