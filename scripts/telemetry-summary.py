#!/usr/bin/env python3
import json
from collections import Counter
from datetime import datetime
from pathlib import Path

root = Path(__file__).resolve().parents[1]
p = root / '.ai/telemetry/cycles.jsonl'
if not p.exists() or not p.read_text(encoding='utf-8').strip():
    print('No telemetry yet.')
    raise SystemExit(0)

rows=[]
for n,line in enumerate(p.read_text(encoding='utf-8').splitlines(),1):
    try:
        rows.append(json.loads(line))
    except json.JSONDecodeError as e:
        raise SystemExit(f'Invalid JSON on line {n}: {e}')

def ts(s):
    if not s: return None
    return datetime.fromisoformat(s.replace('Z','+00:00'))

durations=[]
for r in rows:
    a,b=ts(r.get('started_at')),ts(r.get('ended_at'))
    if a and b: durations.append((b-a).total_seconds()/60)

results=Counter(r.get('result') for r in rows)
models=Counter(r.get('model') or 'unknown' for r in rows)
reviews=[r.get('review_rounds') for r in rows if isinstance(r.get('review_rounds'), int)]
human=[r.get('human_minutes') for r in rows if isinstance(r.get('human_minutes'), (int,float))]

print(f'cycles: {len(rows)}')
if durations: print(f'avg cycle minutes: {sum(durations)/len(durations):.1f}')
print('results: ' + ', '.join(f'{k}={v}' for k,v in sorted(results.items())))
print('models: ' + ', '.join(f'{k}={v}' for k,v in models.most_common()))
if reviews: print(f'avg review rounds: {sum(reviews)/len(reviews):.2f}')
if human: print(f'avg human minutes: {sum(human)/len(human):.1f}')
