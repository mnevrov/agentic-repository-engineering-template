#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

from telemetry_cutover import UNSAFE_REF, bootstrap_cutover, history_monotonic

TELEMETRY_REL = Path(".ai/telemetry/cycles.jsonl")


def git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=repo, text=True, capture_output=True)


def changed_files(repo: Path, base_ref: str) -> list[str]:
    if not base_ref or UNSAFE_REF.search(base_ref):
        raise ValueError(f"unsafe telemetry base ref: {base_ref!r}")
    proc = git(repo, "diff", "--name-only", base_ref, "HEAD")
    if proc.returncode != 0:
        raise ValueError(proc.stderr.strip() or f"cannot diff {base_ref}..HEAD")
    return [line for line in proc.stdout.splitlines() if line]


def telemetry_lines_at_ref(repo: Path, ref: str) -> list[str]:
    proc = git(repo, "show", f"{ref}:{TELEMETRY_REL.as_posix()}")
    if proc.returncode == 0:
        return proc.stdout.splitlines()
    if "does not exist in" in proc.stderr or "exists on disk, but not in" in proc.stderr:
        return []
    raise ValueError(proc.stderr.strip() or f"cannot read telemetry at {ref}")


def telemetry_lines_now(repo: Path) -> list[str]:
    path = repo / TELEMETRY_REL
    return path.read_text(encoding="utf-8").splitlines() if path.exists() else []


def check(repo: Path, base_ref: str) -> tuple[bool, str]:
    changed = changed_files(repo, base_ref)
    substantive = [path for path in changed if path != TELEMETRY_REL.as_posix()]
    if not substantive:
        return True, "no substantive change requires a telemetry row"

    old = telemetry_lines_at_ref(repo, base_ref)
    new = telemetry_lines_now(repo)
    # Integrity over the full range is enforced here as well, so the gate
    # cannot be satisfied alone against a stale PR target branch after rows
    # were deleted or rewritten inside base..HEAD.
    if not history_monotonic(repo, base_ref, new):
        return False, "Telemetry is not append-only: ledger rewritten inside base..HEAD history"
    if bootstrap_cutover(repo, base_ref, old, new):
        old = []  # Project's first ledger starts after dropping source-only history.
    appended = len(new) - len(old)
    if appended <= 0:
        return False, f"substantive change without appended telemetry: {len(substantive)} changed file(s)"
    return True, f"telemetry required: {appended} row(s) appended for {len(substantive)} substantive changed file(s)"


def main() -> None:
    parser = argparse.ArgumentParser(description="Require new telemetry for substantive repository changes.")
    parser.add_argument("--base-ref", required=True)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()

    try:
        ok, message = check(args.repo.resolve(), args.base_ref)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    print(message)
    if not ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
