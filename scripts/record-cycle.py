#!/usr/bin/env python3
import argparse
import json
import subprocess
import uuid
from datetime import datetime

from telemetry_lib import ROOT, TELEMETRY_PATH, load_schema, validate_row


def run_git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=ROOT, text=True, capture_output=True)


def parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def automatic_evidence(started: str, ended: str) -> dict[str, object]:
    try:
        duration = max(0.0, (parse_time(ended) - parse_time(started)).total_seconds())
    except (ValueError, TypeError):
        duration = None

    head = run_git("rev-parse", "HEAD")
    status = run_git("status", "--porcelain")
    tracked = run_git("diff", "--name-only", "HEAD")
    untracked = run_git("ls-files", "--others", "--exclude-standard")
    numstat = run_git("diff", "--numstat", "HEAD")

    changed_files = None
    git_dirty = None
    if status.returncode == 0:
        git_dirty = bool(status.stdout.strip())
    if tracked.returncode == 0 and untracked.returncode == 0:
        changed_files = sorted(set(tracked.stdout.splitlines()) | set(untracked.stdout.splitlines()))

    diff_lines = None
    if numstat.returncode == 0:
        total = 0
        for line in numstat.stdout.splitlines():
            parts = line.split("\t", 2)
            if len(parts) >= 2 and parts[0].isdigit() and parts[1].isdigit():
                total += int(parts[0]) + int(parts[1])
        diff_lines = total

    return {
        "duration_seconds": duration,
        "git_head": head.stdout.strip() if head.returncode == 0 else None,
        "git_dirty": git_dirty,
        "changed_files": changed_files,
        "diff_lines": diff_lines,
    }


p = argparse.ArgumentParser(description="Append one agentic development cycle to JSONL telemetry.")
p.add_argument("--task", required=True)
p.add_argument("--started", required=True, help="ISO-8601 timestamp")
p.add_argument("--ended", required=True, help="ISO-8601 timestamp")
p.add_argument("--result", required=True, choices=["passed", "failed", "partial", "aborted"])
p.add_argument("--cycle-id")
p.add_argument("--model")
p.add_argument("--provider")
p.add_argument("--agent-role")
p.add_argument("--risk", choices=["A", "B", "C"])
p.add_argument("--input-tokens", type=int)
p.add_argument("--output-tokens", type=int)
p.add_argument("--tool-seconds", type=float)
p.add_argument("--test-seconds", type=float)
p.add_argument("--ci-seconds", type=float)
p.add_argument("--review-rounds", type=int)
p.add_argument("--review-p0", type=int)
p.add_argument("--review-p1", type=int)
p.add_argument("--parallel", action="store_true")
p.add_argument("--human-minutes", type=float)
p.add_argument("--estimated-cost-usd", type=float)
p.add_argument("--live-validation-result", choices=["passed", "failed", "skipped", "not_applicable"])
p.add_argument("--defects-found-pre-release", type=int)
p.add_argument("--escaped-defects", type=int)
p.add_argument("--evidence")
p.add_argument("--notes")
args = p.parse_args()

row = {
    "cycle_id": args.cycle_id or f"{args.task}-{uuid.uuid4().hex[:8]}",
    "task_id": args.task,
    "started_at": args.started,
    "ended_at": args.ended,
    "model": args.model,
    "provider": args.provider,
    "agent_role": args.agent_role,
    "risk": args.risk,
    "input_tokens": args.input_tokens,
    "output_tokens": args.output_tokens,
    "tool_seconds": args.tool_seconds,
    "test_seconds": args.test_seconds,
    "ci_seconds": args.ci_seconds,
    "review_rounds": args.review_rounds,
    "review_p0": args.review_p0,
    "review_p1": args.review_p1,
    "parallel": args.parallel,
    "human_minutes": args.human_minutes,
    "estimated_cost_usd": args.estimated_cost_usd,
    "live_validation_result": args.live_validation_result,
    "defects_found_pre_release": args.defects_found_pre_release,
    "escaped_defects": args.escaped_defects,
    "result": args.result,
    "evidence_ref": args.evidence,
    "notes": args.notes,
    **automatic_evidence(args.started, args.ended),
}

errors = validate_row(row, load_schema())
if errors:
    raise SystemExit("Telemetry validation failed:\n- " + "\n- ".join(errors))

TELEMETRY_PATH.parent.mkdir(parents=True, exist_ok=True)
with TELEMETRY_PATH.open("a", encoding="utf-8") as f:
    f.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")

print(TELEMETRY_PATH.relative_to(TELEMETRY_PATH.parents[2]))
