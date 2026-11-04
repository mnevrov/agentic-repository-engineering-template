#!/usr/bin/env python3
"""Offline OpenCode v2 acceptance: never sends a model request."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def command(cli: str, *args: str) -> tuple[bool, str]:
    try:
        proc = subprocess.run([cli, *args], cwd=ROOT, text=True,
                              capture_output=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired):
        return False, ""
    return proc.returncode == 0, proc.stdout


def check(cli: str) -> list[str]:
    failures = []
    try:
        config = json.loads((ROOT / "opencode.json").read_text(encoding="utf-8"))
        if "model" in config or "provider" in config:
            failures.append("repository config pins model/provider")
        if not isinstance(config.get("permissions"), list):
            failures.append("missing V2 permissions")
    except (OSError, ValueError):
        failures.append("invalid opencode.json")
    for name in ("develop", "iterate", "adopt-existing", "grill-me"):
        if not (ROOT / ".opencode/commands" / (name + ".md")).is_file():
            failures.append("missing command: " + name)
    for name in ("adopt-existing", "grill-me"):
        if not (ROOT / ".opencode/skills" / name / "SKILL.md").is_file():
            failures.append("missing skill: " + name)
    ok, version = command(cli, "--version")
    if not ok or not re.search(r"\bv?2\.\d+", version):
        failures.append("OpenCode CLI missing or not v2")
        return failures
    ok, _ = command(cli, "debug", "config")
    if not ok:
        failures.append("OpenCode debug config failed (details suppressed)")
    ok, agents = command(cli, "debug", "agents")
    if not ok:
        failures.append("OpenCode debug agents failed (details suppressed)")
    else:
        for name in ("reviewer", "repository-discovery", "adoption-orchestrator"):
            if name not in agents:
                failures.append("OpenCode does not discover agent: " + name)
    return failures


def main() -> int:
    p = argparse.ArgumentParser(description="Validate OpenCode v2 integration without inference")
    p.add_argument("--cli", default="opencode")
    args = p.parse_args()
    errors = check(args.cli)
    if errors:
        for error in errors:
            print("[FAIL] " + error)
        return 1
    print("OpenCode v2 offline acceptance: PASS (no model request; connected HOST not checked)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
