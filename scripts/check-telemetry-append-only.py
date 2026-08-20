#!/usr/bin/env python3
import argparse
import subprocess
from pathlib import Path

from telemetry_lib import TELEMETRY_PATH, load_jsonl

p = argparse.ArgumentParser(description="Ensure telemetry history is append-only relative to a Git ref.")
p.add_argument("--base-ref", required=True)
args = p.parse_args()

root = Path(__file__).resolve().parents[1]
rel = TELEMETRY_PATH.relative_to(root)

# Validate the current file first.
try:
    load_jsonl()
except ValueError as exc:
    raise SystemExit(str(exc))

proc = subprocess.run(
    ["git", "show", f"{args.base_ref}:{rel.as_posix()}"],
    cwd=root,
    text=True,
    capture_output=True,
)
if proc.returncode == 0:
    old_lines = proc.stdout.splitlines()
else:
    # The telemetry file may legitimately not exist on the base ref yet.
    old_lines = []

new_lines = TELEMETRY_PATH.read_text(encoding="utf-8").splitlines() if TELEMETRY_PATH.exists() else []

if len(new_lines) < len(old_lines):
    raise SystemExit("Telemetry is not append-only: existing rows were removed.")
if new_lines[: len(old_lines)] != old_lines:
    raise SystemExit("Telemetry is not append-only: existing rows were modified or reordered.")

print(f"telemetry append-only: preserved {len(old_lines)} existing row(s), appended {len(new_lines)-len(old_lines)}")
