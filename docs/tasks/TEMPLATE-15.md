# TEMPLATE-15 — Remediation of independent release audit findings (issue #9)

**Статус:** done  
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
- [x] AC-4: `make test-template` (144 по финальной remediation), `repo-doctor --template`, `validate-telemetry.py`, `check-task-state.py` PASS.
- [x] AC-5: allow-правила shell без `*` и без операторов; контракт закреплен тестом.
- [x] AC-6: независимый clean-context adversarial review (rounds 1-5, все подтверждённые P0/P1 устранены с регрессиями) сохранен в `docs/reviews/TEMPLATE-15-review.md`; round 6 сжат автором по явному указанию владельца (время) — pre-check атак-поверхностей, residual раскрыт в артефакте.
- [x] AC-7: PR не создавался: владелец указал прямой merge в main. `2043f6d..f0f2a34` смержен fast-forward и запушен по SSH; CI Repository Doctor на `f0f2a34` — success. Tag/RC не тронуты.

## План проверки

- PoC-репродукция до исправления (зафиксирована в `/tmp/opencode/audit-repro2/poc1`) и повторное отклонение после;
- `make test-template` (Git-backed негативные regression tests включены);
- downstream bootstrap smoke локально в точности как шаг CI (включая destructive-repeat и no-origin негатив);
- `make opencode-acceptance` на HOST (v2.2.5);
- CI на точном SHA PR-head.

## Доказательства

- PoC repro/blocked: каталог аудита, вывод обоих gate `False` после исправления.
- Тесты: `template_tests/test_telemetry_cutover.py` (20), `test_opencode_contract.py`, `test_init_project.py`, `test_ci_workflow_permissions.py`.
- CI финальной remediation: [run 42194726094](https://github.com/mnevrov/agentic-repository-engineering-template/actions/runs/42194726094) на `f0f2a344bee0bc391ab341601eae2d1cf566a5e1` — PASS, `doctor` и оба OpenCode v2 config jobs.
- CI после fast-forward main: [run 42195162188](https://github.com/mnevrov/agentic-repository-engineering-template/actions/runs/42195162188) на `a3bf31af89964c7ae3f87eebd62ad38133db5e52` — PASS, те же три jobs.
- Источник предметного анализа: `scripts/telemetry_cutover.py`, оба `check-telemetry-*.py`, `template_tests/test_telemetry_cutover.py`, ADR-0001 и `docs/reviews/TEMPLATE-15-review.md`.
- Решение владельца 2026-11-06: дополнительных adversarial-раундов по TEMPLATE-15 не проводить, remediation принять как завершённую. Оставшийся риск provenance как эвристики описан в ADR-0001.

## Review

- self-review: выполнен по диффу;
- independent review artifact: `docs/reviews/TEMPLATE-15-review.md`
- остаточные замечания: origin identity — эвристика, не удостоверение (ADR-0001); downstream без origin обязан задать origin до bootstrap.

## Traceability

- audit finding → task: `ISSUE9-RELEASE-AUDIT.md` P1-1/P2-1/P2-2/P2-3/P3-1..4 → `TEMPLATE-15`;
- decision: ADR-0001;
- task → evidence: секция «Доказательства»;
- task → commits: `2043f6d` (baseline) → `f0f2a34` (remediation) → `a3bf31a` (AC-7 закрыт, final main CI PASS). PR для remediation не создавался по решению владельца.

## Закрытие (2026-11-06)

**Решение: ACCEPTED / REMEDIATION COMPLETE.** Все семь AC отмечены; 144 теста и Git-backed PoC-батареи подтверждены сохранённым отчётом, final CI на SHA `a3bf31a` PASS. Раунд 6 — документированный author pre-check, а не новая независимая проверка. Дополнительных раундов по этой задаче не требуется.

**Граница:** закрытие TEMPLATE-15 не равно разрешению production release `v0.1.0`: issue #9 остаётся открытым из-за отсутствующей защиты main, отдельного release-review точного SHA и незакрытого integration/e2e gate. Ни release tag, ни RC здесь не изменяются.
