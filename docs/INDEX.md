# Индекс проектной памяти

Это основная карта документации для человека и AI-агента.

Если вы впервые используете шаблон, начните с:

**[`GETTING_STARTED.md`](GETTING_STARTED.md) — подробная пошаговая инструкция от создания проекта до первого полного агентского цикла.**

## Быстрые ссылки

- [`GETTING_STARTED.md`](GETTING_STARTED.md) — начало работы.
- [`reference/commands.md`](reference/commands.md) — справочник команд.
- [`examples/first-agent-cycle.md`](examples/first-agent-cycle.md) — пример первого цикла.

## Архитектура

- [`architecture/overview.md`](architecture/overview.md) — цель системы, компоненты, потоки, trust boundaries и текущее состояние.
- [`architecture/invariants.md`](architecture/invariants.md) — правила, которые нельзя нарушать обычным изменением.
- [`adr/`](adr/) — принятые архитектурные решения.

## Планирование

- [`backlog/ROADMAP.md`](backlog/ROADMAP.md) — этапы и измеримые результаты.
- [`backlog/TODO.md`](backlog/TODO.md) — ближайшие небольшие задачи.
- [`tasks/`](tasks/) — Task, scope, Acceptance Criteria и evidence.

## Процесс разработки

- [`process/development-cycle.md`](process/development-cycle.md) — полный цикл одной Task.
- [`process/code-review.md`](process/code-review.md) — уровни риска, independent review и исключения.
- [`process/definition-of-done.md`](process/definition-of-done.md) — критерии завершения.
- [`process/evidence-ladder.md`](process/evidence-ladder.md) — уровни силы доказательств E0–E5.
- [`process/traceability.md`](process/traceability.md) — связь требований, ADR, Task, evidence и commit/PR.
- [`process/telemetry.md`](process/telemetry.md) — запись и анализ agentic cycles.

## Review

- [`reviews/`](reviews/) — результаты независимых проверок.
- шаблон: `../.ai/templates/REVIEW.md`.
- стартовый prompt reviewer: `../REVIEW_PROMPT.md`.

## Материалы и примеры

- [`examples/`](examples/) — примеры применения процесса.
- [`workshop/`](workshop/) — демонстрационные материалы.
- [`workshop/team-demo-scenario.md`](workshop/team-demo-scenario.md) — рекомендуемый сценарий командной презентации на 15 минут с несколькими итерациями.
- [`workshop/demo-project.md`](workshop/demo-project.md) — спецификация демонстрационного Mini Task Board, Task DEMO-1…DEMO-4 и checkpoints.
- [`workshop/10-minute-demo.md`](workshop/10-minute-demo.md) — сокращённая демонстрация механики template без live-разработки нескольких фич.

## Актуализация

После изменения архитектуры, интерфейсов, процесса или фактического состояния проекта обновляйте соответствующие документы в том же цикле.

Главное правило: **документация должна описывать фактическое состояние репозитория, а не старый план или содержание прошлой беседы с агентом.**
