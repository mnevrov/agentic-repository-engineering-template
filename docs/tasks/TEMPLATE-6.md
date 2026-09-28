# TEMPLATE-6 — Ограничить чтение build-marker symlink в repo-audit

**Статус:** complete\
**Риск:** B\
**Human gate:** подтверждён владельцем repository 2026-09-28 до реализации\
**Владелец:** repository owner\
**Связанный эпик/этап:** M0 — закрытие TEMPLATE-4 / brownfield adoption\
**Requirements / ADR:** `docs/tasks/TEMPLATE-4.md` AC-3; `docs/reviews/TEMPLATE-4-final-review.md`; ADR n/a

## Зачем

Независимый review обнаружил, что `repo-audit` читает `Makefile` через symlink. Если symlink ведёт за пределы аудируемого repository, содержимое внешнего файла влияет на emitted verification candidates. Это нарушает заявленную границу read-only discovery.

## Объём

### Входит

- не читать build-marker файлы, являющиеся symlink, либо доказуемо ограничить чтение путями внутри target repository;
- добавить regression test с внешним `Makefile`-target sentinel и symlink внутри fixture repository;
- сохранить обнаружение обычного repository-local `Makefile`.

### Не входит

- изменение `repo-doctor` или обработка P3 malformed config types;
- автоматический запуск verification candidates, обнаруженных audit;
- изменение общей модели adoption или архитектурных границ.

## Критерии приёмки

- [x] AC-1: внешний target symlinked `Makefile` не читается и его уникальная цель не появляется в audit output.
- [x] AC-2: обычный файл `Makefile` внутри repository по-прежнему даёт ожидаемые verification candidates.
- [x] AC-3: regression test проходит в `make test-template`; project doctor проходит. Telemetry validator выполняется перед закрытием цикла.
- [x] AC-4: exact diff получил independent clean-context review без открытых P0/P1.
- [x] AC-5: telemetry зафиксирована и проходит валидатор.

## Архитектурные ограничения

- Audit остаётся read-only и не раскрывает содержимое файлов вне target repository.
- Candidate detection остаётся advisory и не объявляет найденные команды authoritative.
- Не менять несвязанные ветки в `repo-doctor`.

## План проверки

- добавлены два regression tests; внешний symlink test падал на исходном поведении (`make check` попадал в candidates), затем оба tests прошли;
- `repo-audit` пропускает чтение symlinked `Makefile`;
- `make test-template` — 61 tests, OK; `./scripts/repo-doctor --template` — OK; `git diff --check` — OK; final `python3 scripts/validate-telemetry.py` — 25 cycles valid;
- выполнить independent clean-context review exact diff;
- ожидаемый evidence level: E2; внешняя интеграция/эксплуатационная проверка не требуется.

## Доказательства

После Human Gate: focused brownfield suite — 51 tests, OK; `make test-template` — 61 tests, OK; `./scripts/repo-doctor --template` — exit 0; `git diff --check` — OK; финальный telemetry validator — 25 cycles valid. Первый telemetry цикл TEMPLATE-6 отмечен `partial` из-за выявленного review пробела; исправление записано отдельной append-only строкой.

## Review

- self-review: выполнен; изменение ограничено чтением `Makefile` и двумя regression tests.
- independent review artifact: `docs/reviews/TEMPLATE-6-review.md`; verdict `approved`, открытых P0/P1/P2/P3 нет.
- остаточный риск: проверка намеренно пропускает любой symlinked `Makefile`, в том числе repository-local symlink; обычный regular file сохраняет обнаружение targets.

## Traceability

- `TEMPLATE-4` AC-3 → finding P2 в `TEMPLATE-4-final-review.md` → исправление `scripts/repo-audit` и regression tests.
- task → evidence/review/commit: локальные gates и `docs/reviews/TEMPLATE-6-review.md`; implementation commit `8061409d7dda2127604acc050aebffdf080fae0f`; PR не создавался.
