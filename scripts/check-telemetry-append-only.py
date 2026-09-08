#!/usr/bin/env python3
import argparse
import json
import subprocess
from pathlib import Path

from telemetry_lib import TELEMETRY_PATH, load_jsonl

p = argparse.ArgumentParser(description="Ensure telemetry history is append-only relative to a Git ref.")
p.add_argument("--base-ref", required=True)
args = p.parse_args()

root = Path(__file__).resolve().parents[1]
rel = TELEMETRY_PATH.relative_to(root)

# Validate and parse the current file first.
try:
    new_rows = load_jsonl()
except ValueError as exc:
    raise SystemExit(str(exc))

proc = subprocess.run(
    ["git", "show", f"{args.base_ref}:{rel.as_posix()}"],
    cwd=root,
    text=True,
    capture_output=True,
)

old_rows = []
if proc.returncode == 0:
    for line_no, line in enumerate(proc.stdout.splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise SystemExit(
                f"Base telemetry is invalid JSON on line {line_no}: {exc}"
            ) from exc
        if not isinstance(row, dict):
            raise SystemExit(f"Base telemetry line {line_no} must be a JSON object")
        old_rows.append(row)

if len(new_rows) < len(old_rows):
    raise SystemExit("Telemetry is not append-only: existing rows were removed.")

# Compare row content, not incidental JSON formatting. Changing any historical
# value or row order still fails; whitespace/key-order normalization does not.
if new_rows[: len(old_rows)] != old_rows:
    raise SystemExit("Telemetry is not append-only: existing rows were modified or reordered.")

print(
    f"telemetry append-only: preserved {len(old_rows)} existing row(s), "
    f"appended {len(new_rows)-len(old_rows)}"
)
