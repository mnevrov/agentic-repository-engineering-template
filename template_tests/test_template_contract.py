#!/usr/bin/env python3
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAKEFILE = ROOT / "Makefile"

SOURCE_PLACEHOLDERS = {
    "check": "NOT CONFIGURED: replace 'make check' with formatter/linter/type-check commands for your project",
    "test": "NOT CONFIGURED: replace 'make test' with unit-test commands for your project",
    "test-integration": "NOT CONFIGURED: replace 'make test-integration' with integration/e2e commands for your project",
}


class TemplateContractTests(unittest.TestCase):
    def target_recipe(self, target: str) -> str:
        lines = MAKEFILE.read_text(encoding="utf-8").splitlines()
        header = f"{target}:"
        start = None

        for index, line in enumerate(lines):
            if line.strip() == header:
                start = index + 1
                break

        self.assertIsNotNone(start, f"missing Make target: {target}")

        recipe = []
        for line in lines[start:]:
            if line.startswith("\t"):
                recipe.append(line)
                continue
            if not line.strip():
                if recipe:
                    break
                continue
            if recipe:
                break

        self.assertTrue(recipe, f"missing recipe for Make target: {target}")
        return "\n".join(recipe)

    def assert_source_placeholder_fails_closed_if_present(self, target: str) -> None:
        recipe = self.target_recipe(target)
        marker = SOURCE_PLACEHOLDERS[target]

        # The reusable template has exact source placeholders. Downstream
        # projects may use their own fail-closed wording (including the phrase
        # "NOT CONFIGURED") without still being in the template placeholder
        # state, so match the exact source marker instead of a generic phrase.
        if marker not in recipe:
            self.skipTest(f"{target} is configured by downstream project")

        proc = subprocess.run(["make", target], cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(proc.returncode, 2, proc.stdout + proc.stderr)
        self.assertIn(marker, proc.stdout + proc.stderr)

    def test_project_check_placeholder_fails_closed(self):
        self.assert_source_placeholder_fails_closed_if_present("check")

    def test_project_test_placeholder_fails_closed(self):
        self.assert_source_placeholder_fails_closed_if_present("test")

    def test_integration_placeholder_fails_closed(self):
        self.assert_source_placeholder_fails_closed_if_present("test-integration")


if __name__ == "__main__":
    unittest.main()
