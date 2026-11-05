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


cutover = load_script("telemetry_cutover.py", "telemetry_cutover")
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
    """Cutover is bound to provenance: hosted identity, lineage and
    source-only baseline. Every unverifiable condition fails closed."""

    DOWNSTREAM_ORIGIN = "https://github.com/example/pilot-project.git"

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
        self.set_origin(self.DOWNSTREAM_ORIGIN)

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.repo, check=True,
                              capture_output=True, text=True)

    def set_origin(self, url):
        self.git("remote", "add", "origin", url)

    def commit(self, message):
        self.git("add", ".")
        self.git("commit", "-qm", message)

    def initialize(self, *, contents=None, marker=True, marker_text=None):
        if marker or marker_text is not None:
            (self.repo / ".ai/project-initialized").write_text(
                marker_text if marker_text is not None
                else "project_name=Pilot\nbootstrap_id=PROJECT-BOOTSTRAP\n")
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
        # The invalid content is committed, so even the HEAD blob cannot
        # vouch for project identity.
        self.initialize(marker_text="arbitrary\n")
        self.check(False, False)

    # ---- provenance negatives (derived from the independent release audit) ----

    def test_poc_rogue_cutover_on_local_clone_is_refused(self):
        # Audit PoC: clone of the template (origin = local path), fake marker,
        # 38-row TEMPLATE-* ledger replaced by one fabricated row. Without a
        # verifiable hosted identity the exception must stay locked.
        self.git("remote", "set-url", "origin", "/srv/scratch/template-clone")
        self.initialize()
        self.check(False, False)

    def test_missing_origin_refuses_cutover(self):
        self.git("remote", "remove", "origin")
        self.initialize()
        self.check(False, False)

    def test_file_url_origin_refuses_cutover(self):
        self.git("remote", "set-url", "origin", "file:///srv/scratch/clone")
        self.initialize()
        self.check(False, False)

    def test_source_repository_origin_refuses_cutover(self):
        # A rogue branch of the source template itself (or its CI checkout):
        # origin identity is the source, so the exception is permanently off.
        self.initialize()
        for url in (
            "https://github.com/mnevrov/agentic-repository-engineering-template.git",
            "git@github.com:mnevrov/agentic-repository-engineering-template.git",
        ):
            with self.subTest(url=url):
                self.git("remote", "set-url", "origin", url)
                self.check(False, False)

    def test_untracked_marker_refuses_cutover(self):
        # Marker only in the worktree, never committed at HEAD.
        (self.repo / ".ai/project-initialized").write_text(
            "project_name=Rogue\nbootstrap_id=PROJECT-BOOTSTRAP\n")
        (self.repo / "src/app.txt").write_text("project\n")
        self.telemetry.write_text(row("PROJECT-BOOTSTRAP"))
        self.git("add", "src", ".ai/telemetry")
        self.git("commit", "-qm", "Rogue bootstrap without marker")
        self.check(False, False)

    def test_worktree_marker_cannot_unlock_cutover(self):
        # HEAD blob is the authority: an uncommitted worktree marker never
        # counts, and once the marker path exists in a commit it permanently
        # blocks cutover for that base ref even if the content was invalid.
        (self.repo / ".ai/project-initialized").write_text("placeholder\n")
        self.commit("Placeholder marker")
        placeholder = self.git("rev-parse", "HEAD").stdout.strip()
        (self.repo / ".ai/project-initialized").write_text(
            "project_name=Rogue\nbootstrap_id=PROJECT-BOOTSTRAP\n")
        self.telemetry.write_text(row("PROJECT-BOOTSTRAP"))
        # Worktree marker is valid but HEAD blob is still 'placeholder'.
        self.assertFalse(append.check(self.repo, self.base)[0])
        self.commit("Late valid marker")
        # Base ref now contains the marker path: fail closed regardless of
        # committed content.
        self.assertFalse(append.check(self.repo, placeholder)[0])

    def test_disjoint_history_refuses_cutover(self):
        # Unrelated grafted history in HEAD's ancestry hides the real root:
        # lineage is not verifiable, so the exception stays locked.
        self.git("checkout", "-q", "--orphan", "unrelated")
        # The orphan worktree still contains the template files; commit them
        # as a second root and merge it with --allow-unrelated-histories.
        self.git("add", ".")
        self.git("commit", "-qm", "Second root")
        self.git("checkout", "-q", self.base)
        self.git("merge", "-q", "--allow-unrelated-histories", "-m", "graft", "unrelated")
        self.initialize()
        self.check(False, False)

    def test_non_ancestor_base_ref_refuses_cutover(self):
        self.initialize()
        bootstrap = self.git("rev-parse", "HEAD").stdout.strip()
        # A side branch from the template base: its own ledger rewrite against
        # its own base would pass shape checks, but compared against a base
        # that is not its ancestor the exception must not apply.
        self.git("checkout", "-q", "-b", "side", self.base)
        (self.repo / ".ai/project-initialized").write_text(
            "project_name=Side\nbootstrap_id=PROJECT-BOOTSTRAP\n")
        self.telemetry.write_text(row("PROJECT-BOOTSTRAP"))
        self.commit("Side bootstrap")
        self.assertFalse(cutover.bootstrap_cutover(
            self.repo, bootstrap,
            [row("TEMPLATE-1"), row("TEMPLATE-2")], [row("PROJECT-BOOTSTRAP")]))
        self.git("checkout", "-q", "-")


class RepositoryIdentityTests(unittest.TestCase):
    def parse(self, url):
        return cutover.repository_identity(url)

    def test_https_and_ssh_forms_normalize(self):
        expected = "github.com/mnevrov/pilot"
        for url in (
            "https://github.com/mnevrov/pilot.git",
            "HTTPS://GitHub.com/Mnevrov/Pilot",
            "git@github.com:mnevrov/pilot.git",
            "ssh://git@github.com/mnevrov/pilot",
        ):
            with self.subTest(url=url):
                self.assertEqual(self.parse(url), expected)

    def test_untrusted_forms_yield_none(self):
        for url in (
            "",
            "/home/dev/pilot",
            "./pilot",
            "file:///srv/pilot",
            "https://gitserver/pilot",          # no dot in host
            "https://gitserver.example/pilot",  # single path segment
            "../evil",
        ):
            with self.subTest(url=url):
                self.assertIsNone(self.parse(url))

    def test_source_identity_matches_only_exact_repository(self):
        self.assertTrue(cutover.source_identity_matches(
            "github.com/mnevrov/agentic-repository-engineering-template"))
        self.assertFalse(cutover.source_identity_matches(
            "github.com/mnevrov/agentic-repository-engineering-template-demo"))
        self.assertFalse(cutover.source_identity_matches(
            "gitlab.t8.ru/sensor/other/agentic-repository-engineering-template"))
        self.assertFalse(cutover.source_identity_matches(None))


if __name__ == "__main__":
    unittest.main()
