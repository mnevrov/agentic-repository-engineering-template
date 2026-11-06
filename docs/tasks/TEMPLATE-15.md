# TEMPLATE-15 — Remediation of independent release audit findings (issue #9)

**Статус:** in progress  
**Риск:** A  
**Human gate:** delegated by owner, 2026-11-05 (remediation of an externally reviewed P1 within the existing stabilization scope; merge/tag/RC mutation explicitly excluded and reserved to the owner).

## Scope

Восстановление результатов independent release audit (`ISSUE9-RELEASE-AUDIT.md`) на SHA `2043f6d1c2262342f81edb296f5d5584a50c5107`:

- P1-1: provenance-bound telemetry cutover (identity + lineage + baseline shape, fail-closed, HEAD-blob marker) — ADR-0001;
- P2-1: удалить wildcard prefix-allow из shell permissions, задокументировать ограничение составных команд;
- P2-2: `init-project` устраняет мёртвые ссылки удалённых template-only файлов из `docs/INDEX.md`;
- P2-3: статус README согласован со STABILIZATION/BLOCKED;
- P3-1…P3-4: дубль `HANDOUT.md`, удаление устаревшего `publish-github-template`, assert отсутствия job-level `permissions:`, явная строковая связка негативного CI-gate.

Не входит: merge, tag/release, изменения `release/v0.1.0-rc.1`, branch protection (остаются gate владельца).

## Acceptance Criteria

- [x] AC-1: PoC аудитора (поддельный маркер + замена `TEMPLATE-*` истории) отклоняется обоими gate в Git-backed тесте, воспроизводящем layout исходного шаблона.
- [x] AC-2: каждый provenance-отказ отдельный: отсутствие origin, локальный/`file://` origin, origin source-template (включая алиасы `/.`, dot-segment, порт, trailing-dot host), одноимённое зеркало, untracked/worktree/symlink-маркер, не-ancestor base, disjoint history, маркер в base/корне, shallow-клон, `url.*.insteadOf`, `--base-ref` с `-`.
- [x] AC-3: первый downstream bootstrap и strict append-only после него работают (позитивные регрессии, merge-with-parallel-rows, downstream smoke с CI-origin, replay реального Pilot `mnevrov/agentic-template` на boundary-коммитах).
- [x] AC-4: `make test-template` (122), `repo-doctor --template`, `validate-telemetry.py`, `check-task-state.py` PASS.
- [x] AC-5: allow-правила shell без `*` и без операторов; контракт закреплен тестом.
- [x] AC-6: независимый clean-context adversarial review (rounds 1-5, все подтверждённые P0/P1 устранены с регрессиями) сохранен в `docs/reviews/TEMPLATE-15-review.md`; round 6 сжат автором по явному указанию владельца (время) — pre-check атак-поверхностей, residual раскрыт в артефакте.
- [ ] AC-7: PR создан; merge/tag/RC — только после подтверждения владельца.

## План проверки

- PoC-репродукция до исправления (зафиксирована в `/tmp/opencode/audit-repro2/poc1`) и повторное отклонение после;
- `make test-template` (Git-backed негативные regression tests включены);
- downstream bootstrap smoke локально в точности как шаг CI (включая destructive-repeat и no-origin негатив);
- `make opencode-acceptance` на HOST (v2.2.5);
- CI на точном SHA PR-head.

## Доказательства

- PoC repro/blocked: каталог аудита, вывод обоих gate `False` после исправления.
- Тесты: `template_tests/test_telemetry_cutover.py` (20), `test_opencode_contract.py`, `test_init_project.py`, `test_ci_workflow_permissions.py`.
- CI run на exact SHA: добавляется после push (pending).

## Review

- self-review: выполнен по диффу;
- independent review artifact: `docs/reviews/TEMPLATE-15-review.md`
- остаточные замечания: origin identity — эвристика, не удостоверение (ADR-0001); downstream без origin обязан задать origin до bootstrap.

## Traceability

- audit finding → task: `ISSUE9-RELEASE-AUDIT.md` P1-1/P2-1/P2-2/P2-3/P3-1..4 → `TEMPLATE-15`;
- decision: ADR-0001;
- task → evidence: секция «Доказательства»;
- task → commit/PR: заполняется после push.
