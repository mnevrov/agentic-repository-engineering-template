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

    def test_merge_with_parallel_rows_still_passes(self):
        # Legitimate merge of two branches that each appended rows: the
        # conflict resolution reorders rows (A before B instead of B before
        # A at the intermediate commit), but every historical ledger remains
        # an order-preserving subsequence of the merged ledger. Both gates
        # must pass against the merge base.
        self.initialize()
        boot = self.git("rev-parse", "HEAD").stdout.strip()
        self.git("checkout", "-q", "-b", "feature-a", boot)
        with self.telemetry.open("a") as stream:
            stream.write(row("STEP-A"))
        (self.repo / "src/app.txt").write_text("a\n")
        self.commit("row A")
        self.git("checkout", "-q", "-b", "feature-b", boot)
        with self.telemetry.open("a") as stream:
            stream.write(row("STEP-B"))
        (self.repo / "src/file-b.txt").write_text("b\n")
        self.commit("row B")
        # Merge B into A: cycles.jsonl conflicts; resolve as B-then-A order.
        self.git("checkout", "-q", "feature-a")
        merge = subprocess.run(["git", "merge", "--no-ff", "--no-commit", "feature-b"],
                               cwd=self.repo, capture_output=True, text=True)
        self.assertNotEqual(merge.returncode, 0)  # telemetry conflicted
        boot_ledger = self.git("show", f"{boot}:.ai/telemetry/cycles.jsonl").stdout
        self.telemetry.write_text(boot_ledger + row("STEP-B") + row("STEP-A"))
        self.git("add", ".")
        self.git("commit", "-qm", "merge with reordered resolution")
        # Endpoint append-only vs boot base passes, and history_monotonic
        # accepts the intermediate STEP-B-only ledger as a subsequence.
        ok, message = append.check(self.repo, boot)
        self.assertTrue(ok, message)

    def test_stale_ancestor_cannot_reopen_cutover_after_growth(self):
        # Adversarial-review P0: after a legitimate bootstrap and several real
        # project cycles, presenting the pre-bootstrap template tip as base to
        # delete the project ledger must fail. Intermediate ledgers in
        # base..HEAD are not prefixes of the rewritten ledger.
        self.initialize()
        for index in range(3):
            with self.telemetry.open("a") as stream:
                stream.write(row(f"STEP-{index}"))
            (self.repo / "src/app.txt").write_text(f"step {index}\n")
            self.commit(f"step {index}")
        self.telemetry.write_text(row("PROJECT-BOOTSTRAP"))
        self.commit("attack: delete project telemetry")
        root = self.git("rev-list", "--max-parents=0", "HEAD").stdout.strip()
        self.assertFalse(append.check(self.repo, root)[0])

    def test_symlink_marker_refuses_cutover(self):
        # git show would happily print a symlink's target text; a committed
        # symlink is not a regular marker file.
        (self.repo / "marker-target").write_text(
            "project_name=Pilot\nbootstrap_id=PROJECT-BOOTSTRAP\n")
        (self.repo / ".ai/project-initialized").symlink_to("../marker-target")
        self.telemetry.write_text(row("PROJECT-BOOTSTRAP"))
        self.commit("Symlink marker")
        self.assertFalse(append.check(self.repo, self.base)[0])

    def test_source_template_cannot_delete_template_row_with_prefix_restored(self):
        # Round-3 P0: in the source template's own regime the final ledger
        # keeps TEMPLATE-* rows, so the cutover exemption must NOT apply to
        # intermediate ledgers. A failed cycle added in one commit and
        # deleted in the next — with the base prefix restored byte-exactly —
        # must fail both gates against origin/main, as CI would run them.
        origin_main = self.git("rev-parse", "HEAD").stdout.strip()
        with self.telemetry.open("a") as stream:
            stream.write(row("TEMPLATE-FAILED"))
        (self.repo / "src/a.txt").write_text("a\n")
        self.commit("record failed cycle")
        lines = self.telemetry.read_text().splitlines()
        self.telemetry.write_text("\n".join(
            line for line in lines if "TEMPLATE-FAILED" not in line) + "\n"
            + row("TEMPLATE-NEXT"))
        (self.repo / "src/b.txt").write_text("b\n")
        self.commit("delete failed row, prefix preserved")
        self.assertFalse(append.check(self.repo, origin_main)[0])
        self.assertFalse(required.check(self.repo, origin_main)[0])

    def test_ledger_deleted_midrange_fails_closed(self):
        # Full-ledger deletion at an interior commit, then restore of the
        # base prefix: absent-at-later-commit is a deletion, not an exemption.
        origin_main = self.git("rev-parse", "HEAD").stdout.strip()
        self.telemetry.unlink()
        (self.repo / "src/gone.txt").write_text("gone\n")
        self.commit("ledger deleted")
        restored = self.git("show", f"{origin_main}:.ai/telemetry/cycles.jsonl").stdout
        self.telemetry.write_text(restored + row("TEMPLATE-NEXT"))
        (self.repo / "src/back.txt").write_text("back\n")
        self.commit("ledger restored plus new row")
        self.assertFalse(append.check(self.repo, origin_main)[0])

    def test_directory_marker_refuses_cutover(self):
        # ls-tree -r would report a directory's children as regular blobs and
        # `git show` of a tree prints child names that fake marker content.
        (self.repo / ".ai/project-initialized").mkdir()
        (self.repo / ".ai/project-initialized" / "project_name=").touch()
        (self.repo / ".ai/project-initialized" / "bootstrap_id=").touch()
        self.telemetry.write_text(row("PROJECT-BOOTSTRAP"))
        self.commit("Directory marker")
        self.check(False, False)

    def test_evil_merge_cannot_drop_committed_row(self):
        # Round-2 P0: git rev-list <range> -- path applies default history
        # simplification and prunes merge commits whose tree equals a
        # parent's. An '-s ours' merge must not hide a side branch that
        # appended (and here: honestly recorded a failed) ledger row.
        self.initialize()
        boot = self.git("rev-parse", "HEAD").stdout.strip()
        self.git("checkout", "-q", "-b", "side", boot)
        with self.telemetry.open("a") as stream:
            stream.write(row("STEP-FAILED"))
        (self.repo / "src/risky.txt").write_text("risky\n")
        self.commit("side: risky change + failed cycle")
        self.git("checkout", "-q", "-b", "mainline", boot)
        self.git("merge", "-q", "--no-commit", "-s", "ours", "side")
        self.git("commit", "-qm", "evil merge silently drops the failed row")
        with self.telemetry.open("a") as stream:
            stream.write(row("STEP-NEXT"))
        (self.repo / "src/feature.txt").write_text("feature\n")
        self.commit("later normal cycle")
        self.assertFalse(append.check(self.repo, boot)[0])
        self.assertFalse(required.check(self.repo, boot)[0])

    def test_worktree_ledger_diverged_from_head_fails_closed(self):
        # Gates evaluate the committed HEAD ledger; an uncommitted local
        # rewrite must never produce a green local verdict.
        self.initialize()
        product_base = self.git("rev-parse", "HEAD").stdout.strip()
        with self.telemetry.open("a") as stream:
            stream.write(row("FOLLOWUP-1"))
        (self.repo / "src/app.txt").write_text("change\n")
        self.commit("cycle recorded")
        # Uncommitted row deletion in the worktree only.
        original = self.telemetry.read_text()
        self.telemetry.write_text(row("PROJECT-BOOTSTRAP"))
        ok_a, msg_a = append.check(self.repo, product_base)
        ok_r, msg_r = required.check(self.repo, product_base)
        self.assertFalse(ok_a, msg_a)
        self.assertFalse(ok_r, msg_r)
        self.assertIn("worktree", msg_a)
        self.telemetry.write_text(original)
        self.assertTrue(append.check(self.repo, product_base)[0])

    def test_url_insteadof_origin_refuses_cutover(self):
        # url.<base>.insteadOf can silently retarget origin to another repo;
        # while configured for this origin URL, identity is unverifiable.
        self.git("config", "url.https://github.com/mnevrov/"
                 "agentic-repository-engineering-template.git.insteadOf",
                 self.DOWNSTREAM_ORIGIN)
        self.initialize()
        self.check(False, False)

    def test_mirror_named_repository_refuses_cutover(self):
        # An internal mirror keeping the template repository name must not
        # cut its inherited ledger over.
        self.git("remote", "set-url", "origin",
                 "git@gitlab.t8.ru:sensor/other/agentic-repository-engineering-template.git")
        self.initialize()
        self.check(False, False)

    def test_shallow_clone_refuses_cutover(self):
        # A shallow boundary masquerades as a root commit; identity/lineage
        # cannot be verified in a shallow clone.
        clone = self.repo / "shallow-clone"
        subprocess.run(["git", "clone", "-q", str(self.repo), str(clone)],
                       check=True, capture_output=True, text=True)
        # Simulate a shallow boundary deterministically: git reports
        # shallow purely from a non-empty .git/shallow.
        head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=clone,
                              check=True, capture_output=True, text=True).stdout
        (clone / ".git" / "shallow").write_text(head, encoding="utf-8")
        subprocess.run(["git", "remote", "set-url", "origin",
                        self.DOWNSTREAM_ORIGIN], cwd=clone, check=True)
        self.assertTrue(cutover._is_shallow(clone))
        self.assertFalse(cutover.bootstrap_cutover(
            clone, "HEAD^",
            [row("TEMPLATE-1"), row("TEMPLATE-2")], [row("PROJECT-BOOTSTRAP")]))

    def test_dash_base_ref_refuses_cutover(self):
        # argparse's `--base-ref=--all` form would otherwise reach git diff
        # as a flag and silently report 'no substantive change'.
        self.initialize()
        for unsafe in ("--all", "--exit-code", "-x", ""):
            self.assertFalse(append.check(self.repo, unsafe)[0])
            self.assertFalse(required.check(self.repo, unsafe)[0])

    def test_replace_refs_refuse_cutover(self):
        # git replace grafts can fabricate a template-signature root locally;
        # any refs/replace object makes lineage unverifiable.
        self.initialize()
        root = self.git("rev-list", "--max-parents=0", "HEAD").stdout.strip()
        grafted = self.git("commit-tree", f"{root}^{{tree}}", "-m", "fake root").stdout.strip()
        self.git("replace", root, grafted)
        try:
            self.check(False, False)
        finally:
            self.git("replace", "-d", root)

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


    def build_pre_ledger_repo(self):
        """Downstream-shaped repo whose ROOT COMMIT has no ledger at all —
        the exact shape the template's own first commits started from."""
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        repo = Path(temp.name)

        def git(*args):
            return subprocess.run(["git", *args], cwd=repo, check=True,
                                  capture_output=True, text=True)
        git("init", "-q")
        git("config", "user.email", "ci@example.invalid")
        git("config", "user.name", "CI")
        (repo / "src").mkdir()
        (repo / "src" / "app.txt").write_text("hello\n")
        git("add", ".")
        git("commit", "-qm", "root without ledger")
        root = git("rev-parse", "HEAD").stdout.strip()
        git("remote", "add", "origin", self.DOWNSTREAM_ORIGIN)
        return repo, git, root

    def test_pre_ledger_base_cannot_wipe_inherited_template_rows(self):
        # Round-4 F1: base an ancestor from BEFORE the ledger existed and the
        # shape-only exemption would license wiping TEMPLATE-* rows committed
        # inside the range. The exemption requires a verified cutover, and no
        # verified cutover exists for a lineageless ledger introduction.
        repo, git, root = self.build_pre_ledger_repo()
        ledger = repo / ".ai" / "telemetry" / "cycles.jsonl"
        ledger.parent.mkdir(parents=True)
        ledger.write_text(row("TEMPLATE-1") + row("TEMPLATE-2") + row("TEMPLATE-3"))
        git("add", ".")
        git("commit", "-qm", "template rows")
        (repo / ".ai" / "project-initialized").write_text(
            "project_name=Pilot\nbootstrap_id=PROJECT-BOOTSTRAP\n")
        ledger.write_text(row("PROJECT-BOOTSTRAP"))
        (repo / "src" / "app.txt").write_text("wiped\n")
        git("add", ".")
        git("commit", "-qm", "wipe ledger to a fabricated project row")
        self.assertFalse(append.check(repo, root)[0])
        self.assertFalse(required.check(repo, root)[0])

    def test_pre_ledger_root_honest_project_ledger_still_passes(self):
        # The no-over-refusal side: a ledger introduced at no-template-rows
        # root and grown with genuine PROJECT rows against that root passes
        # the ordinary append-only rules without any exemption.
        repo, git, root = self.build_pre_ledger_repo()
        ledger = repo / ".ai" / "telemetry" / "cycles.jsonl"
        ledger.parent.mkdir(parents=True)
        ledger.write_text(row("PROJECT-1"))
        (repo / "src" / "app.txt").write_text("first project change\n")
        git("add", ".")
        git("commit", "-qm", "first project commit")
        self.assertTrue(append.check(repo, root)[0])
        self.assertTrue(required.check(repo, root)[0])

    def test_multiple_origin_urls_refuse_identity(self):
        # remote.origin.url is multi-valued: transport uses the FIRST value
        # while `git config --get` reports the LAST, so no single value can be
        # trusted as the provenance identity. Ambiguity fails closed.
        self.git("remote", "set-url", "origin",
                 "https://github.com/example/other-project.git")
        self.git("config", "--add", "remote.origin.url", self.DOWNSTREAM_ORIGIN)
        self.assertIsNone(cutover.trusted_repository_identity(self.repo))
        self.initialize()
        self.check(False, False)

    def test_identity_preserving_insteadof_alias_allows_cutover(self):
        # A personal `url.git@github.com:.insteadOf https://github.com/`
        # alias (typically global, invisible to repo-local config scans)
        # rewrites the fetch URL but preserves host/owner/repo; asking Git
        # itself for the effective target keeps the provenance verdict
        # identical, so first-bootstrap over-refusal must not happen.
        self.git("config", "url.git@github.com:.insteadOf", "https://github.com/")
        self.initialize()
        self.check(True, True)

    def test_identity_changing_insteadof_refuses_cutover(self):
        # An alias that retargets host or owner masks the real fetch target:
        # the effective identity differs from the raw one and is unverifiable.
        self.git("config", "url.https://mirror.example/retarget/.insteadOf",
                 "https://github.com/example/")
        self.initialize()
        self.check(False, False)

    def test_grafts_file_refuses_cutover(self):
        # A legacy .git/info/grafts file signals fabricated lineage. Even
        # where modern git ignores its content, lineage integrity cannot be
        # asserted while it exists, and history scans must not run over a
        # repository whose owner intended to rewrite it.
        self.initialize()
        grafts = self.repo / ".git" / "info" / "grafts"
        grafts.parent.mkdir(exist_ok=True)
        grafts.write_text(self.base + "\n", encoding="utf-8")
        try:
            self.check(False, False)
        finally:
            grafts.unlink()

    def test_directory_ledger_path_fails_closed(self):
        # A tree at the ledger path would make `git show` print a child
        # listing (which passed JSON parsing would then see as rows); the
        # gates must report an explicit structural error, not rows and not
        # an unhandled traceback.
        self.telemetry.unlink()
        self.telemetry.mkdir()
        (self.telemetry / "inner.txt").write_text("nope\n")
        self.commit("directory at ledger path")
        ok_append, message_append = append.check(self.repo, self.base)
        ok_required, message_required = required.check(self.repo, self.base)
        self.assertFalse(ok_append)
        self.assertFalse(ok_required)
        self.assertIn("not a regular file", message_append)
        self.assertIn("not a regular file", message_required)


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

    def test_dot_segment_aliasing_yields_none(self):
        # Confirmed adversarial aliases: git/HTTP resolve these to the real
        # repository, so they must not be normalized to a usable identity.
        for url in (
            "https://github.com/other/x/../pilot.git",
        ):
            with self.subTest(url=url):
                self.assertIsNone(self.parse(url))

    def test_port_and_trailing_dot_host_forms(self):
        # Scheme-form ports, trailing-dot hosts and `/.` path aliases are
        # genuine aliases of the same hosted repository: normalize them so
        # source detection sees them, and reject `..` traversal outright.
        self.assertEqual(self.parse("ssh://git@github.com:443/mnevrov/pilot.git"),
                         "github.com/mnevrov/pilot")
        self.assertEqual(self.parse("https://github.com./mnevrov/pilot"),
                         "github.com/mnevrov/pilot")
        self.assertEqual(self.parse("https://github.com/mnevrov/pilot.git/."),
                         "github.com/mnevrov/pilot")
        self.assertTrue(cutover.source_identity_matches(
            self.parse("https://github.com./mnevrov/"
                       "agentic-repository-engineering-template.git/.")))

    def test_source_identity_matches_only_exact_repository(self):
        self.assertTrue(cutover.source_identity_matches(
            "github.com/mnevrov/agentic-repository-engineering-template"))
        # Equal-named mirrors must not cut their inherited ledger over.
        self.assertTrue(cutover.source_identity_matches(
            "gitlab.t8.ru/sensor/other/agentic-repository-engineering-template"))
        self.assertFalse(cutover.source_identity_matches(
            "github.com/mnevrov/agentic-repository-engineering-template-demo"))
        self.assertFalse(cutover.source_identity_matches(
            "github.com/mnevrov/pilot"))
        self.assertFalse(cutover.source_identity_matches(None))

    def test_percent_encoded_paths_are_decoded_once(self):
        # Round-2 P1: servers fetch the decoded path, so aliases must be
        # normalized to the same identity the deny list sees.
        self.assertEqual(
            self.parse("https://github.com/mnevrov/%61gentic-repository-engineering-template"),
            "github.com/mnevrov/agentic-repository-engineering-template")
        self.assertTrue(cutover.source_identity_matches(self.parse(
            "git@gitlab.t8.ru:sensor/%61gentic-repository-engineering-template.git")))
        # Decoding happens once: double-encoded %2561 stays literal and is a
        # different path, not the source.
        self.assertNotEqual(self.parse(
            "https://github.com/mnevrov/%2561gentic-repository-engineering-template"),
            "github.com/mnevrov/agentic-repository-engineering-template")

    def test_uppercase_percent_escape_identity_aliases(self):
        # %41 decodes to 'A' AFTER lowercasing would have run; decoding must
        # precede case folding or this aliases past the source deny.
        identity = self.parse(
            "https://github.com/mnevrov/%41gentic-repository-engineering-template")
        self.assertEqual(identity,
                         "github.com/mnevrov/agentic-repository-engineering-template")
        self.assertTrue(cutover.source_identity_matches(identity))
        self.assertTrue(cutover.source_url_matches(
            "https://github.com/mnevrov/%41GENTIC-REPOSITORY-ENGINEERING-TEMPLATE"))
        self.assertTrue(cutover.source_identity_matches(self.parse(
            "https://github.com/mnevrov/agentic-repository-engineering-templat%45")))
        self.assertTrue(cutover.source_identity_matches(self.parse(
            "https://%67ithub.com/mnevrov/agentic-repository-engineering-template")))
        # Legitimate downstream names are untouched by the deny logic.
        self.assertFalse(cutover.source_identity_matches(
            self.parse("https://github.com/example/pilot.git")))

    def test_source_url_matches_covers_local_paths_and_mirrors(self):
        self.assertTrue(cutover.source_url_matches(
            "/home/dev/clones/agentic-repository-engineering-template"))
        self.assertTrue(cutover.source_url_matches(
            "https://gitlab.t8.ru/sensor/other/agentic-repository-engineering-template.git"))
        # Round-2 P2: `git clone /path/repo/.git` clones the full history too.
        self.assertTrue(cutover.source_url_matches(
            "/srv/mirrors/agentic-repository-engineering-template/.git"))
        self.assertTrue(cutover.source_url_matches(
            "https://github.com/mnevrov/%61gentic-repository-engineering-template"))
        self.assertFalse(cutover.source_url_matches("/home/dev/pilot"))
        self.assertFalse(cutover.source_url_matches(""))
        self.assertFalse(cutover.source_url_matches(".git"))


if __name__ == "__main__":
    unittest.main()
