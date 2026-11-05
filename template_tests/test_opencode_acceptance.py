import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/opencode-acceptance.py"


class OpenCodeAcceptanceTests(unittest.TestCase):
    def run_cli(self, *, version="opencode v2.2.5",
                agents="reviewer repository-discovery adoption-orchestrator",
                sources=None, disable=None):
        if sources is None:
            sources = [{"type": "document", "path": str(ROOT / "opencode.json")},
                       {"type": "directory", "path": str(ROOT / ".opencode")}]
        with tempfile.TemporaryDirectory() as tmp:
            cli = Path(tmp) / "fake-opencode"
            cli.write_text(
                "#!/usr/bin/env python3\n"
                "import sys\n"
                f"version = {version!r}\n"
                f"agents = {agents!r}\n"
                f"sources = {json.dumps(sources)!r}\n"
                "args = sys.argv[1:]\n"
                "if args == ['--version']: print(version)\n"
                "elif args == ['debug', 'config']: print(sources)\n"
                "elif args == ['debug', 'agents']: print(agents)\n"
                "else: sys.exit(1)\n", encoding="utf-8"
            )
            cli.chmod(0o755)
            env = dict(os.environ)
            env.pop("OPENCODE_DISABLE_PROJECT_CONFIG", None)
            if disable is not None:
                env["OPENCODE_DISABLE_PROJECT_CONFIG"] = disable
            return subprocess.run(
                [sys.executable, str(SCRIPT), "--cli", str(cli)],
                cwd=ROOT, env=env, text=True, capture_output=True
            )

    def test_valid_v2_passes(self):
        p = self.run_cli()
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("no model request", p.stdout)

    def test_v1_rejected(self):
        p = self.run_cli(version="opencode v1.19.2")
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("not v2", p.stdout)

    def test_missing_reviewer_rejected(self):
        p = self.run_cli(agents="repository-discovery adoption-orchestrator")
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("reviewer", p.stdout)

    def test_missing_project_config_is_distinguished_from_missing_agent(self):
        global_only = [{"type": "document", "path": "/tmp/global/opencode.json"},
                       {"type": "directory", "path": "/tmp/global"}]
        p = self.run_cli(agents="build plan", sources=global_only)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("NOT loading project", p.stdout)
        self.assertIn("opencode service stop", p.stdout)
        self.assertNotIn("/tmp/global", p.stdout)

    def test_service_env_hint_and_no_config_content_leak(self):
        global_only = [{"type": "document", "path": "/tmp/global/opencode.json",
                        "info": {"secret": "HIDDEN_TEST_SECRET"}}]
        p = self.run_cli(agents="build plan", sources=global_only, disable="1")
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("OPENCODE_DISABLE_PROJECT_CONFIG is enabled", p.stdout)
        self.assertNotIn("HIDDEN_TEST_SECRET", p.stdout)

    def test_missing_agents_with_project_source_is_not_called_disabled(self):
        p = self.run_cli(agents="build plan")
        self.assertNotEqual(p.returncode, 0)
        self.assertNotIn("NOT loading project", p.stdout)
