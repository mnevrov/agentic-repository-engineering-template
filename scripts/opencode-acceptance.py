#!/usr/bin/env python3
"""Offline OpenCode v2 acceptance: never sends a model request or prints config."""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_AGENTS = ("reviewer", "repository-discovery", "adoption-orchestrator")
MAX_OUTPUT_BYTES = 8 * 1024 * 1024


def command(cli: str, *args: str) -> tuple[bool, str]:
    """Capture CLI stdout in a regular file, not a pipe.

    OpenCode/Bun can truncate large JSON written to stdout pipes on exit.
    TemporaryFile has no persistent path and is never copied to logs.
    """
    try:
        with tempfile.TemporaryFile(mode="w+b") as out:
            proc = subprocess.run(
                [cli, *args], cwd=ROOT, stdout=out,
                stderr=subprocess.DEVNULL, timeout=30, check=False
            )
            out.seek(0)
            data = out.read(MAX_OUTPUT_BYTES + 1)
        if proc.returncode != 0 or len(data) > MAX_OUTPUT_BYTES:
            return False, ""
        return True, data.decode("utf-8", errors="replace")
    except (OSError, subprocess.TimeoutExpired):
        return False, ""


def project_source_loaded(debug_output: str) -> bool | None:
    """Check only source paths, never show resolved model/provider credentials."""
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


def discovered_agent_ids(raw: str) -> set[str] | None:
    """Only top-level agent IDs count; names in descriptions/prompts do not."""
    try:
        agents = json.loads(raw)
    except ValueError:
        return None
    if not isinstance(agents, list) or any(
        not isinstance(item, dict) or not isinstance(item.get("id"), str)
        for item in agents
    ):
        return None
    return {item["id"] for item in agents}


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
    match = re.search(r"\bv?(\d+)\.(\d+)\.(\d+)\b", version) if ok else None
    if match is None or int(match.group(1)) != 2:
        errors.append("OpenCode CLI missing or not v2")
        return errors
    installed = tuple(map(int, match.groups()))
    if installed < (2, 2, 5):
        errors.append(
            "OpenCode v2.2.5 or newer required: v2.1.2 failed project-agent "
            "discovery on clean GitHub CI; upgrade OpenCode and restart its service"
        )
        return errors
    config_ok, sources = command(cli, "debug", "config")
    if not config_ok:
        errors.append("OpenCode debug config failed (details suppressed)")
    agents_ok, raw = command(cli, "debug", "agents")
    if not agents_ok:
        errors.append("OpenCode debug agents failed or exceeded output limit (details suppressed)")
        return errors
    names = discovered_agent_ids(raw)
    if names is None:
        errors.append(
            "OpenCode debug agents returned invalid or incomplete JSON "
            "even with regular-file capture; cannot verify project agent IDs"
        )
        errors.append(
            "HINT: the OpenCode CLI may have a large-output bug; compare "
            "'opencode debug agents > /tmp/agents.json' locally and "
            "do not share full output (it may contain prompts or credentials)"
        )
        return errors

    missing = [name for name in EXPECTED_AGENTS if name not in names]
    errors.extend("OpenCode does not discover agent ID: " + name for name in missing)
    if missing:
        loaded = project_source_loaded(sources) if config_ok else None
        if loaded is True:
            errors.append(
                "HINT: project config sources ARE loaded; check agent file parsing "
                "and any global overrides rather than restarting the service"
            )
        elif loaded is False:
            errors.append(
                "HINT: background OpenCode service is NOT loading project "
                "opencode.json/.opencode sources"
            )
        if os.environ.get("OPENCODE_DISABLE_PROJECT_CONFIG", "").strip().lower() not in (
            "", "0", "false", "no"
        ):
            errors.append("HINT: OPENCODE_DISABLE_PROJECT_CONFIG is enabled in this shell")
        if loaded is not True:
            errors.append(
                "HINT: check OPENCODE_DISABLE_PROJECT_CONFIG in the background "
                "service environment; restart the service from a clean shell "
                "if project config was disabled"
            )
        errors.append(
            "HINT: only top-level agent IDs were checked; never paste raw "
            "'opencode debug config' or 'opencode debug agents' output"
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
            print("[INFO] " + error if error.startswith("HINT:") else "[FAIL] " + error)
        return 1
    print("OpenCode v2 offline acceptance: PASS (no model request; connected HOST not checked)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
