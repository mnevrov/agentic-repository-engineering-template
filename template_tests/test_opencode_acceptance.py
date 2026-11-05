import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/opencode-acceptance.py"
ALL = ("reviewer", "repository-discovery", "adoption-orchestrator")


class OpenCodeAcceptanceTests(unittest.TestCase):
    def run_cli(self, *, version="opencode v2.2.5", agents=ALL,
                sources=None, disable=None, huge=False, corrupt=False,
                misleading=False, truncate_pipe=False):
        if sources is None:
            sources = [{"type": "document", "path": str(ROOT / "opencode.json")},
                       {"type": "directory", "path": str(ROOT / ".opencode")}]
        with tempfile.TemporaryDirectory() as tmp:
            cli = Path(tmp) / "fake-opencode"
            cli.write_text(
                "#!/usr/bin/env python3\n"
                "import json, os, stat, sys\n"
                f"version = {version!r}\n"
                f"agent_ids = {list(agents)!r}\n"
                f"sources = {sources!r}\n"
                f"huge = {huge!r}\n"
                f"corrupt = {corrupt!r}\n"
                f"misleading = {misleading!r}\n"
                f"truncate_pipe = {truncate_pipe!r}\n"
                "args = sys.argv[1:]\n"
                "if args == ['--version']:\n"
                "    print(version)\n"
                "elif args == ['debug', 'config']:\n"
                "    print(json.dumps(sources))\n"
                "elif args == ['debug', 'agents']:\n"
                "    desc = 'repository-discovery' if misleading else 'test'\n"
                "    if huge: desc += 'x' * 250000\n"
                "    payload = json.dumps([{'id': name, 'description': desc} "
                "for name in agent_ids], indent=2)\n"
                "    if corrupt: payload = payload[:-6]\n"
                "    if truncate_pipe and stat.S_ISFIFO(os.fstat(1).st_mode): "
                "payload = payload[:65536]\n"
                "    sys.stdout.write(payload)\n"
                "else:\n"
                "    sys.exit(1)\n", encoding="utf-8"
            )
            cli.chmod(0o755)
            env = dict(os.environ)
            env.pop("OPENCODE_DISABLE_PROJECT_CONFIG", None)
            if disable is not None:
                env["OPENCODE_DISABLE_PROJECT_CONFIG"] = disable
            return subprocess.run(
                [sys.executable, str(SCRIPT), "--cli", str(cli)],
                cwd=ROOT, env=env, text=True, capture_output=True, timeout=45
            )

    def test_valid_v2_passes(self):
        p = self.run_cli()
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("no model request", p.stdout)

    def test_v2_1_2_rejected_with_actionable_version_requirement(self):
        p = self.run_cli(version="opencode v2.1.2")
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("v2.2.5 or newer required", p.stdout)
        self.assertIn("upgrade OpenCode", p.stdout)

    def test_v1_rejected(self):
        p = self.run_cli(version="opencode v1.19.2")
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("not v2", p.stdout)

    def test_missing_reviewer_rejected(self):
        p = self.run_cli(agents=("repository-discovery", "adoption-orchestrator"))
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("agent ID: reviewer", p.stdout)

    def test_global_only_config_triggers_project_warning(self):
        p = self.run_cli(agents=("build", "plan"), sources=[
            {"type": "document", "path": "/tmp/global/opencode.json"},
            {"type": "directory", "path": "/tmp/global"}])
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("NOT loading project", p.stdout)
        self.assertNotIn("/tmp/global", p.stdout)

    def test_environment_warning_never_prints_config_content(self):
        p = self.run_cli(agents=("build",), sources=[{
            "type": "document", "path": "/tmp/global/opencode.json",
            "info": {"secret": "SENSITIVE_TEST_SECRET"}}], disable="1")
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("OPENCODE_DISABLE_PROJECT_CONFIG is enabled", p.stdout)
        self.assertNotIn("SENSITIVE_TEST_SECRET", p.stdout)

    def test_project_source_loaded_no_restart_suggestion(self):
        p = self.run_cli(agents=("build",))
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("ARE loaded", p.stdout)
        self.assertNotIn("restart the service", p.stdout)

    def test_pipe_truncation_regression_large_output(self):
        p = self.run_cli(huge=True, truncate_pipe=True)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)

    def test_absent_agent_id_not_accepted_from_description(self):
        p = self.run_cli(agents=("reviewer", "adoption-orchestrator"),
                         misleading=True)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("agent ID: repository-discovery", p.stdout)

    def test_invalid_output_fails_closed_without_agent_missing_claim(self):
        p = self.run_cli(corrupt=True)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("invalid or incomplete JSON", p.stdout)
        self.assertNotIn("does not discover agent ID", p.stdout)
