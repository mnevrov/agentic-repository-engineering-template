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

for index, (old_row, new_row) in enumerate(zip(old_rows, new_rows), 1):
    if old_row == new_row:
        continue
    keys = sorted(
        key
        for key in set(old_row) | set(new_row)
        if old_row.get(key) != new_row.get(key)
    )
    cycle_id = old_row.get("cycle_id") or new_row.get("cycle_id") or "unknown"
    raise SystemExit(
        "Telemetry is not append-only: historical row "
        f"{index} ({cycle_id}) changed fields: {', '.join(keys) or 'unknown'}"
    )

print(
    f"telemetry append-only: preserved {len(old_rows)} existing row(s), "
    f"appended {len(new_rows)-len(old_rows)}"
)
