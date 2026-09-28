# Независимая проверка — TEMPLATE-6

**Дата:** 2026-09-28\
**Проверяющий / модель:** Codex code-reviewer (GPT-6), независимый clean-context review\
**Риск задачи:** B\
**Проверенный diff / SHA reference (final follow-up, 2026-09-28):** base `ae1e4a6b838c4fce518d6285d327c19b923f49b0`; dirty scoped diff: `scripts/repo-audit` and `tests/test_brownfield_adoption.py` (SHA-256 `d2bca39a4fa3092b0e0ae5d2a20ddb587893844d68717d09edc5a73c7dc1cf0f`); finalized task contract `docs/tasks/TEMPLATE-6.md` (SHA-256 `68dc20c4c0848a07c1443011e35c88b1fb5d1da267a972bd5266930ce09f5d18`); both TEMPLATE-6 telemetry rows, in file order (combined SHA-256 `7a9694818fa8b8ad887d5878cd4948053e8e934dddcf27749e4f3f829b16b29e`). No commit contains this exact diff. HEAD is `ae1e4a6b838c4fce518d6285d327c19b923f49b0`.

## Итог

**Verdict:** approved

В реализации не найдено открытых P0/P1. Изменение ограничено пропуском чтения `Makefile`, если сам путь является symlink; обычный файл продолжает разбираться прежним кодом. Регрессионные тесты проверяют отсутствие и стандартной, и уникальной внешней цели в кандидатах, а также сохранение целей локального обычного файла.

## Замечания

| Severity | Файл/область | Замечание | Способ проверки исправления | Статус |
|---|---|---|---|---|
| P2 | `.ai/telemetry/cycles.jsonl`, TEMPLATE-6 AC-5 | Первоначально отсутствовала запись цикла TEMPLATE-6. Добавлены две append-only строки: первая (`TEMPLATE-6-4b60664b`) честно фиксирует `partial` attempt, вторая (`TEMPLATE-6-b6dc683b`) фиксирует `passed` attempt и закрытие review finding. AC-5 требует записанную и валидную telemetry; обе строки сохранены. | Final follow-up подтвердил обе строки и повторно запустил telemetry validator: `telemetry valid: 25 cycle(s)`. | fixed |

## Проверка критериев приёмки

- **AC-1 — выполнен:** реализация проверяет `makefile.is_symlink()` до `read_text()`. Новый тест использует внешний sentinel `external_secret_target` и проверяет отсутствие его команды и `make check` в кандидатах. Заявленный прогон тестов принят как предоставленное свидетельство.
- **AC-2 — выполнен:** чтение обычного `Makefile` остаётся прежним; добавленный тест проверяет кандидаты `make check` и `make test`. Заявленный прогон тестов принят как предоставленное свидетельство.
- **AC-3 — выполнен:** предоставлены результаты `make test-template` (61 тест) и `./scripts/repo-doctor --template`; в final follow-up reviewer запустил `python3 scripts/validate-telemetry.py`, результат — `telemetry valid: 25 cycle(s)`. Task contract сохраняет историческую отметку предыдущей проверки на 24 строках; финальная проверка включила новую append-only запись. `git diff --check` также заявлен успешным. Команды автора приняты как предоставленное свидетельство, а не повторно исполнены.
- **AC-4 — выполнен:** этот артефакт проверяет указанный scoped dirty diff и фиксирует отсутствие открытых P0/P1.
- **AC-5 — выполнен:** в `.ai/telemetry/cycles.jsonl` присутствуют `TEMPLATE-6-4b60664b` (`partial`, первая попытка) и `TEMPLATE-6-b6dc683b` (`passed`, закрытие review finding). `python3 scripts/validate-telemetry.py` сообщил `telemetry valid: 25 cycle(s)`.

## Остаточный риск

Любой symlinked `Makefile` пропускается, включая ссылку на файл внутри target repository; это поведение явно отмечено в task contract и сохраняет fail-closed границу без вычисления разрешённого пути. Проверка `is_symlink()` и последующее чтение разделены во времени, поэтому конкурентная подмена пути теоретически возможна; для локального read-only discovery и данного объёма эта гонка не образует отдельного блокирующего finding. Кандидаты остаются advisory.

Финальный follow-up проверил finalized task contract и повторно сверил implementation/test diff: новых P0/P1/P2/P3 замечаний нет. Все AC выполнены, независимая проверка остаётся без открытых P0/P1.

Ревью охватывает только `scripts/repo-audit`, `tests/test_brownfield_adoption.py`, контракт TEMPLATE-6 и относящуюся к AC-5 telemetry row. P3 по malformed config в `repo-doctor` и широкие архитектурные изменения исключены из scope.
