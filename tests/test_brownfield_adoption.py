#!/usr/bin/env python3
from __future__ import annotations

import importlib.machinery
import importlib.util
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / 'tests/fixtures/brownfield-project'
GIT_REPOSITORY_ENV_VARS = {
    'GIT_DIR', 'GIT_WORK_TREE', 'GIT_COMMON_DIR', 'GIT_INDEX_FILE',
    'GIT_OBJECT_DIRECTORY', 'GIT_ALTERNATE_OBJECT_DIRECTORIES',
    'GIT_NAMESPACE', 'GIT_CEILING_DIRECTORIES', 'GIT_DISCOVERY_ACROSS_FILESYSTEM',
}

_doctor_loader = importlib.machinery.SourceFileLoader('repo_doctor_module', str(ROOT / 'scripts/repo-doctor'))
_doctor_spec = importlib.util.spec_from_loader(_doctor_loader.name, _doctor_loader)
repo_doctor_module = importlib.util.module_from_spec(_doctor_spec)
_doctor_loader.exec_module(repo_doctor_module)

_new_task_loader = importlib.machinery.SourceFileLoader('new_task_module', str(ROOT / 'scripts/new-task'))
_new_task_spec = importlib.util.spec_from_loader(_new_task_loader.name, _new_task_loader)
new_task_module = importlib.util.module_from_spec(_new_task_spec)
_new_task_loader.exec_module(new_task_module)


def run(cmd: list[str], cwd: Path, check: bool = True) -> subprocess.CompletedProcess[str]:
    """Run test commands without inheriting Git repository-location overrides."""
    env = os.environ.copy()
    for key in GIT_REPOSITORY_ENV_VARS:
        env.pop(key, None)
    return subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, check=check, env=env)


class BrownfieldAdoptionTests(unittest.TestCase):
    def make_repo(self) -> Path:
        root = Path(tempfile.mkdtemp()) / 'existing-project'
        shutil.copytree(FIXTURE, root)
        run(['git', 'init', '-q'], root)
        run(['git', 'config', 'user.email', 'test@example.com'], root)
        run(['git', 'config', 'user.name', 'Test'], root)
        run(['git', 'add', '.'], root)
        run(['git', 'commit', '-qm', 'existing project baseline'], root)
        return root

    def test_audit_is_read_only_and_detects_existing_mechanisms(self):
        repo = self.make_repo()
        before = run(['git', 'status', '--porcelain'], repo).stdout
        proc = run([str(ROOT / 'scripts/repo-audit'), '--repo', str(repo), '--format', 'json'], ROOT)
        after = run(['git', 'status', '--porcelain'], repo).stdout
        self.assertEqual(before, after)
        report = json.loads(proc.stdout)
        self.assertTrue(report['repository']['git_repository'])
        self.assertIn('CLAUDE.md', {x['path'] for x in report['instructions']})
        self.assertIn('CONTRIBUTING.md', {x['path'] for x in report['instructions']})
        self.assertIn('.github/workflows/build.yml', {x['path'] for x in report['ci']})
        commands = {x['command'] for x in report['verification_candidates']}
        self.assertIn('./scripts/check.sh', commands)
        self.assertIn('./scripts/test.sh', commands)
        self.assertIn('BACKLOG.md', report['backlog_candidates'])

    def test_audit_includes_nonignored_untracked_repository_rules(self):
        repo = self.make_repo()
        (repo / 'AGENTS.md').write_text('# Local agent rules\n', encoding='utf-8')
        proc = run([str(ROOT / 'scripts/repo-audit'), '--repo', str(repo), '--format', 'json'], ROOT)
        report = json.loads(proc.stdout)
        self.assertIn('AGENTS.md', {x['path'] for x in report['instructions']})
        self.assertIn('?? AGENTS.md', run(['git', 'status', '--porcelain'], repo).stdout)

    def test_adoption_doctor_does_not_require_template_layout(self):
        repo = self.make_repo()
        config = {
            'schema_version': 1,
            'mode': 'adoption',
            'stage': 'minimum-context',
            'source_of_truth_precedence': [
                'security_and_project_policy', 'repository_instructions',
                'architecture_and_decisions', 'current_task_contract',
                'agent_suggestions', 'chat_history'
            ],
            'sources': {
                'instructions': {'primary': 'CONTRIBUTING.md', 'also_read': ['CLAUDE.md']},
                'architecture': {'status': 'partial', 'paths': ['README.md']},
                'decisions': {'kind': 'none', 'paths': []},
                'tasks': {'kind': 'markdown-backlog', 'reference': 'BACKLOG.md', 'local_contract_dir': '.agentic/tasks'},
                'ci': {'status': 'existing', 'paths': ['.github/workflows/build.yml']},
            },
            'verification': {
                'check': {'status': 'configured', 'command': './scripts/check.sh'},
                'test': {'status': 'configured', 'command': './scripts/test.sh'},
                'integration': {'status': 'not_applicable', 'reason': 'fixture has no integration boundary'},
            },
            'unresolved_conflicts': [],
            'open_questions': [],
        }
        (repo / '.agentic-repository.json').write_text(json.dumps(config, indent=2), encoding='utf-8')
        proc = run([str(ROOT / 'scripts/repo-doctor'), '--adoption', '--repo', str(repo)], ROOT)
        self.assertIn('Brownfield adoption context looks consistent.', proc.stdout)
        self.assertFalse((repo / 'docs/tasks').exists())
        self.assertFalse((repo / 'Makefile').exists())

    def test_external_task_contract_reuses_existing_tracker(self):
        repo = self.make_repo()
        tracked_before = {
            p: (repo / p).read_bytes()
            for p in ['README.md', 'CONTRIBUTING.md', 'CLAUDE.md', 'BACKLOG.md', '.github/workflows/build.yml']
        }
        proc = run([
            str(ROOT / 'scripts/new-task'), '--repo', str(repo), '--contract', '--source', 'BACKLOG.md#LEGACY-17',
            'LEGACY-17', 'Collapse repeated internal whitespace'
        ], ROOT)
        self.assertIn('.agentic/tasks/LEGACY-17.md', proc.stdout)
        contract = (repo / '.agentic/tasks/LEGACY-17.md').read_text(encoding='utf-8')
        self.assertIn('BACKLOG.md#LEGACY-17', contract)
        for path, content in tracked_before.items():
            self.assertEqual((repo / path).read_bytes(), content, path)
        run(['./scripts/check.sh'], repo)
        run(['./scripts/test.sh'], repo)

    def test_new_task_default_cli_remains_backward_compatible(self):
        repo = self.make_repo()
        (repo / 'docs/tasks').mkdir(parents=True)
        proc = run([str(ROOT / 'scripts/new-task'), '--repo', str(repo), 'LOCAL-1', 'Local task'], ROOT)
        self.assertIn('docs/tasks/LOCAL-1.md', proc.stdout)
        self.assertIn('LOCAL-1 — Local task', (repo / 'docs/tasks/LOCAL-1.md').read_text(encoding='utf-8'))

    def test_audit_ignores_inherited_git_repository_override(self):
        repo = self.make_repo()
        contaminated = os.environ.copy()
        contaminated['GIT_DIR'] = str(repo.parent / 'wrong-git-dir')
        proc = subprocess.run(
            [str(ROOT / 'scripts/repo-audit'), '--repo', str(repo), '--format', 'json'],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
            env=contaminated,
        )
        report = json.loads(proc.stdout)
        self.assertTrue(report['repository']['git_repository'])

    def test_doctor_ignores_inherited_git_repository_override(self):
        repo = self.make_repo()
        previous = os.environ.get('GIT_DIR')
        os.environ['GIT_DIR'] = str(repo.parent / 'wrong-git-dir')
        try:
            self.assertTrue(repo_doctor_module.git_repo(repo))
        finally:
            if previous is None:
                os.environ.pop('GIT_DIR', None)
            else:
                os.environ['GIT_DIR'] = previous

    def test_adoption_doctor_requires_task_source_reference(self):
        repo = self.make_repo()
        config = {
            'schema_version': 1,
            'mode': 'adoption',
            'stage': 'minimum-context',
            'source_of_truth_precedence': ['repository_instructions', 'current_task_contract'],
            'sources': {
                'instructions': {'primary': 'CONTRIBUTING.md', 'also_read': []},
                'architecture': {'status': 'partial', 'paths': ['README.md']},
                'decisions': {'kind': 'none', 'paths': []},
                'tasks': {'kind': 'external', 'local_contract_dir': '.agentic/tasks'},
                'ci': {'status': 'existing', 'paths': ['.github/workflows/build.yml']},
            },
            'verification': {
                'check': {'status': 'configured', 'command': './scripts/check.sh'},
                'test': {'status': 'configured', 'command': './scripts/test.sh'},
                'integration': {'status': 'not_applicable', 'reason': 'fixture has no integration boundary'},
            },
            'unresolved_conflicts': [],
            'open_questions': [],
        }
        (repo / '.agentic-repository.json').write_text(json.dumps(config, indent=2), encoding='utf-8')
        proc = run([str(ROOT / 'scripts/repo-doctor'), '--adoption', '--repo', str(repo)], ROOT, check=False)
        self.assertEqual(proc.returncode, 2)
        self.assertIn('[NOT_CONFIGURED] sources.tasks.reference', proc.stdout)

    def test_adoption_doctor_requires_explicit_check_and_test_gates(self):
        repo = self.make_repo()
        config = {
            'schema_version': 1,
            'mode': 'adoption',
            'stage': 'minimum-context',
            'source_of_truth_precedence': ['repository_instructions', 'current_task_contract'],
            'sources': {
                'instructions': {'primary': 'CONTRIBUTING.md', 'also_read': []},
                'architecture': {'status': 'partial', 'paths': ['README.md']},
                'decisions': {'kind': 'none', 'paths': []},
                'tasks': {
                    'kind': 'markdown-backlog',
                    'reference': 'BACKLOG.md',
                    'local_contract_dir': '.agentic/tasks',
                },
                'ci': {'status': 'existing', 'paths': ['.github/workflows/build.yml']},
            },
            'verification': {
                'integration': {'status': 'not_applicable', 'reason': 'fixture has no integration boundary'},
            },
            'unresolved_conflicts': [],
            'open_questions': [],
        }
        (repo / '.agentic-repository.json').write_text(json.dumps(config, indent=2), encoding='utf-8')
        proc = run([str(ROOT / 'scripts/repo-doctor'), '--adoption', '--repo', str(repo)], ROOT, check=False)
        self.assertEqual(proc.returncode, 2)
        self.assertIn('[NOT_CONFIGURED] verification.check not mapped', proc.stdout)
        self.assertIn('[NOT_CONFIGURED] verification.test not mapped', proc.stdout)

    def test_template_secret_scan_includes_untracked_files_without_values(self):
        repo = self.make_repo()
        secret = 'ghp_' + ('A' * 24)
        (repo / 'local-untracked.txt').write_text(f'token={secret}\n', encoding='utf-8')
        hits = repo_doctor_module.scan_secret_locations(repo)
        self.assertIn('local-untracked.txt:1', hits)
        self.assertTrue(all(secret not in hit for hit in hits))

    def test_new_task_rejects_missing_target_repo(self):
        parent = Path(tempfile.mkdtemp())
        missing = parent / 'typo-repository'
        proc = run([
            str(ROOT / 'scripts/new-task'), '--repo', str(missing), '--contract',
            '--source', 'JIRA-1', 'JIRA-1', 'Task'
        ], ROOT, check=False)
        self.assertNotEqual(proc.returncode, 0)
        self.assertFalse(missing.exists())

    def test_new_task_rejects_output_path_escape(self):
        repo = self.make_repo()
        outside = repo.parent / 'escaped'
        proc = run([
            str(ROOT / 'scripts/new-task'), '--repo', str(repo), '--contract',
            '--output-dir', '../escaped', '--source', 'JIRA-2', 'JIRA-2', 'Task'
        ], ROOT, check=False)
        self.assertNotEqual(proc.returncode, 0)
        self.assertFalse(outside.exists())

    def test_template_secret_scan_keeps_tracked_build_and_vendor_coverage(self):
        repo = self.make_repo()
        secret = 'ghp_' + ('B' * 24)
        for rel in ('build/credentials.txt', 'vendor/private.txt'):
            path = repo / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f'token={secret}\n', encoding='utf-8')
            run(['git', 'add', rel], repo)
        hits = repo_doctor_module.scan_secret_locations(repo)
        self.assertIn('build/credentials.txt:1', hits)
        self.assertIn('vendor/private.txt:1', hits)
        self.assertTrue(all(secret not in hit for hit in hits))

    def test_audit_refuses_output_inside_target_repository(self):
        repo = self.make_repo()
        readme = repo / 'README.md'
        before = readme.read_bytes()
        proc = run([
            str(ROOT / 'scripts/repo-audit'), '--repo', str(repo),
            '--output', str(readme)
        ], ROOT, check=False)
        self.assertNotEqual(proc.returncode, 0)
        self.assertEqual(readme.read_bytes(), before)

    def test_audit_refuses_existing_external_output_and_symlink_target(self):
        repo = self.make_repo()
        outside_dir = Path(tempfile.mkdtemp())
        existing = outside_dir / 'audit.md'
        existing.write_text('keep me\n', encoding='utf-8')
        proc = run([
            str(ROOT / 'scripts/repo-audit'), '--repo', str(repo),
            '--output', str(existing)
        ], ROOT, check=False)
        self.assertNotEqual(proc.returncode, 0)
        self.assertEqual(existing.read_text(encoding='utf-8'), 'keep me\n')

        inside = repo / 'audit.md'
        link = outside_dir / 'audit-link.md'
        link.symlink_to(inside)
        proc = run([
            str(ROOT / 'scripts/repo-audit'), '--repo', str(repo),
            '--output', str(link)
        ], ROOT, check=False)
        self.assertNotEqual(proc.returncode, 0)
        self.assertFalse(inside.exists())

    def test_adoption_doctor_is_stage_aware(self):
        repo = self.make_repo()
        config = {
            'schema_version': 1,
            'mode': 'adoption',
            'stage': 'risk-aware',
            'source_of_truth_precedence': ['repository_instructions', 'current_task_contract'],
            'sources': {
                'instructions': {'primary': 'CONTRIBUTING.md', 'also_read': []},
                'architecture': {'status': 'partial', 'paths': ['README.md']},
                'decisions': {'kind': 'none', 'paths': []},
                'tasks': {'kind': 'markdown-backlog', 'reference': 'BACKLOG.md', 'local_contract_dir': '.agentic/tasks'},
                'ci': {'status': 'existing', 'paths': ['.github/workflows/build.yml']},
            },
            'verification': {
                'check': {'status': 'configured', 'command': './scripts/check.sh'},
                'test': {'status': 'configured', 'command': './scripts/test.sh'},
                'integration': {'status': 'not_applicable', 'reason': 'fixture has no integration boundary'},
            },
            'unresolved_conflicts': [],
            'open_questions': [],
        }
        (repo / '.agentic-repository.json').write_text(json.dumps(config, indent=2), encoding='utf-8')
        proc = run([str(ROOT / 'scripts/repo-doctor'), '--adoption', '--repo', str(repo)], ROOT, check=False)
        self.assertEqual(proc.returncode, 2)
        self.assertIn('[NOT_CONFIGURED] capabilities.repeatable_workflow', proc.stdout)
        self.assertIn('[NOT_CONFIGURED] capabilities.independent_verification', proc.stdout)
        self.assertIn('[NOT_CONFIGURED] capabilities.risk_aware', proc.stdout)

    def test_adoption_doctor_accepts_fully_evidenced_risk_aware_stage(self):
        repo = self.make_repo()
        contract = repo / '.agentic/tasks/LEGACY-17.md'
        contract.parent.mkdir(parents=True)
        contract.write_text('# LEGACY-17\n## Acceptance Criteria\n## Evidence\n', encoding='utf-8')
        configured = lambda ref_type, value: {
            'status': 'configured',
            'reference': {'type': ref_type, 'value': value},
        }
        config = {
            'schema_version': 1,
            'mode': 'adoption',
            'stage': 'risk-aware',
            'source_of_truth_precedence': ['repository_instructions', 'current_task_contract'],
            'sources': {
                'instructions': {'primary': 'CONTRIBUTING.md', 'also_read': ['CLAUDE.md']},
                'architecture': {'status': 'partial', 'paths': ['README.md']},
                'decisions': {'kind': 'none', 'paths': []},
                'tasks': {'kind': 'markdown-backlog', 'reference': 'BACKLOG.md', 'local_contract_dir': '.agentic/tasks'},
                'ci': {'status': 'existing', 'paths': ['.github/workflows/build.yml']},
            },
            'verification': {
                'check': {'status': 'configured', 'command': './scripts/check.sh'},
                'test': {'status': 'configured', 'command': './scripts/test.sh'},
                'integration': {'status': 'not_applicable', 'reason': 'fixture has no integration boundary'},
            },
            'capabilities': {
                'repeatable_workflow': {
                    'task_contract': configured('path', '.agentic/tasks/LEGACY-17.md'),
                    'acceptance_criteria': configured('path', '.agentic/tasks/LEGACY-17.md#acceptance-criteria'),
                    'evidence': configured('path', '.agentic/tasks/LEGACY-17.md#evidence'),
                    'definition_of_done': configured('path', 'GOVERNANCE.md#definition-of-done'),
                },
                'independent_verification': {
                    'review_mechanism': configured('path', 'GOVERNANCE.md#independent-review'),
                    'exact_sha_diff_evidence': configured('path', 'GOVERNANCE.md#independent-review'),
                    'ci_pr_linkage': configured('path', '.github/workflows/build.yml'),
                },
                'risk_aware': {
                    'risk_model': configured('path', 'GOVERNANCE.md#risk-model'),
                    'high_risk_gates': configured('path', 'GOVERNANCE.md#risk-model'),
                    'adversarial_review': configured('path', 'GOVERNANCE.md#adversarial-review'),
                    'technical_enforcement': configured('path', '.github/workflows/build.yml'),
                },
            },
            'unresolved_conflicts': [],
            'open_questions': [],
        }
        (repo / '.agentic-repository.json').write_text(json.dumps(config, indent=2), encoding='utf-8')
        proc = run([str(ROOT / 'scripts/repo-doctor'), '--adoption', '--repo', str(repo)], ROOT)
        self.assertIn('Brownfield adoption context looks consistent.', proc.stdout)

    def test_adoption_doctor_rejects_source_path_escape_and_symlink_escape(self):
        repo = self.make_repo()
        outside = repo.parent / 'outside-rules.md'
        outside.write_text('outside\n', encoding='utf-8')
        config = {
            'schema_version': 1,
            'mode': 'adoption',
            'stage': 'minimum-context',
            'source_of_truth_precedence': ['repository_instructions', 'current_task_contract'],
            'sources': {
                'instructions': {'primary': '../outside-rules.md', 'also_read': []},
                'tasks': {'kind': 'markdown-backlog', 'reference': 'BACKLOG.md', 'local_contract_dir': '.agentic/tasks'},
            },
            'verification': {
                'check': {'status': 'configured', 'command': './scripts/check.sh'},
                'test': {'status': 'configured', 'command': './scripts/test.sh'},
            },
            'unresolved_conflicts': [],
            'open_questions': [],
        }
        (repo / '.agentic-repository.json').write_text(json.dumps(config, indent=2), encoding='utf-8')
        proc = run([str(ROOT / 'scripts/repo-doctor'), '--adoption', '--repo', str(repo)], ROOT, check=False)
        self.assertEqual(proc.returncode, 1)
        self.assertIn('must be repository-relative without ..', proc.stdout)

        (repo / 'rules-link.md').symlink_to(outside)
        config['sources']['instructions']['primary'] = 'rules-link.md'
        (repo / '.agentic-repository.json').write_text(json.dumps(config, indent=2), encoding='utf-8')
        proc = run([str(ROOT / 'scripts/repo-doctor'), '--adoption', '--repo', str(repo)], ROOT, check=False)
        self.assertEqual(proc.returncode, 1)
        self.assertIn('escapes repository', proc.stdout)

    def test_adoption_doctor_rejects_placeholders_and_malformed_nested_types(self):
        repo = self.make_repo()
        config = {
            'schema_version': 1,
            'mode': 'adoption',
            'stage': 'minimum-context',
            'source_of_truth_precedence': ['repository_instructions', 'current_task_contract'],
            'sources': {
                'instructions': {'primary': 'CONTRIBUTING.md', 'also_read': 'CLAUDE.md'},
                'tasks': {'kind': 'external', 'reference': 'not specified yet', 'local_contract_dir': '.agentic/tasks'},
            },
            'verification': {
                'check': {'status': 'configured', 'command': 'TODO later'},
                'test': {'status': 'configured', 'command': './scripts/test.sh'},
                'integration': {'status': 'not_applicable', 'reason': 'unknown yet'},
            },
            'unresolved_conflicts': [],
            'open_questions': [],
        }
        (repo / '.agentic-repository.json').write_text(json.dumps(config, indent=2), encoding='utf-8')
        proc = run([str(ROOT / 'scripts/repo-doctor'), '--adoption', '--repo', str(repo)], ROOT, check=False)
        self.assertEqual(proc.returncode, 1)
        self.assertIn('sources.instructions.also_read must be a list', proc.stdout)
        self.assertIn('[NOT_CONFIGURED] sources.tasks.reference', proc.stdout)
        self.assertIn('configured with placeholder/missing command', proc.stdout)
        self.assertIn('not_applicable with placeholder/missing reason', proc.stdout)

    def test_new_task_contract_requires_source_and_git_root(self):
        repo = self.make_repo()
        proc = run([
            str(ROOT / 'scripts/new-task'), '--repo', str(repo), '--contract',
            'JIRA-3', 'Task without source'
        ], ROOT, check=False)
        self.assertNotEqual(proc.returncode, 0)
        self.assertFalse((repo / '.agentic/tasks/JIRA-3.md').exists())

        non_git = Path(tempfile.mkdtemp()) / 'plain-dir'
        non_git.mkdir()
        proc = run([
            str(ROOT / 'scripts/new-task'), '--repo', str(non_git), '--contract',
            '--source', 'JIRA-4', 'JIRA-4', 'Task'
        ], ROOT, check=False)
        self.assertNotEqual(proc.returncode, 0)
        self.assertFalse((non_git / '.agentic/tasks/JIRA-4.md').exists())

    def test_new_task_rejects_dangling_output_symlink(self):
        repo = self.make_repo()
        task_dir = repo / '.agentic/tasks'
        task_dir.mkdir(parents=True)
        outside = repo.parent / 'outside-contract.md'
        link = task_dir / 'JIRA-5.md'
        link.symlink_to(outside)
        proc = run([
            str(ROOT / 'scripts/new-task'), '--repo', str(repo), '--contract',
            '--source', 'JIRA-5', 'JIRA-5', 'Task'
        ], ROOT, check=False)
        self.assertNotEqual(proc.returncode, 0)
        self.assertFalse(outside.exists())

    def test_adoption_doctor_treats_wrong_scalar_types_as_invalid(self):
        repo = self.make_repo()
        config = {
            'schema_version': 1,
            'mode': 'adoption',
            'stage': 'minimum-context',
            'source_of_truth_precedence': ['repository_instructions', 'current_task_contract'],
            'sources': {
                'instructions': {'primary': 123, 'also_read': []},
                'tasks': {'kind': ['external'], 'reference': 42, 'local_contract_dir': 7},
            },
            'verification': {
                'check': {'status': 'configured', 'command': './scripts/check.sh'},
                'test': {'status': 'configured', 'command': './scripts/test.sh'},
            },
            'unresolved_conflicts': [],
            'open_questions': [],
        }
        (repo / '.agentic-repository.json').write_text(json.dumps(config, indent=2), encoding='utf-8')
        proc = run([str(ROOT / 'scripts/repo-doctor'), '--adoption', '--repo', str(repo)], ROOT, check=False)
        self.assertEqual(proc.returncode, 1)
        self.assertIn('sources.instructions.primary must be a string', proc.stdout)
        self.assertIn('sources.tasks.kind must be a string', proc.stdout)
        self.assertIn('sources.tasks.reference must be a string', proc.stdout)
        self.assertIn('sources.tasks.local_contract_dir must be a string', proc.stdout)

    def test_adoption_doctor_validates_present_lower_stage_capability_schema(self):
        repo = self.make_repo()
        config = {
            'schema_version': 1,
            'mode': 'adoption',
            'stage': 'minimum-context',
            'source_of_truth_precedence': ['repository_instructions', 'current_task_contract'],
            'sources': {
                'instructions': {'primary': 'CONTRIBUTING.md', 'also_read': []},
                'tasks': {'kind': 'markdown-backlog', 'reference': 'BACKLOG.md', 'local_contract_dir': '.agentic/tasks'},
            },
            'verification': {
                'check': {'status': 'configured', 'command': './scripts/check.sh'},
                'test': {'status': 'configured', 'command': './scripts/test.sh'},
            },
            'capabilities': {
                'repeatable_workflow': {
                    'task_contract': 'configured'
                }
            },
            'unresolved_conflicts': [],
            'open_questions': [],
        }
        (repo / '.agentic-repository.json').write_text(json.dumps(config, indent=2), encoding='utf-8')
        proc = run([str(ROOT / 'scripts/repo-doctor'), '--adoption', '--repo', str(repo)], ROOT, check=False)
        self.assertEqual(proc.returncode, 1)
        self.assertIn('capabilities.repeatable_workflow.task_contract must be an object', proc.stdout)


    def test_placeholder_policy_rejects_natural_variants_but_allows_tracker_ids(self):
        for value in ('TODO later', 'TBD later', 'unknown yet', 'not specified yet', 'not set yet', 'replace this'):
            self.assertTrue(repo_doctor_module.is_placeholder(value), value)
            self.assertTrue(new_task_module.is_placeholder(value), value)
        self.assertFalse(repo_doctor_module.is_placeholder('TODO-123'))
        self.assertFalse(new_task_module.is_placeholder('TODO-123'))

        repo = self.make_repo()
        rejected = run([
            str(ROOT / 'scripts/new-task'), '--repo', str(repo), '--contract',
            '--source', 'TODO later', 'TASK-1', 'Task'
        ], ROOT, check=False)
        self.assertNotEqual(rejected.returncode, 0)

        accepted = run([
            str(ROOT / 'scripts/new-task'), '--repo', str(repo), '--contract',
            '--source', 'TODO-123', 'TASK-2', 'Task'
        ], ROOT)
        self.assertIn('.agentic/tasks/TASK-2.md', accepted.stdout)

    def test_adoption_doctor_rejects_self_asserted_capability_references(self):
        repo = self.make_repo()
        contract = repo / '.agentic/tasks/LEGACY-17.md'
        contract.parent.mkdir(parents=True)
        contract.write_text('# LEGACY-17\n', encoding='utf-8')
        bad_ref = {'status': 'configured', 'reference': 'project risk policy'}
        bad_id = {'status': 'configured', 'reference': {'type': 'external_id', 'value': 'yes'}}
        config = {
            'schema_version': 1,
            'mode': 'adoption',
            'stage': 'repeatable-workflow',
            'source_of_truth_precedence': ['repository_instructions', 'current_task_contract'],
            'sources': {
                'instructions': {'primary': 'CONTRIBUTING.md', 'also_read': []},
                'tasks': {'kind': 'markdown-backlog', 'reference': 'BACKLOG.md', 'local_contract_dir': '.agentic/tasks'},
            },
            'verification': {
                'check': {'status': 'configured', 'command': './scripts/check.sh'},
                'test': {'status': 'configured', 'command': './scripts/test.sh'},
            },
            'capabilities': {
                'repeatable_workflow': {
                    'task_contract': bad_ref,
                    'acceptance_criteria': bad_id,
                    'evidence': {'status': 'configured', 'reference': {'type': 'command', 'value': 'make deploy'}},
                    'definition_of_done': {'status': 'configured', 'reference': {'type': 'path', 'value': 'GOVERNANCE.md#definition-of-done'}},
                }
            },
            'unresolved_conflicts': [],
            'open_questions': [],
        }
        (repo / '.agentic-repository.json').write_text(json.dumps(config, indent=2), encoding='utf-8')
        proc = run([str(ROOT / 'scripts/repo-doctor'), '--adoption', '--repo', str(repo)], ROOT, check=False)
        self.assertEqual(proc.returncode, 1)
        self.assertIn('reference must be an object with type/value', proc.stdout)
        self.assertIn('not an identifiable external ID', proc.stdout)
        self.assertIn('must match a configured verification command', proc.stdout)

    def test_adoption_config_must_not_be_external_symlink(self):
        repo = self.make_repo()
        outside = repo.parent / 'valid-adoption.json'
        outside.write_text(json.dumps({
            'schema_version': 1,
            'mode': 'adoption',
            'stage': 'minimum-context',
            'source_of_truth_precedence': ['repository_instructions', 'current_task_contract'],
            'sources': {
                'instructions': {'primary': 'CONTRIBUTING.md', 'also_read': []},
                'tasks': {'kind': 'markdown-backlog', 'reference': 'BACKLOG.md', 'local_contract_dir': '.agentic/tasks'},
            },
            'verification': {
                'check': {'status': 'configured', 'command': './scripts/check.sh'},
                'test': {'status': 'configured', 'command': './scripts/test.sh'},
            },
            'unresolved_conflicts': [],
            'open_questions': [],
        }), encoding='utf-8')
        (repo / '.agentic-repository.json').symlink_to(outside)
        proc = run([str(ROOT / 'scripts/repo-doctor'), '--adoption', '--repo', str(repo)], ROOT, check=False)
        self.assertEqual(proc.returncode, 1)
        self.assertIn('must be a repository-local regular file', proc.stdout)

    def test_local_task_reference_cannot_escape_repository(self):
        repo = self.make_repo()
        outside = repo.parent / 'outside-backlog.md'
        outside.write_text('# outside\n', encoding='utf-8')
        config = {
            'schema_version': 1,
            'mode': 'adoption',
            'stage': 'minimum-context',
            'source_of_truth_precedence': ['repository_instructions', 'current_task_contract'],
            'sources': {
                'instructions': {'primary': 'CONTRIBUTING.md', 'also_read': []},
                'tasks': {'kind': 'markdown-backlog', 'reference': '../outside-backlog.md#TASK-1', 'local_contract_dir': '.agentic/tasks'},
            },
            'verification': {
                'check': {'status': 'configured', 'command': './scripts/check.sh'},
                'test': {'status': 'configured', 'command': './scripts/test.sh'},
            },
            'unresolved_conflicts': [],
            'open_questions': [],
        }
        (repo / '.agentic-repository.json').write_text(json.dumps(config, indent=2), encoding='utf-8')
        proc = run([str(ROOT / 'scripts/repo-doctor'), '--adoption', '--repo', str(repo)], ROOT, check=False)
        self.assertEqual(proc.returncode, 1)
        self.assertIn('must be repository-relative without ..', proc.stdout)

        (repo / 'backlog-link.md').symlink_to(outside)
        config['sources']['tasks']['reference'] = 'backlog-link.md#TASK-1'
        (repo / '.agentic-repository.json').write_text(json.dumps(config, indent=2), encoding='utf-8')
        proc = run([str(ROOT / 'scripts/repo-doctor'), '--adoption', '--repo', str(repo)], ROOT, check=False)
        self.assertEqual(proc.returncode, 1)
        self.assertIn('escapes repository', proc.stdout)

    def test_new_task_dirfd_creation_does_not_follow_swapped_parent_symlink(self):
        repo = self.make_repo()
        output_fd = new_task_module.open_output_dir_fd(repo, Path('.agentic/tasks'))
        original = repo / '.agentic/tasks'
        renamed = repo / '.agentic/tasks-original'
        original.rename(renamed)
        outside = repo.parent / 'outside-task-dir'
        outside.mkdir()
        original.symlink_to(outside, target_is_directory=True)
        try:
            new_task_module.exclusive_write_at(output_fd, 'RACE.md', 'safe\n')
        finally:
            os.close(output_fd)
        self.assertEqual((renamed / 'RACE.md').read_text(encoding='utf-8'), 'safe\n')
        self.assertFalse((outside / 'RACE.md').exists())



    def test_typed_url_evidence_rejects_malformed_host_and_port(self):
        repo = self.make_repo()
        commands = {'./scripts/check.sh'}
        for value in (
            'https://exa mple.com',
            'https://example.com:bad',
            'https://user:pass@example.com/evidence',
            'https://localhost/evidence',
        ):
            ok, _ = repo_doctor_module.validate_evidence_reference(
                repo,
                {'type': 'url', 'value': value},
                'capabilities.risk_aware.risk_model',
                commands,
            )
            self.assertFalse(ok, value)

        for value in (
            'https://example.com/evidence',
            'https://example.com:8443/evidence',
            'https://127.0.0.1/evidence',
        ):
            ok, reason = repo_doctor_module.validate_evidence_reference(
                repo,
                {'type': 'url', 'value': value},
                'capabilities.risk_aware.risk_model',
                commands,
            )
            self.assertTrue(ok, reason)

    def test_evidence_path_and_local_task_source_require_regular_files(self):
        repo = self.make_repo()
        ok, reason = repo_doctor_module.validate_evidence_reference(
            repo,
            {'type': 'path', 'value': '.'},
            'capabilities.repeatable_workflow.evidence',
            {'./scripts/check.sh'},
        )
        self.assertFalse(ok)
        self.assertIn('regular file', reason)

        config = {
            'schema_version': 1,
            'mode': 'adoption',
            'stage': 'minimum-context',
            'source_of_truth_precedence': ['repository_instructions', 'current_task_contract'],
            'sources': {
                'instructions': {'primary': 'CONTRIBUTING.md', 'also_read': []},
                'tasks': {'kind': 'markdown-backlog', 'reference': '.', 'local_contract_dir': '.agentic/tasks'},
            },
            'verification': {
                'check': {'status': 'configured', 'command': './scripts/check.sh'},
                'test': {'status': 'configured', 'command': './scripts/test.sh'},
            },
            'unresolved_conflicts': [],
            'open_questions': [],
        }
        (repo / '.agentic-repository.json').write_text(json.dumps(config, indent=2), encoding='utf-8')
        proc = run([str(ROOT / 'scripts/repo-doctor'), '--adoption', '--repo', str(repo)], ROOT, check=False)
        self.assertEqual(proc.returncode, 1)
        self.assertIn('regular file', proc.stdout)

        config['sources']['tasks']['reference'] = 'BACKLOG.md#LEGACY-17'
        (repo / '.agentic-repository.json').write_text(json.dumps(config, indent=2), encoding='utf-8')
        proc = run([str(ROOT / 'scripts/repo-doctor'), '--adoption', '--repo', str(repo)], ROOT)
        self.assertIn('[EXISTING_EQUIVALENT] local task source: BACKLOG.md#LEGACY-17', proc.stdout)

    def test_new_task_requires_identifiable_source_semantics(self):
        repo = self.make_repo()
        for source in ('yes', 'project risk policy', 'https://exa mple.com', 'https://example.com:bad'):
            proc = run([
                str(ROOT / 'scripts/new-task'), '--repo', str(repo), '--contract',
                '--source', source, 'TASK-X', 'Task'
            ], ROOT, check=False)
            self.assertNotEqual(proc.returncode, 0, source)

        accepted = [
            ('JIRA-1842', 'TASK-JIRA'),
            ('https://example.com/issues/1842', 'TASK-URL'),
            ('BACKLOG.md#LEGACY-17', 'TASK-LOCAL'),
        ]
        for source, task_id in accepted:
            proc = run([
                str(ROOT / 'scripts/new-task'), '--repo', str(repo), '--contract',
                '--source', source, task_id, 'Task'
            ], ROOT)
            self.assertIn(f'.agentic/tasks/{task_id}.md', proc.stdout)

    def test_new_task_rejects_missing_local_source_file(self):
        repo = self.make_repo()
        proc = run([
            str(ROOT / 'scripts/new-task'), '--repo', str(repo), '--contract',
            '--source', 'MISSING.md#TASK-1', 'TASK-MISSING', 'Task'
        ], ROOT, check=False)
        self.assertNotEqual(proc.returncode, 0)
        self.assertFalse((repo / '.agentic/tasks/TASK-MISSING.md').exists())

    def test_brownfield_example_uses_stdout_redirection_for_audit(self):
        example = (ROOT / 'docs/examples/first-brownfield-cycle.md').read_text(encoding='utf-8')
        self.assertNotIn('repo-audit --repo . --output', example)
        self.assertIn('repo-audit --repo . > /tmp/audit.md', example)


    def test_http_looking_values_never_fall_back_to_external_id(self):
        malformed = (
            'https://example.com:bad',
            'https://example.com:99999',
            'https://-bad.example/path',
            'https://bad-.example/path',
            'https://exa_mple.com/path',
        )
        for value in malformed:
            self.assertFalse(repo_doctor_module.is_valid_http_url(value), value)
            self.assertFalse(repo_doctor_module.is_identifiable_external_reference(value), value)

        repo = self.make_repo()
        for value in malformed:
            ok, _ = repo_doctor_module.validate_evidence_reference(
                repo,
                {'type': 'external_id', 'value': value},
                'capabilities.risk_aware.risk_model',
                {'./scripts/check.sh'},
            )
            self.assertFalse(ok, value)

    def test_strict_url_rejects_unicode_space_control_format_and_post_idna_overflow(self):
        overlong_idna_host = '.'.join(['ä' * 57] * 4)
        malformed = (
            'https://example.com/\u0085evidence',
            'https://example.com/\u2028evidence',
            'https://example.com/\u00a0evidence',
            'https://exa\u200bmple.com/evidence',
            f'https://{overlong_idna_host}/evidence',
        )
        for value in malformed:
            self.assertFalse(repo_doctor_module.is_valid_http_url(value), repr(value))
            self.assertFalse(new_task_module.is_valid_http_url(value), repr(value))

    def test_non_local_task_source_rejects_malformed_http_fallback(self):
        repo = self.make_repo()
        config = {
            'schema_version': 1,
            'mode': 'adoption',
            'stage': 'minimum-context',
            'source_of_truth_precedence': ['repository_instructions', 'current_task_contract'],
            'sources': {
                'instructions': {'primary': 'CONTRIBUTING.md', 'also_read': []},
                'tasks': {
                    'kind': 'external',
                    'reference': 'https://example.com:bad',
                    'local_contract_dir': '.agentic/tasks',
                },
            },
            'verification': {
                'check': {'status': 'configured', 'command': './scripts/check.sh'},
                'test': {'status': 'configured', 'command': './scripts/test.sh'},
            },
            'unresolved_conflicts': [],
            'open_questions': [],
        }
        (repo / '.agentic-repository.json').write_text(json.dumps(config, indent=2), encoding='utf-8')
        proc = run([str(ROOT / 'scripts/repo-doctor'), '--adoption', '--repo', str(repo)], ROOT, check=False)
        self.assertEqual(proc.returncode, 1)
        self.assertIn('concrete URL/external ID', proc.stdout)

    def test_new_task_rejects_malformed_http_fallback_and_outer_whitespace(self):
        repo = self.make_repo()
        rejected = (
            'https://example.com:bad',
            'https://example.com:99999',
            'https://exa_mple.com/path',
            ' JIRA-1842 ',
            ' https://example.com/issues/1842 ',
        )
        for index, source in enumerate(rejected):
            proc = run([
                str(ROOT / 'scripts/new-task'), '--repo', str(repo), '--contract',
                '--source', source, f'TASK-R{index}', 'Task'
            ], ROOT, check=False)
            self.assertNotEqual(proc.returncode, 0, repr(source))



    def test_strict_url_percent_encoding(self):
        invalid = (
            'https://example.com/%',
            'https://example.com/%0G',
            'https://example.com/%GG',
            'https://example.com/%Z1',
        )
        valid = (
            'https://example.com/%20',
            'https://example.com/%2F',
            'https://example.com/%25',
        )
        for value in invalid:
            self.assertFalse(repo_doctor_module.is_valid_http_url(value), value)
            self.assertFalse(repo_doctor_module.is_identifiable_external_reference(value), value)
            self.assertFalse(new_task_module.is_valid_http_url(value), value)
        for value in valid:
            self.assertTrue(repo_doctor_module.is_valid_http_url(value), value)
            self.assertTrue(new_task_module.is_valid_http_url(value), value)

    def test_risk_aware_doctor_rejects_malformed_percent_url_evidence(self):
        repo = self.make_repo()
        contract = repo / '.agentic/tasks/LEGACY-17.md'
        contract.parent.mkdir(parents=True)
        contract.write_text('# LEGACY-17\n## Acceptance Criteria\n## Evidence\n', encoding='utf-8')
        configured = lambda ref_type, value: {
            'status': 'configured',
            'reference': {'type': ref_type, 'value': value},
        }
        config = {
            'schema_version': 1,
            'mode': 'adoption',
            'stage': 'risk-aware',
            'source_of_truth_precedence': ['repository_instructions', 'current_task_contract'],
            'sources': {
                'instructions': {'primary': 'CONTRIBUTING.md', 'also_read': ['CLAUDE.md']},
                'architecture': {'status': 'partial', 'paths': ['README.md']},
                'decisions': {'kind': 'none', 'paths': []},
                'tasks': {'kind': 'markdown-backlog', 'reference': 'BACKLOG.md', 'local_contract_dir': '.agentic/tasks'},
                'ci': {'status': 'existing', 'paths': ['.github/workflows/build.yml']},
            },
            'verification': {
                'check': {'status': 'configured', 'command': './scripts/check.sh'},
                'test': {'status': 'configured', 'command': './scripts/test.sh'},
                'integration': {'status': 'not_applicable', 'reason': 'fixture has no integration boundary'},
            },
            'capabilities': {
                'repeatable_workflow': {
                    'task_contract': configured('path', '.agentic/tasks/LEGACY-17.md'),
                    'acceptance_criteria': configured('path', '.agentic/tasks/LEGACY-17.md#acceptance-criteria'),
                    'evidence': configured('url', 'https://example.com/%ZZ'),
                    'definition_of_done': configured('path', 'GOVERNANCE.md#definition-of-done'),
                },
                'independent_verification': {
                    'review_mechanism': configured('path', 'GOVERNANCE.md#independent-review'),
                    'exact_sha_diff_evidence': configured('path', 'GOVERNANCE.md#independent-review'),
                    'ci_pr_linkage': configured('path', '.github/workflows/build.yml'),
                },
                'risk_aware': {
                    'risk_model': configured('path', 'GOVERNANCE.md#risk-model'),
                    'high_risk_gates': configured('path', 'GOVERNANCE.md#risk-model'),
                    'adversarial_review': configured('path', 'GOVERNANCE.md#adversarial-review'),
                    'technical_enforcement': configured('path', '.github/workflows/build.yml'),
                },
            },
            'unresolved_conflicts': [],
            'open_questions': [],
        }
        (repo / '.agentic-repository.json').write_text(json.dumps(config, indent=2), encoding='utf-8')
        proc = run([str(ROOT / 'scripts/repo-doctor'), '--adoption', '--repo', str(repo)], ROOT, check=False)
        self.assertEqual(proc.returncode, 1)
        self.assertIn('valid absolute http(s) URL', proc.stdout)

    def test_new_task_accepts_slash_compact_ids_without_treating_them_as_files(self):
        repo = self.make_repo()
        accepted = (
            ('owner/repo#123', 'TASK-SLASH-1'),
            ('PROJ/team-123', 'TASK-SLASH-2'),
        )
        for source, task_id in accepted:
            proc = run([
                str(ROOT / 'scripts/new-task'), '--repo', str(repo), '--contract',
                '--source', source, task_id, 'Task'
            ], ROOT)
            self.assertIn(f'.agentic/tasks/{task_id}.md', proc.stdout)
            content = (repo / f'.agentic/tasks/{task_id}.md').read_text(encoding='utf-8')
            self.assertIn(source, content)

        missing_local = run([
            str(ROOT / 'scripts/new-task'), '--repo', str(repo), '--contract',
            '--source', 'MISSING.md#TASK-1', 'TASK-MISSING-LOCAL', 'Task'
        ], ROOT, check=False)
        self.assertNotEqual(missing_local.returncode, 0)

    def test_new_task_rejects_malformed_percent_url_source(self):
        repo = self.make_repo()
        for index, source in enumerate((
            'https://example.com/%',
            'https://example.com/%0G',
            'https://example.com/%GG',
            'https://example.com/%Z1',
        )):
            proc = run([
                str(ROOT / 'scripts/new-task'), '--repo', str(repo), '--contract',
                '--source', source, f'TASK-PCT-{index}', 'Task'
            ], ROOT, check=False)
            self.assertNotEqual(proc.returncode, 0, source)


    def test_adoption_doctor_reports_not_configured_without_calling_repo_broken(self):
        repo = self.make_repo()
        proc = run([str(ROOT / 'scripts/repo-doctor'), '--adoption', '--repo', str(repo)], ROOT, check=False)
        self.assertEqual(proc.returncode, 2)
        self.assertIn('[NOT_CONFIGURED]', proc.stdout)
        self.assertIn('not broken', proc.stdout)


if __name__ == '__main__':
    unittest.main()
