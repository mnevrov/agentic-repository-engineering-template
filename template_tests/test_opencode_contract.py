import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class OpenCodeV2ContractTests(unittest.TestCase):
    def test_only_opencode_native_layout(self):
        self.assertFalse((ROOT / ".claude").exists())
        self.assertFalse((ROOT / "CLAUDE.md").exists())
        for name in ("develop", "iterate", "adopt-existing", "grill-me"):
            path = ROOT / ".opencode" / "commands" / f"{name}.md"
            self.assertTrue(path.is_file(), name)
            self.assertTrue(path.read_text(encoding="utf-8").startswith("---\n"), name)
            self.assertIn("description:", path.read_text(encoding="utf-8"), name)
        for name in ("adopt-existing", "grill-me"):
            path = ROOT / ".opencode" / "skills" / name / "SKILL.md"
            self.assertIn(f"name: {name}", path.read_text(encoding="utf-8"), name)

    def test_v2_config_is_provider_neutral_and_restricts_destructive_commands(self):
        config = json.loads((ROOT / "opencode.json").read_text(encoding="utf-8"))
        self.assertNotIn("model", config)
        self.assertNotIn("provider", config)
        rules = config["permissions"]
        self.assertIn({"action": "external_directory", "resource": "*", "effect": "ask"}, rules)
        self.assertIn({"action": "shell", "resource": "git push --force*", "effect": "deny"}, rules)
        self.assertIn({"action": "shell", "resource": "git reset --hard *", "effect": "deny"}, rules)

    def test_shell_allow_rules_have_no_wildcard_prefix(self):
        # A wildcard allow is a prefix allow: chained commands such as
        # 'git diff HEAD && <arbitrary>' would inherit it and never reach the
        # deny rules. Only exact, operator-free commands may be allowed.
        config = json.loads((ROOT / "opencode.json").read_text(encoding="utf-8"))
        for rule in config["permissions"]:
            if rule["action"] == "shell" and rule["effect"] == "allow":
                resource = rule["resource"]
                self.assertNotIn("*", resource, resource)
                for separator in ("&&", ";", "|", "\n"):
                    self.assertNotIn(separator, resource, resource)

    def test_read_only_subagents(self):
        for path in (ROOT / ".opencode/agents").glob("*.md"):
            doc = path.read_text(encoding="utf-8")
            self.assertIn("mode: subagent", doc, path.name)
            self.assertIn("action: edit", doc, path.name)
            self.assertIn("effect: deny", doc, path.name)
            self.assertIn("action: shell", doc, path.name)
            self.assertNotIn("effect: ask", doc, path.name)
