#!/usr/bin/env python3
import argparse
import json
import uuid
from pathlib import Path

p = argparse.ArgumentParser(description='Append one agentic development cycle to JSONL telemetry.')
p.add_argument('--task', required=True)
p.add_argument('--started', required=True, help='ISO-8601 timestamp')
p.add_argument('--ended', required=True, help='ISO-8601 timestamp')
p.add_argument('--result', required=True, choices=['passed','failed','partial','aborted'])
p.add_argument('--cycle-id')
p.add_argument('--model')
p.add_argument('--provider')
p.add_argument('--agent-role')
p.add_argument('--risk', choices=['A','B','C'])
p.add_argument('--input-tokens', type=int)
p.add_argument('--output-tokens', type=int)
p.add_argument('--tool-seconds', type=float)
p.add_argument('--test-seconds', type=float)
p.add_argument('--review-rounds', type=int)
p.add_argument('--review-p0', type=int)
p.add_argument('--review-p1', type=int)
p.add_argument('--parallel', action='store_true')
p.add_argument('--human-minutes', type=float)
p.add_argument('--evidence')
p.add_argument('--notes')
args = p.parse_args()

row = {
    'cycle_id': args.cycle_id or f'{args.task}-{uuid.uuid4().hex[:8]}',
    'task_id': args.task,
    'started_at': args.started,
    'ended_at': args.ended,
    'model': args.model,
    'provider': args.provider,
    'agent_role': args.agent_role,
    'risk': args.risk,
    'input_tokens': args.input_tokens,
    'output_tokens': args.output_tokens,
    'tool_seconds': args.tool_seconds,
    'test_seconds': args.test_seconds,
    'review_rounds': args.review_rounds,
    'review_p0': args.review_p0,
    'review_p1': args.review_p1,
    'parallel': args.parallel,
    'human_minutes': args.human_minutes,
    'result': args.result,
    'evidence_ref': args.evidence,
    'notes': args.notes,
}

root = Path(__file__).resolve().parents[1]
out = root / '.ai/telemetry/cycles.jsonl'
out.parent.mkdir(parents=True, exist_ok=True)
with out.open('a', encoding='utf-8') as f:
    f.write(json.dumps(row, ensure_ascii=False, separators=(',', ':')) + '\n')
print(out.relative_to(root))
