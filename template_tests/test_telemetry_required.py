#!/usr/bin/env python3
import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check-telemetry-required.py"
spec = importlib.util.spec_from_file_location("telemetry_required", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


class TelemetryRequiredTests(unittest.TestCase):
    def init_repo(self) -> Path:
        root = Path(tempfile.mkdtemp())
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=root, check=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=root, check=True)
        (root / "src").mkdir()
        (root / "src/app.txt").write_text("v1\n")
        subprocess.run(["git", "add", "."], cwd=root, check=True)
        subprocess.run(["git", "commit", "-qm", "base"], cwd=root, check=True)
        return root

    def test_substantive_change_requires_new_row(self):
        repo = self.init_repo()
        base = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()
        (repo / "src/app.txt").write_text("v2\n")
        subprocess.run(["git", "add", "."], cwd=repo, check=True)
        subprocess.run(["git", "commit", "-qm", "change"], cwd=repo, check=True)
        ok, message = module.check(repo, base)
        self.assertFalse(ok)
        self.assertIn("without appended telemetry", message)

    def test_appended_row_satisfies_requirement(self):
        repo = self.init_repo()
        base = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()
        (repo / "src/app.txt").write_text("v2\n")
        telemetry = repo / ".ai/telemetry/cycles.jsonl"
        telemetry.parent.mkdir(parents=True)
        telemetry.write_text('{"cycle_id":"x"}\n')
        subprocess.run(["git", "add", "."], cwd=repo, check=True)
        subprocess.run(["git", "commit", "-qm", "change"], cwd=repo, check=True)
        ok, message = module.check(repo, base)
        self.assertTrue(ok)
        self.assertIn("1 row(s) appended", message)

    def test_telemetry_only_change_does_not_require_another_row(self):
        repo = self.init_repo()
        base = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()
        telemetry = repo / ".ai/telemetry/cycles.jsonl"
        telemetry.parent.mkdir(parents=True)
        telemetry.write_text('{"cycle_id":"x"}\n')
        subprocess.run(["git", "add", "."], cwd=repo, check=True)
        subprocess.run(["git", "commit", "-qm", "telemetry"], cwd=repo, check=True)
        ok, message = module.check(repo, base)
        self.assertTrue(ok)
        self.assertIn("no substantive change", message)


if __name__ == "__main__":
    unittest.main()
