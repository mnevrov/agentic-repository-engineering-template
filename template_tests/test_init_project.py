#!/usr/bin/env python3
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "init-project"


class InitProjectTests(unittest.TestCase):
    def make_fixture(self, root: Path) -> None:
        for path in [
            "AGENTS.md",
            "Makefile",
            "PUBLISH_TO_GITHUB.md",
            "docs/adr/0000-template.md",
            "docs/workshop/github-template-qr.png",
            "docs/tasks/TEMPLATE-1.md",
            "docs/tasks/TEMPLATE-2.md",
            "docs/tasks/EXAMPLE-1.md",
            "docs/tasks/KEEP-1.md",
            ".ai/telemetry/cycles.jsonl",
        ]:
            target = root / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("template-history\n", encoding="utf-8")

    def test_initializer_removes_source_history_and_creates_bootstrap_context(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_fixture(root)

            proc = subprocess.run(
                [
                    "python3",
                    str(SCRIPT),
                    "Mini Task Board",
                    "--root",
                    str(root),
                    "--bootstrap-id",
                    "DEMO-BOOTSTRAP",
                    "--bootstrap-title",
                    "Подготовить Mini Task Board к продуктовым итерациям",
                ],
                text=True,
                capture_output=True,
            )
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

            self.assertFalse((root / "docs/tasks/TEMPLATE-1.md").exists())
            self.assertFalse((root / "docs/tasks/TEMPLATE-2.md").exists())
            self.assertFalse((root / "docs/tasks/EXAMPLE-1.md").exists())
            self.assertTrue((root / "docs/tasks/KEEP-1.md").exists())
            self.assertFalse((root / "PUBLISH_TO_GITHUB.md").exists())
            self.assertFalse((root / "docs/adr/0000-template.md").exists())
            self.assertFalse((root / "docs/workshop/github-template-qr.png").exists())
            self.assertEqual((root / ".ai/telemetry/cycles.jsonl").read_text(), "")

            readme = (root / "README.md").read_text(encoding="utf-8")
            self.assertIn("# Mini Task Board", readme)
            self.assertIn("Bootstrap ещё не завершён", readme)

            task = (root / "docs/tasks/DEMO-BOOTSTRAP.md").read_text(encoding="utf-8")
            self.assertIn("**Статус:** ready", task)
            self.assertIn("make test-integration", task)

            todo = (root / "docs/backlog/TODO.md").read_text(encoding="utf-8")
            self.assertIn("DEMO-BOOTSTRAP", todo)
            self.assertNotIn("EXAMPLE-1", todo)
            self.assertTrue((root / ".ai/project-initialized").exists())

    def test_initializer_refuses_accidental_second_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_fixture(root)
            first = subprocess.run(
                ["python3", str(SCRIPT), "Project", "--root", str(root)],
                text=True,
                capture_output=True,
            )
            self.assertEqual(first.returncode, 0, first.stdout + first.stderr)

            second = subprocess.run(
                ["python3", str(SCRIPT), "Project", "--root", str(root)],
                text=True,
                capture_output=True,
            )
            self.assertNotEqual(second.returncode, 0)
            self.assertIn("already initialized", second.stdout + second.stderr)


if __name__ == "__main__":
    unittest.main()
