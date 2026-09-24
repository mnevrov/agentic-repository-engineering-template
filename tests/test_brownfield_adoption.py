#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / 'tests/fixtures/brownfield-project'


def run(cmd: list[str], cwd: Path, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, check=check)


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

    def test_adoption_doctor_reports_not_configured_without_calling_repo_broken(self):
        repo = self.make_repo()
        proc = run([str(ROOT / 'scripts/repo-doctor'), '--adoption', '--repo', str(repo)], ROOT, check=False)
        self.assertEqual(proc.returncode, 2)
        self.assertIn('[NOT_CONFIGURED]', proc.stdout)
        self.assertIn('not broken', proc.stdout)


if __name__ == '__main__':
    unittest.main()
