# TEMPLATE-7 — Игнорировать локальное состояние Serena

**Статус:** complete\
**Риск:** A\
**Human gate:** подтверждён запросом владельца на изменение `.gitignore` и локальный commit 2026-09-28\
**Владелец:** repository owner\
**Requirements / ADR:** локальная конфигурация agent tooling не должна попадать в template commit; ADR n/a

## Объём

- игнорировать корневой каталог `.serena/`, содержащий локальный Serena-профиль и настройки;
- проверить, что README не требует изменения для этой локальной настройки;
- сохранить локальные файлы на диске и не добавлять их в commit.

## Критерии приёмки

- [x] AC-1: файлы внутри `.serena/` совпадают с новым root ignore rule.
- [x] AC-2: `.gitignore` и README остаются видимыми Git; README не содержит требующих изменения сведений о локальном Serena workspace.
- [x] AC-3: independent clean-context review не находит P0/P1.
- [x] AC-4: telemetry добавлена append-only и проходит validator.

## Evidence

`git check-ignore --verbose` подтвердил root rule для файлов `.serena/`; `.gitignore` и `README.md` не совпадают с ignore patterns. README просмотрен: он описывает greenfield и brownfield onboarding, но не содержит инструкций о локальном Serena workspace. `make test-template` — 61 tests, OK; `./scripts/repo-doctor --template` — OK; final telemetry validator — 28 cycles valid.

## Review

- self-review: выполнен; правило ограничено root-каталогом `/.serena/`, README оставлен без изменений.
- independent review artifact: `docs/reviews/TEMPLATE-7-review.md`.
- verdict `approved`; открытых P0/P1/P2/P3 нет.

## Traceability

- запрос владельца → TEMPLATE-7 → `.gitignore` и проверки ignore behavior.
