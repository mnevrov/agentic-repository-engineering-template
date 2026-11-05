# TEMPLATE-13 — Stabilize release evidence and task statuses

**Статус:** in progress
**Риск:** A
**Human gate:** delegated by owner, 2026-11-05.

## Scope

- Согласовать source ROADMAP/TODO, README, first-use guidance, release readiness и исторические TEMPLATE-4 / 8–12 с фактическими CI и owner-reported Pilot evidence.
- Проверять `Blocked` в `scripts/check-task-state.py`; добавить позитивный/негативный regression test.
- Не выдавать CI E2 за E3 и owner-reported HOST evidence за independently checked.
- Сохранить `release/v0.1.0-rc.1` без изменений; не выпускать tag/release.

## Acceptance

- [ ] `make test-template` и `./scripts/repo-doctor --template` PASS.
- [ ] Exact-head GitHub CI PASS.
- [ ] TODO/task states (включая Blocked) согласованы.
- [ ] Независимый final release review завершён и задокументирован.
- [ ] Branch protection проверена администратором.

## Evidence

Source main baseline `42559fa4b03c115d72dc933d71a3bf72caddd6f1`, run 42014455431 — PASS. Full independent release review и управление main rulesets недоступны через текущий connector. Пока gate открыт, telemetry-результат `partial`.
