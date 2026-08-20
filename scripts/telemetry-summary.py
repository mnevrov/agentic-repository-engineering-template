#!/usr/bin/env python3
from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime
from statistics import mean, median

from telemetry_lib import load_jsonl

rows = load_jsonl()
if not rows:
    print("No telemetry yet.")
    raise SystemExit(0)


def ts(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def numeric_values(key):
    return [r[key] for r in rows if isinstance(r.get(key), (int, float)) and not isinstance(r.get(key), bool)]


durations = [(ts(r["ended_at"]) - ts(r["started_at"])).total_seconds() / 60 for r in rows]
results = Counter(r["result"] for r in rows)
models = Counter(r.get("model") or "unknown" for r in rows)

by_task = defaultdict(list)
for row in rows:
    by_task[row["task_id"]].append(row)

completed_tasks = {}
task_lead_minutes = []
for task_id, task_rows in by_task.items():
    ordered = sorted(task_rows, key=lambda r: ts(r["started_at"]))
    first_started = ts(ordered[0]["started_at"])
    passed = [r for r in ordered if r["result"] == "passed"]
    if passed:
        first_pass = min(passed, key=lambda r: ts(r["ended_at"]))
        completed_tasks[task_id] = first_pass
        task_lead_minutes.append((ts(first_pass["ended_at"]) - first_started).total_seconds() / 60)

reworked_tasks = sum(1 for task_rows in by_task.values() if len(task_rows) > 1)
start = min(ts(r["started_at"]) for r in rows)
end = max(ts(r["ended_at"]) for r in rows)
span_weeks = max((end - start).total_seconds() / (7 * 24 * 3600), 1.0)

review_rounds = numeric_values("review_rounds")
input_tokens = numeric_values("input_tokens")
output_tokens = numeric_values("output_tokens")
human_minutes = numeric_values("human_minutes")
tool_seconds = numeric_values("tool_seconds")
test_seconds = numeric_values("test_seconds")
ci_seconds = numeric_values("ci_seconds")
costs = numeric_values("estimated_cost_usd")
pre_release_defects = numeric_values("defects_found_pre_release")
escaped_defects = numeric_values("escaped_defects")

live_rows = [r for r in rows if r.get("live_validation_result") in {"passed", "failed"}]
live_passes = sum(1 for r in live_rows if r["live_validation_result"] == "passed")
parallel_cycles = sum(1 for r in rows if r.get("parallel"))

print(f"cycles: {len(rows)}")
print(f"tasks: {len(by_task)}")
print(f"completed tasks: {len(completed_tasks)}")
print(f"avg cycle minutes: {mean(durations):.1f}")
print(f"median cycle minutes: {median(durations):.1f}")
if task_lead_minutes:
    print(f"avg task lead minutes: {mean(task_lead_minutes):.1f}")
    print(f"median task lead minutes: {median(task_lead_minutes):.1f}")
print(f"throughput completed tasks/week: {len(completed_tasks)/span_weeks:.2f}")
print(f"avg cycles/task: {len(rows)/len(by_task):.2f}")
print(f"rework task rate: {100*reworked_tasks/len(by_task):.1f}%")
print("results: " + ", ".join(f"{k}={v}" for k, v in sorted(results.items())))
print("models: " + ", ".join(f"{k}={v}" for k, v in models.most_common()))
if review_rounds:
    print(f"avg review rounds: {mean(review_rounds):.2f}")
print(f"review P0 total: {sum(numeric_values('review_p0')):.0f}")
print(f"review P1 total: {sum(numeric_values('review_p1')):.0f}")
print(f"parallel cycle share: {100*parallel_cycles/len(rows):.1f}%")
if live_rows:
    print(f"live-validation pass rate: {100*live_passes/len(live_rows):.1f}%")
if input_tokens or output_tokens:
    print(f"tokens: input={sum(input_tokens):.0f}, output={sum(output_tokens):.0f}")
if costs:
    print(f"estimated model cost USD: {sum(costs):.4f}")
if human_minutes:
    print(f"human steering minutes: total={sum(human_minutes):.1f}, avg/cycle={mean(human_minutes):.1f}")
if tool_seconds:
    print(f"tool runtime seconds: {sum(tool_seconds):.1f}")
if test_seconds:
    print(f"test runtime seconds: {sum(test_seconds):.1f}")
if ci_seconds:
    print(f"CI runtime seconds: {sum(ci_seconds):.1f}")

pre = sum(pre_release_defects)
esc = sum(escaped_defects)
if pre_release_defects or escaped_defects:
    print(f"escaped defects: {esc:.0f}")
    if pre + esc > 0:
        print(f"defect escape rate: {100*esc/(pre+esc):.1f}%")
