#!/usr/bin/env python3
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"

import sys
sys.path.insert(0, str(SCRIPTS))
from telemetry_lib import load_schema, validate_row


class TelemetryTests(unittest.TestCase):
    def test_valid_row(self):
        row = {
            "cycle_id": "TASK-1-a",
            "task_id": "TASK-1",
            "started_at": "2026-08-20T12:00:00Z",
            "ended_at": "2026-08-20T12:30:00Z",
            "result": "passed",
            "parallel": False,
        }
        self.assertEqual(validate_row(row, load_schema()), [])

    def test_negative_metric_is_rejected(self):
        row = {
            "cycle_id": "TASK-1-a",
            "task_id": "TASK-1",
            "started_at": "2026-08-20T12:00:00Z",
            "ended_at": "2026-08-20T12:30:00Z",
            "result": "passed",
            "tool_seconds": -1,
            "parallel": False,
        }
        errors = validate_row(row, load_schema())
        self.assertTrue(any("tool_seconds" in e for e in errors))

    def test_end_before_start_is_rejected(self):
        row = {
            "cycle_id": "TASK-1-a",
            "task_id": "TASK-1",
            "started_at": "2026-08-20T13:00:00Z",
            "ended_at": "2026-08-20T12:30:00Z",
            "result": "failed",
            "parallel": False,
        }
        errors = validate_row(row, load_schema())
        self.assertIn("ended_at must be >= started_at", errors)


if __name__ == "__main__":
    unittest.main()
