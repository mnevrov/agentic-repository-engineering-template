#!/usr/bin/env python3
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class TemplateContractTests(unittest.TestCase):
    def assert_not_configured(self, target: str) -> None:
        proc = subprocess.run(["make", target], cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(proc.returncode, 2, proc.stdout + proc.stderr)
        self.assertIn("NOT CONFIGURED", proc.stdout + proc.stderr)

    def test_project_check_placeholder_fails_closed(self):
        self.assert_not_configured("check")

    def test_project_test_placeholder_fails_closed(self):
        self.assert_not_configured("test")

    def test_integration_placeholder_fails_closed(self):
        self.assert_not_configured("test-integration")


if __name__ == "__main__":
    unittest.main()
