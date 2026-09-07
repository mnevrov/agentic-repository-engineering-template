# TEMPLATE-1 — Усилить guardrails по итогам сравнения с SHEIP

**Статус:** in review  
**Риск:** B  
**Human gate:** required — подтверждён пользователем запросом «Исправь»  
**Владелец:** repository maintainer  
**Связанный эпик/этап:** M0  
**Requirements / ADR:** process hardening; ADR не требуется  

## Зачем

Устранить расхождения между заявленным agentic workflow и реально исполняемыми guardrails шаблона.

## Объём

### Входит

- fail-closed project gates вместо false-green placeholders;
- обязательный clean-context review artifact;
- строгий human gate для B/C и explicit delegation для A;
- optional traceability model;
- automatic Git/duration telemetry и CI requirement новой telemetry row.

### Не входит

- provider/model orchestration;
- отдельный agent runtime;
- изменение продуктовой архитектуры downstream проектов.

## Критерии приёмки

- [x] AC-1: ненастроенные `make check/test/test-integration` возвращают `NOT CONFIGURED` и code 2.
- [x] AC-2: процесс запрещает `passed` без independent clean-context review.
- [x] AC-3: B/C требуют human gate; A допускает только explicit delegation.
- [x] AC-4: документирована минимальная и расширенная traceability chain.
- [x] AC-5: `record-cycle.py` автоматически собирает Git/duration evidence.
- [x] AC-6: CI требует новую telemetry row для содержательного изменения.
- [ ] AC-7: GitHub CI прошёл, а independent clean-context review сохранён в `docs/reviews/TEMPLATE-1-review.md`.

## План проверки

- unit: `make test-template`;
- static/process: `./scripts/repo-doctor`;
- fail-closed: `make check`, `make test`, `make test-integration` → exit 2;
- GitHub CI: после открытия PR;
- ожидаемый evidence level: E2 локально, E3 после GitHub CI.

## Доказательства

- подготовленный patch прошёл локальные template tests и repo-doctor до публикации;
- write-доступ GitHub восстановлен, изменения публикуются в `fix/harden-agentic-workflow`;
- независимый review намеренно не подменяется self-review этой же авторской сессией.

## Review

- self-review: выполнен после локальных тестов;
- independent review artifact: `docs/reviews/TEMPLATE-1-review.md` — ожидается;
- остаточные замечания: дождаться CI и выполнить clean-context review.

## Traceability

- requirement/ADR → task: process hardening, ADR `n/a`;
- task → evidence: этот файл + GitHub Actions PR run;
- task → commit/PR: будет заполнено после создания PR.
