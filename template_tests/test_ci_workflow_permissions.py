"""Release CI token must be read-only even for untrusted pull requests."""
import unittest
from pathlib import Path

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

    def test_no_job_level_permissions_escalation(self):
        # Job-level 'permissions:' blocks can widen the read-only workflow
        # token after the fact; their absence must be asserted, not just the
        # presence of the workflow-level restriction.
        content = WORKFLOW.read_text(encoding="utf-8")
        self.assertNotRegex(content, r"(?m)^\s{2,}permissions:\s*$|^\s{2,}permissions:\s*\S")

if __name__ == "__main__":
    unittest.main()
