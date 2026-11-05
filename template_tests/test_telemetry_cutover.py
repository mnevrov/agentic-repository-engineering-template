#!/usr/bin/env python3
"""Git-backed regressions for template-to-project telemetry cutover."""
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


def load_script(filename, name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / filename)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


append = load_script("check-telemetry-append-only.py", "telemetry_append")
required = load_script("check-telemetry-required.py", "telemetry_required_cutover")


def row(task):
    return json.dumps({
        "cycle_id": f"{task}-test",
        "task_id": task,
        "started_at": "2026-11-05T12:00:00Z",
        "ended_at": "2026-11-05T12:01:00Z",
        "result": "passed"
    }) + "\n"


class TelemetryCutoverTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.repo = Path(temp.name)
        self.git("init", "-q")
        self.git("config", "user.email", "ci@example.invalid")
        self.git("config", "user.name", "CI")
        (self.repo / ".ai/telemetry").mkdir(parents=True)
        (self.repo / "src").mkdir()
        (self.repo / "src/app.txt").write_text("before\n")
        self.telemetry = self.repo / ".ai/telemetry/cycles.jsonl"
        self.telemetry.write_text(row("TEMPLATE-1") + row("TEMPLATE-2"))
        self.commit("Source template")
        self.base = self.git("rev-parse", "HEAD").stdout.strip()

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.repo, check=True,
                              capture_output=True, text=True)

    def commit(self, message):
        self.git("add", ".")
        self.git("commit", "-qm", message)

    def initialize(self, *, contents=None, marker=True):
        if marker:
            (self.repo / ".ai/project-initialized").write_text(
                "project_name=Pilot\nbootstrap_id=PROJECT-BOOTSTRAP\n")
        (self.repo / "src/app.txt").write_text("project\n")
        self.telemetry.write_text(row("PROJECT-BOOTSTRAP") if contents is None else contents)
        self.commit("Bootstrap project")

    def check(self, expected_append, expected_required, base=None):
        ref = base or self.base
        a = append.check(self.repo, ref)
        b = required.check(self.repo, ref)
        self.assertEqual(a[0], expected_append, a)
        self.assertEqual(b[0], expected_required, b)

    def test_first_project_commit_resets_only_template_history(self):
        self.initialize()
        self.check(True, True)
        self.assertIn("bootstrap cutover", append.check(self.repo, self.base)[1])

    def test_cutover_without_product_cycle_still_fails_required(self):
        self.initialize(contents="")
        self.check(True, False)

    def test_unmarked_deletion_fails(self):
        self.initialize(marker=False)
        self.check(False, False)

    def test_mixed_baseline_cannot_cut_over(self):
        self.telemetry.write_text(row("TEMPLATE-1") + row("PROJECT-OLD"))
        self.commit("Mixed history")
        mixed_base = self.git("rev-parse", "HEAD").stdout.strip()
        self.initialize()
        self.check(False, False, mixed_base)

    def test_later_rewrite_fails_even_with_initializer_marker(self):
        self.initialize()
        product_base = self.git("rev-parse", "HEAD").stdout.strip()
        self.telemetry.write_text(row("PROJECT-NEW"))
        (self.repo / "src/app.txt").write_text("new change\n")
        self.commit("Attempt rewrite")
        self.check(False, False, product_base)

    def test_legitimate_subsequent_append_passes(self):
        self.initialize()
        product_base = self.git("rev-parse", "HEAD").stdout.strip()
        with self.telemetry.open("a") as stream:
            stream.write(row("FOLLOWUP-1"))
        (self.repo / "src/app.txt").write_text("new change\n")
        self.commit("Follow up")
        self.check(True, True, product_base)

    def test_source_rows_never_valid_in_new_ledger(self):
        self.initialize(contents=row("TEMPLATE-3"))
        self.check(False, False)

    def test_invalid_base_ref_rejected(self):
        self.initialize()
        self.assertFalse(append.check(self.repo, "missing-ref")[0])
        with self.assertRaises(ValueError):
            required.check(self.repo, "missing-ref")

    def test_bare_marker_does_not_unlock_reset(self):
        self.initialize()
        (self.repo / ".ai/project-initialized").write_text("arbitrary\n")
        self.check(False, False)


if __name__ == "__main__":
    unittest.main()
