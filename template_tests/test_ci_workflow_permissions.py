"""Release CI token must be read-only even for untrusted pull requests."""
import re
import unittest
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/doctor.yml"

# Any 'permissions' mapping key inside a job, including quoted aliases that
# evade a plain-text match: two-or-more-space indentation puts it below the
# workflow-level key (column 0).
JOB_PERMISSION_KEY = re.compile(r"""(?m)^\s{2,}["']?permissions["']?\s*:""")


class WorkflowSecurityTests(unittest.TestCase):
    def test_doctor_uses_read_only_token_and_bounded_runtime(self):
        content = WORKFLOW.read_text(encoding="utf-8")
        self.assertRegex(content, r"(?m)^permissions:\s*\n  contents: read\s*\n")
        self.assertNotIn("pull_request_target:", content)
        self.assertRegex(
            content,
            r"(?m)^  doctor:\s*\n    runs-on: ubuntu-latest\s*\n    timeout-minutes: 20",
        )

    def test_no_job_level_permissions_escalation(self):
        # Job-level 'permissions:' blocks widen the read-only workflow token.
        # Text guard always runs and covers quoted keys at job indentation.
        content = WORKFLOW.read_text(encoding="utf-8")
        self.assertIsNone(JOB_PERMISSION_KEY.search(content))

    @unittest.skipIf(yaml is None, "PyYAML unavailable; text guard still ran")
    def test_no_job_level_permissions_escalation_structural(self):
        # Same contract asserted on parsed YAML, immune to formatting tricks.
        workflow = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
        self.assertEqual(workflow.get("permissions"), {"contents": "read"})
        jobs = workflow.get("jobs", {})
        self.assertTrue(jobs)
        for name, job in jobs.items():
            self.assertNotIn("permissions", job, f"job {name} declares permissions")
            self.assertIn("timeout-minutes", job, f"job {name} has no timeout")


if __name__ == "__main__":
    unittest.main()
