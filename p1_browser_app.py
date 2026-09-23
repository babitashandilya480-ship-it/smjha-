"""Explicitly synthetic browser-test service. Never use this entrypoint for real chat."""
import asyncio
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'backend'))
from samjha import foundation_provider as provider
from samjha.api import app

async def info(mode="chat",effort="quick"):
    return {'available':True,'model':'SYNTHETIC-BROWSER-FIXTURE','digest':'fixture-only'}

async def stream(messages,effort,mode="chat"):
    if 'failure fixture' in messages[-1]['content']:
        raise provider.ProviderError('fixture_failure','Synthetic provider failure. Retry is available.')
    for part in ['Synthetic browser fixture: ','नमस्ते। ','This is not a real model answer.']:
        await asyncio.sleep(0.2)
        yield {'text':part}
    if 'slow fixture' in messages[-1]['content']:
        await asyncio.sleep(20)
    yield {'usage':{'done_reason':'stop','eval_count':10,'prompt_eval_count':20}}

provider.model_info=info
provider.stream=stream
