"""Separate live model checks: saves only synthetic evaluation examples."""
import asyncio,json,sys
from pathlib import Path
from uuid import uuid4
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"backend"))
from samjha import inference
from samjha.schemas import LearnRequest
async def main():
    cases=json.loads((ROOT/"data"/"evaluation.json").read_text(encoding="utf-8"))
    rows=[]
    for case in cases["held_out"] if "--all" in sys.argv else [x for x in cases["held_out"] if x["id"] in ("hinglish","multistep")]:
        req=LearnRequest(request_id=uuid4(),conversation_id=uuid4(),task=case["task"],question=case["question"],answer=case.get("answer",""),language=case.get("language","English"))
        try:
            result,latency=await inference.generate(req)
            rows.append({"id":case["id"],"latency_seconds":latency,"feedback":result.model_dump(),"expected_for_human_review":case["expected"],"schema_valid":True})
        except inference.ModelError as e:rows.append({"id":case["id"],"error":e.code,"message":e.message,"schema_valid":False})
        print(json.dumps(rows[-1],ensure_ascii=True),flush=True)
    out=ROOT/"docs"/"live-evaluation-retest.json"
    out.write_text(json.dumps({"notice":"Real model output. Expected answers are unreviewed original authoring; no quality score claimed.","results":rows},ensure_ascii=False,indent=2),encoding="utf-8")
if __name__=="__main__":asyncio.run(main())
