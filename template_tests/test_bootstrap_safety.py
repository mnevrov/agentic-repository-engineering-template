#!/usr/bin/env python3
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INIT = ROOT / "scripts" / "init-project"


class BootstrapSafetyTests(unittest.TestCase):
    def fixture(self, root: Path) -> None:
        for path in ("AGENTS.md", "Makefile", "docs/tasks/TEMPLATE-1.md", ".ai/telemetry/cycles.jsonl"):
            target = root / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("source-history", encoding="utf-8")

    def run_init(self, root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(["python3", str(INIT), "Project", "--root", str(root)],
                              text=True, capture_output=True)

    def test_rejects_symlink_managed_directory_without_mutation(self):
        with tempfile.TemporaryDirectory() as home:
            root = Path(home) / "project"
            root.mkdir()
            self.fixture(root)
            outside = Path(home) / "external"
            outside.mkdir()
            (outside / "KEEP.md").write_text("do not delete", encoding="utf-8")
            (root / "docs" / "tasks" / "TEMPLATE-1.md").unlink()
            (root / "docs" / "tasks").rmdir()
            (root / "docs" / "tasks").symlink_to(outside, target_is_directory=True)

            proc = self.run_init(root)
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("Refusing symlinked managed directory", proc.stderr + proc.stdout)
            self.assertEqual((outside / "KEEP.md").read_text(encoding="utf-8"), "do not delete")
            self.assertEqual((root / ".ai/telemetry/cycles.jsonl").read_text(encoding="utf-8"), "source-history")
            self.assertFalse((root / ".ai/project-initialized").exists())

    def test_rejects_symlink_bootstrap_file_without_overwriting_external_data(self):
        with tempfile.TemporaryDirectory() as home:
            root = Path(home) / "project"
            root.mkdir()
            self.fixture(root)
            outside = Path(home) / "sensitive.txt"
            outside.write_text("protected", encoding="utf-8")
            (root / "README.md").symlink_to(outside)
            proc = self.run_init(root)
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("Refusing symlinked bootstrap target", proc.stderr + proc.stdout)
            self.assertEqual(outside.read_text(encoding="utf-8"), "protected")
            self.assertTrue((root / "docs/tasks/TEMPLATE-1.md").exists())

    def test_refuses_existing_bootstrap_task_before_deleting_template_data(self):
        with tempfile.TemporaryDirectory() as home:
            root = Path(home)
            self.fixture(root)
            (root / "docs/tasks/PROJECT-BOOTSTRAP.md").write_text("keep me", encoding="utf-8")
            proc = self.run_init(root)
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("Bootstrap Task already exists", proc.stdout + proc.stderr)
            self.assertEqual((root / "docs/tasks/PROJECT-BOOTSTRAP.md").read_text(encoding="utf-8"), "keep me")
            self.assertTrue((root / "docs/tasks/TEMPLATE-1.md").exists())

    def test_refuses_to_initialize_source_repository_checkout(self):
        with tempfile.TemporaryDirectory() as home:
            root = Path(home)
            self.fixture(root)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(["git", "remote", "add", "origin", "https://github.com/mnevrov/agentic-repository-engineering-template.git"], cwd=root, check=True)
            proc = self.run_init(root)
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("Refusing to initialize the source template", proc.stderr + proc.stdout)
            self.assertTrue((root / "docs/tasks/TEMPLATE-1.md").exists())

    def test_refuses_local_path_clone_named_after_template(self):
        # Confirmed adversarial finding: `git clone /abs/path/…-template`
        # keeps the full template history and must never be initialized in
        # place, on any host or path scheme.
        with tempfile.TemporaryDirectory() as home:
            root = Path(home) / "agentic-repository-engineering-template"
            root.mkdir()
            self.fixture(root)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(["git", "remote", "add", "origin", "/srv/mirrors/agentic-repository-engineering-template"],
                           cwd=root, check=True)
            proc = self.run_init(root)
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("Refusing to initialize the source template", proc.stderr + proc.stdout)
            self.assertTrue((root / "docs/tasks/TEMPLATE-1.md").exists())

    def test_refuses_source_origin_with_dot_segment(self):
        # Round-5 F2: `git clone .` inside the template records
        # '/abs/path/…-template/.' verbatim; the guard must resolve dot
        # segments before the name check instead of initializing in place.
        with tempfile.TemporaryDirectory() as home:
            root = Path(home) / "pilot"
            root.mkdir()
            self.fixture(root)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(["git", "remote", "add", "origin",
                            "/srv/mirrors/agentic-repository-engineering-template/."],
                           cwd=root, check=True)
            proc = self.run_init(root)
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("Refusing to initialize the source template", proc.stderr + proc.stdout)
            self.assertTrue((root / "docs/tasks/TEMPLATE-1.md").exists())

    def test_refuses_multi_valued_origin_when_any_value_is_source(self):
        # Round-5 F3: origin_url() reports None for a multi-valued url; the
        # destructive guard must not collapse that ambiguity into 'not the
        # source' — one of the values may be the template itself.
        with tempfile.TemporaryDirectory() as home:
            root = Path(home) / "pilot"
            root.mkdir()
            self.fixture(root)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(["git", "remote", "add", "origin",
                            "https://github.com/example/pilot-project.git"],
                           cwd=root, check=True)
            subprocess.run(["git", "config", "--add", "remote.origin.url",
                            "/srv/mirrors/agentic-repository-engineering-template"],
                           cwd=root, check=True)
            proc = self.run_init(root)
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("Refusing to initialize the source template", proc.stderr + proc.stdout)
            self.assertTrue((root / "docs/tasks/TEMPLATE-1.md").exists())

    def test_downstream_project_gates_do_not_conflict_with_template_contract_tests(self):
        with tempfile.TemporaryDirectory() as home:
            root = Path(home)
            (root / "template_tests").mkdir()
            (root / ".ai").mkdir()
            (root / ".ai/project-initialized").write_text("project initialized", encoding="utf-8")
            shutil.copy2(ROOT / "template_tests/test_template_contract.py", root / "template_tests/test_template_contract.py")
            (root / "Makefile").write_text(
                ".PHONY: check test test-template\n"
                "check:\n\t@echo real-check\n"
                "test:\n\t@echo real-test\n"
                "test-template:\n\tpython3 -m unittest discover -s template_tests -p 'test_*.py'\n",
                encoding="utf-8",
            )
            proc = subprocess.run(["make", "test-template"], cwd=root, text=True, capture_output=True)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertIn("skipped=3", proc.stdout + proc.stderr)


if __name__ == "__main__":
    unittest.main()
