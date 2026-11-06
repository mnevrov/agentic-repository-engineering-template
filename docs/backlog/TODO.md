# TODO — исходный шаблон

Состояния source-template задач. Downstream-проект после `init-project` получает собственный TODO. Раздел `Blocked` проверяется `check-task-state.py`.

## Ready

Нет новых реализационных задач без финального release review.

## In progress

- [ ] TEMPLATE-14 — least-privilege CI and exact SHA release-review evidence.
- [ ] TEMPLATE-13 — стабилизация release-evidence и статусов с тестированием Blocked.

## Blocked

- [ ] TEMPLATE-4 — историческая CI-задолженность по старому SHA; итоговый release review остаётся обязательным.
- [ ] TEMPLATE-8 — bootstrap и разделение тестов реализованы, final release review отсутствует.
- [ ] TEMPLATE-9 — OpenCode v2-only workflow реализован, final release review отсутствует.
- [ ] TEMPLATE-10 — public onboarding реализован, final release review отсутствует.
- [ ] TEMPLATE-11 — HOST discovery пройден по отчёту владельца, final release review отсутствует.
- [ ] TEMPLATE-12 — telemetry cutover пройден в CI/пилоте, final release review отсутствует.

## Done

- [x] TEMPLATE-17 — owner approval, signed-release finalizer and exact-SHA release gates ready; actual release requires admin-scoped GitHub authentication.
- [x] TEMPLATE-16 — подготовка v0.1.0: Pilot E3 CI PASS, ruleset recipe, release notes/playbook; production release остаётся BLOCKED в issue #9.
- [x] TEMPLATE-15 — remediation of release audit telemetry provenance P1/P2/P3; CI `a3bf31a` PASS; release gate #9 separate.
- [x] Создан базовый инженерный каркас репозитория.
- [x] TEMPLATE-5 — сверка GitHub evidence и bounded follow-up.
- [x] TEMPLATE-6 — symlinked Makefile guard + regression/review.
- [x] TEMPLATE-7 — локальный .serena исключён из Git.

`EXAMPLE-1` — только демонстрационный task в source template; `init-project` удаляет его из downstream. Он не является активной задачей самого шаблона.
