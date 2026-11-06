#!/usr/bin/env python3
from collections import Counter

from telemetry_lib import TELEMETRY_PATH, load_jsonl

try:
    rows = load_jsonl()
except ValueError as exc:
    raise SystemExit(str(exc))

duplicates = sorted(
    cycle_id for cycle_id, count in Counter(
        row.get("cycle_id") for row in rows
    ).items() if count > 1
)
if duplicates:
    raise SystemExit(
        "telemetry invalid: duplicate cycle_id(s): " + ", ".join(duplicates)
    )

print(f"telemetry valid: {len(rows)} cycle(s) in {TELEMETRY_PATH}")
