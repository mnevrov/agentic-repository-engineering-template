#!/usr/bin/env python3
"""Enforce append-only project telemetry, with an explicit first-bootstrap cutover."""
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

from telemetry_cutover import UNSAFE_REF, bootstrap_cutover, history_monotonic
from telemetry_lib import load_jsonl

TELEMETRY_REL = Path(".ai/telemetry/cycles.jsonl")


def git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True)


def check(repo: Path, base_ref: str) -> tuple[bool, str]:
    if not base_ref or UNSAFE_REF.search(base_ref):
        return False, f"Refusing unsafe telemetry base ref: {base_ref!r}"
    if git(repo, "rev-parse", "--verify", "--quiet", f"{base_ref}^{{commit}}").returncode != 0:
        return False, f"Invalid telemetry base ref: {base_ref}"
    try:
        load_jsonl(repo / TELEMETRY_REL)
    except ValueError as exc:
        return False, str(exc)
    previous = git(repo, "show", f"{base_ref}:{TELEMETRY_REL.as_posix()}")
    if previous.returncode == 0:
        old = previous.stdout.splitlines()
    elif "does not exist in" in previous.stderr or "exists on disk, but not in" in previous.stderr:
        old = []
    else:
        return False, "Could not retrieve base telemetry for comparison"

    path = repo / TELEMETRY_REL
    new = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
    if bootstrap_cutover(repo, base_ref, old, new):
        return True, "telemetry bootstrap cutover: source TEMPLATE-* history isolated from new project"
    if len(new) < len(old) or new[:len(old)] != old:
        return False, "Telemetry is not append-only: existing rows removed, modified or reordered"
    if not history_monotonic(repo, base_ref, new):
        return False, "Telemetry is not append-only: ledger rewritten inside base..HEAD history"
    return True, f"telemetry append-only: preserved {len(old)} existing row(s), appended {len(new)-len(old)}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Enforce telemetry history integrity.")
    parser.add_argument("--base-ref", required=True)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    ok, message = check(args.repo.resolve(), args.base_ref)
    print(message)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
