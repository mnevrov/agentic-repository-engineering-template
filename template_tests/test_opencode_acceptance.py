import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/opencode-acceptance.py"


class OpenCodeAcceptanceTests(unittest.TestCase):
    def run_cli(self, version="opencode v2.2.5", agents="reviewer repository-discovery adoption-orchestrator"):
        with tempfile.TemporaryDirectory() as tmp:
            cli = Path(tmp) / "fake-opencode"
            cli.write_text(
                "#!/usr/bin/env python3\n"
                "import sys\n"
                f"version = {version!r}\n"
                f"agents = {agents!r}\n"
                "args = sys.argv[1:]\n"
                "if args == ['--version']: print(version)\n"
                "elif args == ['debug', 'config']: print('{}')\n"
                "elif args == ['debug', 'agents']: print(agents)\n"
                "else: sys.exit(1)\n", encoding="utf-8"
            )
            cli.chmod(0o755)
            return subprocess.run([sys.executable, str(SCRIPT), "--cli", str(cli)],
                                  cwd=ROOT, text=True, capture_output=True)

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
