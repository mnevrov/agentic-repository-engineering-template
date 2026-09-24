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
        configured = lambda reference: {'status': 'configured', 'reference': reference}
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
                    'task_contract': configured('.agentic/tasks'),
                    'acceptance_criteria': configured('execution contract AC section'),
                    'evidence': configured('execution contract evidence section'),
                    'definition_of_done': configured('CONTRIBUTING.md'),
                },
                'independent_verification': {
                    'review_mechanism': configured('GitHub pull-request review'),
                    'exact_sha_diff_evidence': configured('review requires exact SHA/diff'),
                    'ci_pr_linkage': configured('.github/workflows/build.yml'),
                },
                'risk_aware': {
                    'risk_model': configured('project risk policy'),
                    'high_risk_gates': configured('project risk policy'),
                    'adversarial_review': configured('project risk policy'),
                    'technical_enforcement': configured('.github/workflows/build.yml'),
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
                'tasks': {'kind': 'external', 'reference': 'not specified', 'local_contract_dir': '.agentic/tasks'},
            },
            'verification': {
                'check': {'status': 'configured', 'command': 'TODO'},
                'test': {'status': 'configured', 'command': './scripts/test.sh'},
                'integration': {'status': 'not_applicable', 'reason': 'TODO'},
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

    def test_adoption_doctor_reports_not_configured_without_calling_repo_broken(self):
        repo = self.make_repo()
        proc = run([str(ROOT / 'scripts/repo-doctor'), '--adoption', '--repo', str(repo)], ROOT, check=False)
        self.assertEqual(proc.returncode, 2)
        self.assertIn('[NOT_CONFIGURED]', proc.stdout)
        self.assertIn('not broken', proc.stdout)


if __name__ == '__main__':
    unittest.main()
