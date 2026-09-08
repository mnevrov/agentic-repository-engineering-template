#!/usr/bin/env python3
import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAKEFILE = ROOT / "Makefile"


class TemplateContractTests(unittest.TestCase):
    def target_recipe(self, target: str) -> str:
        text = MAKEFILE.read_text(encoding="utf-8")
        match = re.search(rf"(?ms)^{re.escape(target)}:\s*\n((?:\t.*(?:\n|$))+)", text)
        self.assertIsNotNone(match, f"missing Make target: {target}")
        return match.group(1)

    def assert_placeholder_fails_closed_if_present(self, target: str) -> None:
        recipe = self.target_recipe(target)
        if "NOT CONFIGURED" not in recipe:
            self.skipTest(f"{target} is configured by downstream project")

        proc = subprocess.run(["make", target], cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(proc.returncode, 2, proc.stdout + proc.stderr)
        self.assertIn("NOT CONFIGURED", proc.stdout + proc.stderr)

    def test_project_check_placeholder_fails_closed(self):
        self.assert_placeholder_fails_closed_if_present("check")

    def test_project_test_placeholder_fails_closed(self):
        self.assert_placeholder_fails_closed_if_present("test")

    def test_integration_placeholder_fails_closed(self):
        self.assert_placeholder_fails_closed_if_present("test-integration")


if __name__ == "__main__":
    unittest.main()
