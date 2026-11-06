"""Release CI token must be read-only even for untrusted pull requests."""
import unittest
from pathlib import Path

try:
    import yaml
except ImportError:  # fail closed: the guard itself must be able to run
    yaml = None

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/doctor.yml"


class WorkflowSecurityTests(unittest.TestCase):
    def test_doctor_uses_read_only_token_and_bounded_runtime(self):
        content = WORKFLOW.read_text(encoding="utf-8")
        self.assertRegex(content, r"(?m)^permissions:\s*\n  contents: read\s*\n")
        self.assertNotIn("pull_request_target:", content)
        self.assertRegex(
            content,
            r"(?m)^  doctor:\s*\n    runs-on: ubuntu-latest\s*\n    timeout-minutes: 20",
        )

    @unittest.skipIf(yaml is None, "PyYAML required for structural assertions")
    def test_no_job_level_permissions_escalation(self):
        # Job-level 'permissions:' blocks widen the read-only workflow token.
        # Assert structurally on the parsed YAML: quoted-key aliases
        # ("permissions":) or reordering defeat any text-regex approximation.
        workflow = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
        self.assertEqual(workflow.get("permissions"), {"contents": "read"})
        jobs = workflow.get("jobs", {})
        self.assertTrue(jobs)
        for name, job in jobs.items():
            self.assertNotIn("permissions", job, f"job {name} declares permissions")
            self.assertIn("timeout-minutes", job, f"job {name} has no timeout")


if __name__ == "__main__":
    unittest.main()
