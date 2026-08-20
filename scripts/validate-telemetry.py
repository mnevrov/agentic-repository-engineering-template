#!/usr/bin/env python3
from telemetry_lib import TELEMETRY_PATH, load_jsonl

try:
    rows = load_jsonl()
except ValueError as exc:
    raise SystemExit(str(exc))

print(f"telemetry valid: {len(rows)} cycle(s) in {TELEMETRY_PATH}")
