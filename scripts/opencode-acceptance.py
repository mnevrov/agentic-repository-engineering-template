#!/usr/bin/env python3
"""Offline OpenCode v2 acceptance: no model requests or config secrets in output."""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_AGENTS = ("reviewer", "repository-discovery", "adoption-orchestrator")


def command(cli: str, *args: str) -> tuple[bool, str]:
    try:
        proc = subprocess.run([cli, *args], cwd=ROOT, text=True,
                              capture_output=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired):
        return False, ""
    return proc.returncode == 0, proc.stdout


def project_source_loaded(debug_output: str) -> bool | None:
    """Inspect source paths only. Unknown output format stays unknown, not false."""
    try:
        sources = json.loads(debug_output)
    except ValueError:
        return None
    if isinstance(sources, dict):
        sources = sources.get("sources")
    if not isinstance(sources, list):
        return None
    known_paths = [s.get("path") for s in sources
                   if isinstance(s, dict) and isinstance(s.get("path"), str)]
    if not known_paths:
        return None
    root = ROOT.resolve()
    for source in known_paths:
        try:
            p = Path(source).resolve()
            if p == root / "opencode.json" or p == root / ".opencode" or (
                p.is_relative_to(root / ".opencode")
            ):
                return True
        except (OSError, RuntimeError, ValueError):
            continue
    return False


def check(cli: str) -> list[str]:
    errors: list[str] = []
    try:
        config = json.loads((ROOT / "opencode.json").read_text(encoding="utf-8"))
        if "model" in config or "provider" in config:
            errors.append("repository config pins model/provider")
        if not isinstance(config.get("permissions"), list):
            errors.append("missing V2 permissions")
    except (OSError, ValueError):
        errors.append("invalid opencode.json")
    for name in ("develop", "iterate", "adopt-existing", "grill-me"):
        if not (ROOT / ".opencode/commands" / (name + ".md")).is_file():
            errors.append("missing command: " + name)
    for name in ("adopt-existing", "grill-me"):
        if not (ROOT / ".opencode/skills" / name / "SKILL.md").is_file():
            errors.append("missing skill: " + name)

    ok, version = command(cli, "--version")
    if not ok or not re.search(r"\bv?2\.\d+", version):
        errors.append("OpenCode CLI missing or not v2")
        return errors
    config_ok, config_sources = command(cli, "debug", "config")
    if not config_ok:
        errors.append("OpenCode debug config failed (details suppressed)")
    agents_ok, agent_output = command(cli, "debug", "agents")
    if not agents_ok:
        errors.append("OpenCode debug agents failed (details suppressed)")
        return errors

    missing_agents = [name for name in EXPECTED_AGENTS if name not in agent_output]
    errors.extend("OpenCode does not discover agent: " + name for name in missing_agents)
    if missing_agents:
        loaded = project_source_loaded(config_sources) if config_ok else None
        if loaded is False:
            errors.append(
                "HINT: background OpenCode service is NOT loading project "
                "opencode.json/.opencode sources"
            )
        if os.environ.get("OPENCODE_DISABLE_PROJECT_CONFIG", "").strip().lower() not in (
            "", "0", "false", "no"
        ):
            errors.append(
                "HINT: OPENCODE_DISABLE_PROJECT_CONFIG is enabled in this shell"
            )
        errors.append(
            "HINT: check OPENCODE_DISABLE_PROJECT_CONFIG in the environment that "
            "started the background service, not only this shell"
        )
        errors.append(
            "HINT: after closing active OpenCode sessions, remove the setting "
            "and run 'opencode service stop' then 'opencode service start' "
            "from a clean shell; retry make opencode-acceptance"
        )
        errors.append(
            "HINT: if project sources load but agents remain missing, check "
            "global agent overrides and the actual CLI version; do not paste "
            "raw 'opencode debug config' output (it may contain credentials)"
        )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate OpenCode v2 project integration without inference"
    )
    parser.add_argument("--cli", default="opencode")
    args = parser.parse_args()
    errors = check(args.cli)
    if errors:
        for error in errors:
            print("[FAIL] " + error if not error.startswith("HINT:") else "[INFO] " + error)
        return 1
    print("OpenCode v2 offline acceptance: PASS (no model request; connected HOST not checked)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
