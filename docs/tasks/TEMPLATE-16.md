# TEMPLATE-16 — Release preflight and pilot E3 integration evidence

**Статус:** done  
**Риск:** B  
**Human Gate:** владелец поручил выполнить release-sprint 2026-11-06. Это разрешение на подготовку, а не скрытый waiver обязательных release-gates.

## Scope

- Зафиксировать позитивный Pilot integration evidence и SHA с post-merge CI.
- Подготовить точную конфигурацию GitHub main ruleset и инструкции применения.
- Подготовить честный draft v0.1.0 release notes и безопасную процедуру подписанного тега.
- Обновить release readiness с явными блокерами; не объявлять v0.1.0 опубликованной.
- Не запускать новые security/adversarial-раунды TEMPLATE-15 и не менять RC.

## Acceptance

- [x] `mnevrov/agentic-template`: [PR #2](https://github.com/mnevrov/agentic-template/pull/2), exact-main [CI 42198531178](https://github.com/mnevrov/agentic-template/actions/runs/42198531178) PASS, реальный `make test-integration` 2 tests OK — локальный E3 компонентный gate.
- [x] Source template `main` [CI 42196905872](https://github.com/mnevrov/agentic-repository-engineering-template/actions/runs/42196905872) PASS на `59e4321` (до этого документационного PR).
- [x] Параметры branch ruleset зафиксированы в `docs/release/MAIN_RULESET.json`.
- [x] Draft release notes и release playbook подготовлены.
- [x] Нет ложных утверждений об E4/HOST, branch protection, release/tag.
- [ ] Настроить активный ruleset с admin-доступом. **Не входит в выполненный результат этого PR.**
- [ ] Final independent release verdict + HOST gate / explicit risk waiver. **Не выполнены.**
- [ ] Создать verified tag и release. **Заблокировано до предыдущих шагов.**

## Decision

**Release preflight complete; production v0.1.0 NOT APPROVED / NOT PUBLISHED.** Не требуется дополнительный TEMPLATE-15 аудит; остались организационные и платформенные gate. Выпуск можно делать на одобренном SHA после фактического выполнения check-list, а не раньше.

Документальное решение зафиксировано в `docs/RELEASE_READINESS.md` и [issue #9](https://github.com/mnevrov/agentic-repository-engineering-template/issues/9).
