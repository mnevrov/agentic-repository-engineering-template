# Roadmap — исходный шаблон

Этот ROADMAP описывает `mnevrov/agentic-repository-engineering-template`. В новом проекте `init-project` создаёт собственные milestones.

| Этап | Результат | Готово когда | Статус |
|---|---|---|---|
| T0 — baseline | Greenfield/Brownfield, OpenCode v2, guarded bootstrap, telemetry | CI + HOST pilot evidence | Технически реализовано |
| T1 — v0.1.0 stabilization | Достоверная память проекта, финальное ревью, branch protection | Review exact release SHA + required checks | В работе |
| T2 — release | Версионированный выпуск шаблона | Tag/release на одобренном SHA | Заблокировано T1 |
| T3 — evolution | Новые сценарии и измеримые улучшения | Отдельные Task/PR с AC | Не начато |

## Проверенная база

- Source-template main baseline `42559fa4b03c115d72dc933d71a3bf72caddd6f1` — [CI run 42014455431](https://github.com/mnevrov/agentic-repository-engineering-template/actions/runs/42014455431), PASS.
- CLI v2.2.5 project-agent discovery PASS в CI; v2.1.2 намеренно отклоняется.
- Greenfield bootstrap и telemetry cutover проверены CI, включая первый downstream commit.
- Владелец сообщил об успешном Pilot через OpenCode, восстановлении контекста из Git, independent reviewer и push-CI на merge SHA `c23cbbb9c51d2a988a233373882d0b2d512afebf`. Через подключённый GitHub Pilot недоступен (404), поэтому это **owner-reported evidence**, не независимо проверенный здесь факт.

## Следующий релизный результат

Независимый final review точного нового SHA, согласованный список gate-evidence, проверенная защита `main`. До этого выпуск `v0.1.0` запрещён процедурой.

Ветка `release/v0.1.0-rc.1` заморожена на `61e96b294da0bc567e931f9569675b05ffaa20bd`. Она не содержит TEMPLATE-11/12; не переписывать и не считать итоговым release HEAD.
