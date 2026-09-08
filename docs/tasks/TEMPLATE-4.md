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
- dry-run успешно работал на Python 3.10, поэтому 3.11+ не подтверждено как обязательное требование;
- CI hardening выявил historical telemetry row, случайно изменённую при раннем переносе tests; append-only history восстановлена, а checker теперь диагностирует конкретную row/fields при mismatch.

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
- добавить regression tests initializer и task-state consistency;
- сохранить строгую append-only telemetry semantics и улучшить диагностику mismatch.

### Не входит

- изменение risk model;
- изменение independent review policy;
- новый orchestration runtime;
- изменение продуктового demo приложения.

## Критерии приёмки

- [x] AC-1: `make test-template` запускает только `template_tests/` и fail-closed при отсутствии tests.
- [x] AC-2: `scripts/init-project` удаляет source Tasks/telemetry из downstream, не затрагивая unrelated Tasks.
- [x] AC-3: initializer защищён от случайного повторного запуска.
- [x] AC-4: initializer создаёт bootstrap Task, TODO Ready и честные project placeholders.
- [x] AC-5: `repo-doctor` ловит рассинхрон TODO state ↔ Task status.
- [x] AC-6: runbook не содержит zero-work project/integration test discovery.
- [x] AC-7: до DEMO-3 integration gate остаётся `NOT CONFIGURED`.
- [x] AC-8: onboarding явно требует `scripts/init-project` после создания downstream.
- [x] AC-9: source CI продолжает проверять placeholders `check/test/test-integration`.
- [x] AC-10: template tooling regression tests проходят.
- [x] AC-11: CI проходит.
- [ ] AC-12: independent clean-context review не имеет нерешённых P0/P1.

## Архитектурные ограничения

- Git остаётся источником истины;
- initialization детерминирована;
- повторный destructive запуск требует `--force`;
- `NOT CONFIGURED` не считается PASS;
- фиктивные tests ради зелёного gate запрещены;
- historical telemetry rows immutable по содержимому и порядку.

## План проверки

- `./scripts/repo-doctor`;
- `make test-template`;
- `make telemetry-check`;
- regression tests initializer/task-state;
- GitHub Actions CI;
- independent clean-context review;
- ожидаемый evidence level: E3.

## Доказательства

- GitHub Actions: run `34224444271`, conclusion `success` на head `0ef76c7436bdb5a14ba594a8ed8b1e52f7de5383`.
- `./scripts/repo-doctor`: PASS, включая TODO/Task status consistency.
- `python3 scripts/validate-telemetry.py`: PASS, 6 source cycles.
- append-only contract: `preserved 5 existing row(s), appended 1`.
- telemetry-required contract: `1 row(s) appended for 18 substantive changed file(s)`.
- `make test-template`: 12 tests, PASS.
- source `make check`: expected `NOT CONFIGURED`, exit 2.
- source `make test`: expected `NOT CONFIGURED`, exit 2.
- source `make test-integration`: expected `NOT CONFIGURED`, exit 2.
- initializer mode: `scripts/init-project` исправлен на executable `100755` после отдельной проверки Git tree; повторный CI на этом head PASS.
- initial CI failures по telemetry append-only не скрыты workaround'ом: восстановлен historical `TEMPLATE-1.changed_files`, потерянный в ранней ветке; guard сохранён строгим и теперь сообщает конкретную row/fields.
- фактический evidence level до independent review: E3 (regression tooling tests + GitHub Actions integration).
- что не проверено: independent clean-context review текущего финального HEAD.

## Review

- self-review: dry-run findings сопоставлены с implementation/docs; CI проверил initializer regression suite, task-state consistency, telemetry contracts и source fail-closed placeholders.
- independent review artifact: `docs/reviews/TEMPLATE-4-review.md`
- остаточные замечания: independent review pending.

## Traceability

- real dry-run findings → TEMPLATE-4;
- task → evidence: GitHub Actions run `34224444271` + `template_tests/` + updated onboarding/runbook;
- task → commits/PR: draft PR #4 `fix: harden downstream bootstrap after real dry-run`; reviewed implementation head должен быть зафиксирован после этой evidence update.
