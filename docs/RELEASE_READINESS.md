# Release readiness — OpenCode v2 template

**Статус: STABILIZATION. Production release v0.1.0 ещё не одобрен.**

Технический CI, отчёт владельца о HOST/Pilot и независимый release-review — разные уровни доказательств.

## Матрица gate-evidence на 2026-11-06

| Критерий | Доказательство | Статус |
|---|---|---|
| Source template: doctor, tests, OpenCode v2 matrix | [final remediation main CI 42195162188](https://github.com/mnevrov/agentic-repository-engineering-template/actions/runs/42195162188), SHA `a3bf31a`; `doctor`, v2.1.2 negative, v2.2.5 positive | **PASS на последнем кодовом SHA перед документальным закрытием TEMPLATE-15** |
| Bootstrap и first telemetry cutover | PR #13 + downstream smoke в source CI | PASS, синтетический downstream |
| Release audit P1/P2/P3, TEMPLATE-15 | [TEMPLATE-15](tasks/TEMPLATE-15.md), [ADR-0001](adr/0001-provenance-bound-telemetry-cutover.md), [adversarial review rounds 1–6](reviews/TEMPLATE-15-review.md), [CI 42194726094](https://github.com/mnevrov/agentic-repository-engineering-template/actions/runs/42194726094), [CI 42195162188](https://github.com/mnevrov/agentic-repository-engineering-template/actions/runs/42195162188) | **ACCEPTED / REMEDIATION COMPLETE**; 144 reported tests, round 6 compressed by owner decision |
| OpenCode v2.2.5 agents / v2.1.2 reject | PR #12 + матрица CI | PASS |
| OpenCode HOST acceptance | `make opencode-acceptance` | PASS по отчёту владельца |
| Pilot /develop, Human Gate, tests, reviewer, new-session recovery | `mnevrov/agentic-template` | PASS по отчёту владельца; эти HOST-события не являются CI-аттестацией |
| Pilot PR и post-merge Actions | [run 42023246757](https://github.com/mnevrov/agentic-template/actions/runs/42023246757), [run 42024296100](https://github.com/mnevrov/agentic-template/actions/runs/42024296100), merge `c23cbbb9c51d2a988a233373882d0b2d512afebf` | Ранее подтверждено владельцем; доступен `mnevrov/agentic-template`, но эти CI не заменяют HOST-доказательства |
| Integration/e2e на Pilot | `make test-integration` | **NOT CONFIGURED, rc=2** — fail-closed, не PASS |
| Final independent review точного release SHA | issue #9 / отдельный release verdict | **NOT PERFORMED**; дополнительные раунды TEMPLATE-15 отменены владельцем, но это не равнозначно release-approval |
| Защита main | GitHub `branches/main` показывает `protected=false`; `rulesets` пусты (проверка 2026-11-06) | **BLOCKED**: на момент закрытия TEMPLATE-15 защита не настроена; доступный GitHub connector не предоставляет запись branch rules |
| Версионированный v0.1.0 | tag/release | **NOT CREATED** |

**Уровни evidence:** E1 — static; E2 — unit/contract; E3 — integration/e2e; E4 — target/prod-like; E5 — эксплуатационное повторение. Один факт green CI **не** повышает unit-tests до E3.

**Решение по TEMPLATE-15:** remediation закрыта без новых adversarial-раундов по поручению владельца. Это не выпуск `v0.1.0`. Issue #9 продолжает фиксировать отдельные release-gates; не подменять их успешным CI или завершённой security-remediation.

## Релизные действия (требуют доказательств)

1. Получить PASS на exact final SHA `main` (doctor, telemetry, OpenCode v2 matrix, downstream smoke). Сохранить SHA и Actions URLs.
2. Запустить независимое ревью **в новой чистой сессии**, передав final SHA, полный diff с `61e96b...`, Task/AC, фактические CI-результаты, архитектурные инварианты, diff конфигураций OpenCode и прав, bootstrap + telemetry security. Зафиксировать verdict и P0/P1/P2/P3 в **GitHub PR review или неизменяемом комментарии к issue #9**, явно указав проверенный точный SHA. При необходимости можно зеркалировать результат в `docs/reviews/RELEASE-0.1.0-final-review.md`, но его коммит меняет HEAD и требует **повторной проверки нового SHA**. Самопроверка автора не считается независимой.
3. Настроить для `main` GitHub Branch Protection или Ruleset: PR перед merge, required checks `doctor`, `OpenCode v2.1.2 configuration`, `OpenCode v2.2.5 configuration`, запрет force push и удаления. Независимый approve на PR — при наличии доступного второго reviewer; для solo-owner явно фиксировать невозможность и обеспечить внешний review как ручной gate.
4. Повторно проверить защиту через GitHub UI/API и статус Checks после настройки. Нельзя считать правила настроенными только потому, что документ описывает их.
5. Только после final review, зелёного final-main CI и branch rules — создать **новый** release tag `v0.1.0` на одобренном SHA и GitHub Release. Старую ветку `release/v0.1.0-rc.1` не переписывать.

## Ограничения

- Отдельная meetup-репетиция с DEMO-1…DEMO-4, QR/ссылками и таймингом не выполнена и отслеживается в [workshop/STATUS.md](workshop/STATUS.md); это **другой** acceptance gate.
- Модельный путь LiteLLM, конкретный provider и токены/стоимость не подтверждены логами этого инструмента; нет основания заявлять E4/E5.
- Старые telemetry-циклы `partial` не редактируются задним числом. Технически выполненные TEMPLATE-4 и TEMPLATE-8…12 заблокированы на **финальном release approval**, а не на переписывании истории.
- [Журнал релизного решения — issue #9](https://github.com/mnevrov/agentic-repository-engineering-template/issues/9).
