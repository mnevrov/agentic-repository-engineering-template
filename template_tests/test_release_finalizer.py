"""Offline tests for hard release gates; no gh, network, GPG or tag side effects."""
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/finalize_release.py"
spec = importlib.util.spec_from_file_location("template_release_finalizer", SCRIPT)
assert spec is not None and spec.loader is not None
finalizer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(finalizer)

VALID = [
    {"type": "deletion"},
    {"type": "non_fast_forward"},
    {"type": "pull_request", "parameters": {
        "required_approving_review_count": 0}},
    {"type": "required_status_checks", "parameters": {
        "strict_required_status_checks_policy": True,
        "required_status_checks": [
            {"context": "doctor"},
            {"context": "OpenCode v2.1.2 configuration"},
            {"context": "OpenCode v2.2.5 configuration"},
        ]}},
]


class ReleaseSafetyTests(unittest.TestCase):
    def test_required_rules_are_accepted(self):
        finalizer.validate_rules(VALID)

    def test_missing_protection_rule_blocked(self):
        for i in range(len(VALID)):
            with self.subTest(i=i), self.assertRaises(
                finalizer.FinalizationBlocked
            ):
                finalizer.validate_rules(
                    VALID[:i] + VALID[i + 1:]
                )

    def test_missing_required_ci_job_blocked(self):
        v = [dict(x) for x in VALID]
        v[-1] = {
            "type": "required_status_checks",
            "parameters": {
                "strict_required_status_checks_policy": True,
                "required_status_checks": [{"context": "doctor"}],
            },
        }
        with self.assertRaises(finalizer.FinalizationBlocked):
            finalizer.validate_rules(v)

    def test_non_strict_ci_blocked(self):
        v = [dict(x) for x in VALID]
        v[-1] = {
            "type": "required_status_checks",
            "parameters": {
                "strict_required_status_checks_policy": False,
                "required_status_checks": [
                    {"context": x} for x in finalizer.REQUIRED_CHECKS],
            },
        }
        with self.assertRaises(finalizer.FinalizationBlocked):
            finalizer.validate_rules(v)

    def test_documented_main_ruleset_matches_hard_gates(self):
        import json
        path = SCRIPT.parents[1] / "docs/release/MAIN_RULESET.json"
        ruleset = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(ruleset["target"], "branch")
        self.assertEqual(ruleset["enforcement"], "active")
        self.assertEqual(ruleset["conditions"]["ref_name"]["include"],
                         ["refs/heads/main"])
        finalizer.validate_rules(ruleset["rules"])


if __name__ == "__main__":
    unittest.main()
