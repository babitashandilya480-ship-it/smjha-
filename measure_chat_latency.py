"""Local inference timings; writes only an explicitly named diagnostic report."""
import argparse
import asyncio
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'backend'))
from samjha import foundation_provider as provider

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    results = []
    for mode in ('chat', 'hyper', 'work'):
        start = time.perf_counter()
        first = None
        answer = ''
        usage = {}
        error = None
        try:
            async with asyncio.timeout(65):
                async for item in provider.stream([
                    {'role': 'system', 'content': provider.SYSTEM_PROMPTS[mode]},
                    {'role': 'user', 'content': 'What is 18 divided by 20 as a percentage? Answer in one sentence.'},
                ], 'quick', mode):
                    if item.get('text'):
                        if first is None:
                            first = round(time.perf_counter() - start, 3)
                        answer += item['text']
                    usage = item.get('usage', usage)
        except Exception as exc:
            error = str(exc) or type(exc).__name__
        result = {'mode': mode, 'effort': 'quick', 'first_text_seconds': first,
                  'total_seconds': round(time.perf_counter() - start, 3),
                  'answer': answer, 'usage': usage, 'error': error}
        results.append(result)
        print(json.dumps(result, ensure_ascii=False), flush=True)
    destination = ROOT / 'artifacts' / args.output
    destination.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')

if __name__ == '__main__':
    asyncio.run(main())
