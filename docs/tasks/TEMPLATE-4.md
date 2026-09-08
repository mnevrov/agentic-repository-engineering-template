# TEMPLATE-4 — Harden downstream bootstrap after real dry-run

**Статус:** in progress  
**Риск:** B  
**Human gate:** required — подтверждён владельцем репозитория 2026-09-08  
**Владелец:** repository owner  
**Связанный эпик/этап:** downstream onboarding / template hardening  
**Requirements / ADR:** `docs/workshop/real-repository-dry-run.md`

## Зачем

Полный dry-run на отдельном demo repository выявил проблемы reusable template, которые не были видны при проверке только source repository. Нужно устранить их так, чтобы новый downstream начинал с чистой project memory и честных fail-closed gates.

## Подтверждённые проблемы

- product tests и template tooling tests были смешаны;
- source-only placeholder contract наследовался downstream;
- пустой test discovery мог вернуть exit 0;
- часть gates не была защищена от zero-work PASS;
- downstream наследовал `TEMPLATE-*` Tasks и telemetry source repository;
- TODO state и Task status могли расходиться;
- runbook преждевременно делал integration discovery зелёным до появления настоящего integration test;
- dry-run успешно работал на Python 3.10, поэтому 3.11+ не подтверждено как обязательное требование.

## Объём

### Входит

- отделить `template_tests/` от product `tests/`;
- source-only placeholder contract проверять только source CI;
- добавить fail-closed guards reusable tooling;
- добавить `scripts/init-project` для downstream initialization;
- при initialization очистить source Tasks/telemetry/template-only artifacts;
- создать bootstrap Task и честные project placeholders;
- проверять TODO state ↔ Task status;
- обновить README, onboarding и dry-run runbook;
- оставить integration gate fail-closed до настоящего integration test;
- добавить regression tests initializer и task-state consistency.

### Не входит

- изменение risk model;
- изменение independent review policy;
- новый orchestration runtime;
- изменение продуктового demo приложения.

## Критерии приёмки

- [ ] AC-1: `make test-template` запускает только `template_tests/` и fail-closed при отсутствии tests.
- [ ] AC-2: `scripts/init-project` удаляет source Tasks/telemetry из downstream, не затрагивая unrelated Tasks.
- [ ] AC-3: initializer защищён от случайного повторного запуска.
- [ ] AC-4: initializer создаёт bootstrap Task, TODO Ready и честные project placeholders.
- [ ] AC-5: `repo-doctor` ловит рассинхрон TODO state ↔ Task status.
- [ ] AC-6: runbook не содержит zero-work project/integration test discovery.
- [ ] AC-7: до DEMO-3 integration gate остаётся `NOT CONFIGURED`.
- [ ] AC-8: onboarding явно требует `scripts/init-project` после создания downstream.
- [ ] AC-9: source CI продолжает проверять placeholders `check/test/test-integration`.
- [ ] AC-10: template tooling regression tests проходят.
- [ ] AC-11: CI проходит.
- [ ] AC-12: independent clean-context review не имеет нерешённых P0/P1.

## Архитектурные ограничения

- Git остаётся источником истины;
- initialization детерминирована;
- повторный destructive запуск требует `--force`;
- `NOT CONFIGURED` не считается PASS;
- фиктивные tests ради зелёного gate запрещены.

## План проверки

- `./scripts/repo-doctor`;
- `make test-template`;
- `make telemetry-check`;
- regression tests initializer/task-state;
- GitHub Actions CI;
- independent clean-context review;
- ожидаемый evidence level: E3.

## Доказательства

Заполняется после выполнения.

## Review

- self-review:
- independent review artifact: `docs/reviews/TEMPLATE-4-review.md`
- остаточные замечания:

## Traceability

- real dry-run findings → TEMPLATE-4;
- task → evidence:
- task → commits/PR:
