"""One-time cutover from the template's telemetry to a new project's ledger."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

MARKER = ".ai/project-initialized"


def source_only(lines: list[str]) -> bool:
    if not lines:
        return False
    try:
        rows = [json.loads(line) for line in lines]
    except (TypeError, ValueError):
        return False
    return all(
        isinstance(row, dict)
        and isinstance(row.get("task_id"), str)
        and row["task_id"].startswith("TEMPLATE-")
        for row in rows
    )


def bootstrap_cutover(repo: Path, base_ref: str, old: list[str], new: list[str]) -> bool:
    """Allow a reset only across the first committed initializer marker.

    Never allow this exception after the marker exists in the baseline.
    Only a source-only TEMPLATE-* baseline can be replaced; project history
    cannot be silently removed or mixed with source history.
    """
    marker = repo / MARKER
    if not marker.is_file() or marker.is_symlink():
        return False
    current_marker = subprocess.run(
        ["git", "cat-file", "-e", f"HEAD:{MARKER}"],
        cwd=repo, capture_output=True
    )
    old_marker = subprocess.run(
        ["git", "cat-file", "-e", f"{base_ref}:{MARKER}"],
        cwd=repo, capture_output=True
    )
    if current_marker.returncode != 0 or old_marker.returncode == 0:
        return False
    try:
        lines = marker.read_text(encoding="utf-8").splitlines()
    except OSError:
        return False
    if not (
        any(line.startswith("project_name=") and line[13:].strip() for line in lines)
        and any(line.startswith("bootstrap_id=") and line[13:].strip() for line in lines)
    ):
        return False
    if not source_only(old):
        return False
    try:
        records = [json.loads(line) for line in new]
    except (TypeError, ValueError):
        return False
    return all(
        isinstance(row, dict)
        and isinstance(row.get("task_id"), str)
        and not row["task_id"].startswith("TEMPLATE-")
        for row in records
    )
