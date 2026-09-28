# TEMPLATE-5 — Сверить post-merge evidence TEMPLATE-4

**Статус:** done\
**Риск:** A\
**Human gate:** required — подтверждён владельцем repository 2026-09-28 («приступай по плану»)\
**Владелец:** repository owner\
**Связанный эпик/этап:** M0 — закрытие brownfield adoption\
**Requirements / ADR:** `docs/tasks/TEMPLATE-4.md`; ADR n/a

## Зачем

После merge PR #5 локальный Task и review artifact не отражали конечное состояние проверки. Нужно связать точные GitHub CI SHA с merge, получить независимый clean-context review и определить, закрыта ли TEMPLATE-4 или требует ограниченной доработки.

## Объём

### Входит

- зафиксировать локальную проверку полного merge-коммита `ae1e4a6b838c4fce518d6285d327c19b923f49b0`;
- получить независимый clean-context review точного merge-коммита TEMPLATE-4;
- записать найденные review gaps отдельной следующей Task, не расширяя этот цикл исправлением кода.

### Не входит

- повторная реализация или изменение brownfield tooling;
- утверждение внешнего reviewer без доступного evidence;
- исправление отдельной ссылки `@RTK.md` в пользовательских инструкциях.

## Критерии приёмки

- [x] AC-1: TEMPLATE-4 содержит PR-head CI и post-merge CI с точными SHA, run IDs и ссылками.
- [x] AC-2: CodeRabbit `SUCCESS` отмечен как пропуск review, а не независимый verdict.
- [x] AC-3: TODO и Task contract содержат одну ближайшую bounded задачу по блокирующему finding review.
- [x] AC-4: независимый clean-context review merge-коммита TEMPLATE-4 сохранён в `docs/reviews/TEMPLATE-4-final-review.md`.
- [x] AC-5: независимый clean-context review этого документационного diff сохранён в `docs/reviews/TEMPLATE-5-review.md` с verdict `approved`.
- [x] AC-6: запись попытки цикла добавлена в telemetry и проходит её валидатор.

## Архитектурные ограничения

- Не менять код и проектные gate-команды.
- Не считать merge или локальные проверки доказательством удалённого CI/review.
- Не редактировать предыдущие записи telemetry.

## План проверки

- Удалённый CI: GitHub Actions `doctor` на PR head `d6d93fabd42c3c0d8b0124b7b40d54736f85fbd8` и push SHA `ae1e4a6b838c4fce518d6285d327c19b923f49b0`.
- Локально: `./scripts/repo-doctor --template`, `make test-template`, `python3 scripts/validate-telemetry.py`.
- После изменения: повторить `./scripts/repo-doctor --template`, `make test-template` и `python3 scripts/validate-telemetry.py`.
- Независимая clean-context проверка документационного diff.
- Ожидаемый evidence level: E2 для template tests; doctor и telemetry validation дают дополнительную локальную проверку. GitHub Actions подтверждает выполнение CI на указанных SHA, но сам по себе не повышает уровень до E3/E4. Independent review — отдельный DoD gate, не evidence level.

## Доказательства

- Команды: `./scripts/repo-doctor --template` — exit 0; `make test-template` — 59 тестов, OK; `python3 scripts/validate-telemetry.py` — 23 записи валидны, включая partial и passed циклы TEMPLATE-5.
- Проверенный SHA: `ae1e4a6b838c4fce518d6285d327c19b923f49b0`.
- PR run `36228392844` на `d6d93fabd42c3c0d8b0124b7b40d54736f85fbd8`: workflow conclusion `success`; run metadata подтверждает exact PR head.
- Post-merge run `36229039503` на `ae1e4a6b838c4fce518d6285d327c19b923f49b0`: success.
- PR status `CodeRabbit: SUCCESS` сообщает `Review skipped: manual review required for this OSS repository`; это не является review verdict.
- Источники: [PR #5](https://github.com/mnevrov/agentic-repository-engineering-template/pull/5), [PR-head Actions](https://github.com/mnevrov/agentic-repository-engineering-template/actions/runs/36228392844), [post-merge Actions](https://github.com/mnevrov/agentic-repository-engineering-template/actions/runs/36229039503).
- Фактический evidence level: E2 по template tests; эти тесты прошли локально и в PR CI. Отдельных integration/live evidence E3+ нет.

## Review

- Self-review: выполнен; scope ограничен сверкой CI/review evidence и подготовкой следующего task contract.
- Independent review artifact: `docs/reviews/TEMPLATE-5-review.md`, verdict `approved`, 0 open findings.
- Остаточные замечания: final review TEMPLATE-4 нашёл P2 по symlinked Makefile; кодовая доработка ожидает Human Gate в TEMPLATE-6. В review TEMPLATE-5 закрываются два документационных замечания.

## Traceability

- `TEMPLATE-4` → `TEMPLATE-5` → CI runs и `TEMPLATE-4-final-review.md` → `TEMPLATE-6`.
- Task → commit/PR: локальный документальный цикл, коммит не создавался.
