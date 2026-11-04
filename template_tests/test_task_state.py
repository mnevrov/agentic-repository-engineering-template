#!/usr/bin/env python3
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check-task-state.py"


class TaskStateTests(unittest.TestCase):
    def run_check(self, root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["python3", str(SCRIPT), "--root", str(root)],
            text=True,
            capture_output=True,
        )

    def write_task(self, root: Path, task_id: str, status: str) -> None:
        path = root / "docs" / "tasks" / f"{task_id}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            f"# {task_id}\n\n**Статус:** {status}  \n",
            encoding="utf-8",
        )

    def test_consistent_states_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            todo = root / "docs" / "backlog" / "TODO.md"
            todo.parent.mkdir(parents=True, exist_ok=True)
            todo.write_text(
                """# TODO

## Ready
- [ ] DEMO-1 — ready task

## Planned
- [ ] DEMO-2 — planned task

## Done
- [x] DEMO-BOOTSTRAP — done task
""",
                encoding="utf-8",
            )
            self.write_task(root, "DEMO-1", "ready")
            self.write_task(root, "DEMO-2", "planned")
            self.write_task(root, "DEMO-BOOTSTRAP", "done")

            proc = self.run_check(root)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertIn("3 task(s) checked", proc.stdout)

    def test_ready_planned_mismatch_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            todo = root / "docs" / "backlog" / "TODO.md"
            todo.parent.mkdir(parents=True, exist_ok=True)
            todo.write_text(
                """# TODO

## Ready
- [ ] DEMO-1 — ready task
""",
                encoding="utf-8",
            )
            self.write_task(root, "DEMO-1", "planned")

            proc = self.run_check(root)
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("TODO expects 'ready'", proc.stdout + proc.stderr)

    def test_missing_task_file_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            todo = root / "docs" / "backlog" / "TODO.md"
            todo.parent.mkdir(parents=True, exist_ok=True)
            todo.write_text(
                """# TODO

## In progress
- [ ] TASK-X — missing file
""",
                encoding="utf-8",
            )

            proc = self.run_check(root)
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("TODO references missing", proc.stdout + proc.stderr)


if __name__ == "__main__":
    unittest.main()
