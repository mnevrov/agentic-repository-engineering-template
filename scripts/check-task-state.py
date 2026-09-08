#!/usr/bin/env python3
import argparse
import re
from pathlib import Path

SECTION_STATUS = {
    "ready": "ready",
    "in progress": "in progress",
    "planned": "planned",
    "done": "done",
}
TASK_LINE = re.compile(r"^- \[[ xX]\]\s+([A-Za-z0-9][A-Za-z0-9_.-]*)\s+[—-]\s+")
STATUS_LINE = re.compile(r"^\*\*Статус:\*\*\s*(.+?)\s*$", re.MULTILINE)


def normalize(value: str) -> str:
    return " ".join(value.strip().lower().split())


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that TODO sections agree with docs/tasks/<ID>.md statuses."
    )
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()

    root = args.root.resolve()
    todo = root / "docs" / "backlog" / "TODO.md"
    if not todo.exists():
        raise SystemExit(f"missing TODO: {todo}")

    current_expected = None
    seen: dict[str, str] = {}
    errors: list[str] = []
    checked = 0

    for raw_line in todo.read_text(encoding="utf-8").splitlines():
        if raw_line.startswith("## "):
            section = normalize(raw_line[3:])
            current_expected = SECTION_STATUS.get(section)
            continue

        if current_expected is None:
            continue

        match = TASK_LINE.match(raw_line)
        if not match:
            continue

        task_id = match.group(1)
        previous = seen.get(task_id)
        if previous is not None:
            errors.append(
                f"{task_id}: appears in multiple TODO states ({previous}, {current_expected})"
            )
            continue
        seen[task_id] = current_expected

        task_path = root / "docs" / "tasks" / f"{task_id}.md"
        if not task_path.exists():
            errors.append(f"{task_id}: TODO references missing {task_path.relative_to(root)}")
            continue

        text = task_path.read_text(encoding="utf-8")
        status_match = STATUS_LINE.search(text)
        if not status_match:
            errors.append(f"{task_id}: missing '**Статус:**' in {task_path.relative_to(root)}")
            continue

        actual = normalize(status_match.group(1).rstrip())
        if actual != current_expected:
            errors.append(
                f"{task_id}: TODO expects '{current_expected}', task status is '{actual}'"
            )
        checked += 1

    if errors:
        raise SystemExit("Task state consistency failed:\n- " + "\n- ".join(errors))

    print(f"task state consistent: {checked} task(s) checked")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
