# После митапа: с чего начать

Публичный template:

https://github.com/mnevrov/agentic-repository-engineering-template

Этот документ — короткая точка входа для слушателя. Полная документация остаётся в [`INDEX.md`](INDEX.md).

> **Важно:** meetup-версия пока не фиксируется tag/release. Сначала должен пройти полный тестовый прогон и презентационная репетиция. Фактический статус: [`workshop/STATUS.md`](workshop/STATUS.md).

## За 5 минут понять идею

Шаблон решает не задачу «дать AI хороший большой prompt», а задачу **сделать работу coding agent частью проверяемого инженерного процесса**.

```text
Git repository = долговременная память
Task + AC = граница работы
Human Gate = контроль решения
checks/tests/review = проверка
evidence = сила подтверждения
telemetry = наблюдаемость процесса
```

## Выберите свой путь

### Новый проект

1. Нажмите **Use this template**.
2. Создайте новый repository.
3. Выполните:

```bash
./scripts/repo-doctor
make test-template
```

4. Настройте реальные `make check` / `make test`.
5. Продолжайте по [`GETTING_STARTED.md`](GETTING_STARTED.md).

Не считайте исходные `NOT CONFIGURED` project gates ошибкой: template намеренно fail-closed до настройки проекта.

### Существующий проект

Не переносите template tree поверх production repository.

```bash
git clone --depth 1 https://github.com/mnevrov/agentic-repository-engineering-template.git /tmp/agentic-repository-template
cd existing-project
python3 /tmp/agentic-repository-template/scripts/repo-audit --repo . > /tmp/agentic-repository-audit.md
```

Дальше используйте read-only discovery и staged adoption из [`ADOPT_EXISTING_REPOSITORY.md`](ADOPT_EXISTING_REPOSITORY.md).

Ключевой принцип Brownfield: переиспользовать существующие layout, CI, tracker, build/test commands, architecture/docs и AI instructions; добавлять только недостающий минимальный execution context.

## Что было показано на митапе

Основные идеи:

1. новый агент восстанавливает project context из Git, а не из старого чата;
2. за цикл выполняется одна bounded Task;
3. риск и Human Gate определяются до mutation;
4. tests/review/evidence сильнее сообщения модели «готово»;
5. clean-context review отделяется от self-review;
6. Brownfield не требует переписывать существующий repository под template;
7. процесс можно измерять через telemetry.

## Куда смотреть дальше

- [`GETTING_STARTED.md`](GETTING_STARTED.md) — полный Greenfield onboarding.
- [`ADOPT_EXISTING_REPOSITORY.md`](ADOPT_EXISTING_REPOSITORY.md) — Brownfield adoption.
- [`reference/commands.md`](reference/commands.md) — команды.
- [`examples/first-agent-cycle.md`](examples/first-agent-cycle.md) — первый Greenfield cycle.
- [`examples/first-brownfield-cycle.md`](examples/first-brownfield-cycle.md) — короткий Brownfield cycle.
- [`process/development-cycle.md`](process/development-cycle.md) — основной цикл.
- [`process/evidence-ladder.md`](process/evidence-ladder.md) — E0–E5.
- [`process/agent-orchestration.md`](process/agent-orchestration.md) — subagent workflow.
- [`workshop/STATUS.md`](workshop/STATUS.md) — статус demo/rehearsal.

## Demo и checkpoints

Workshop-документы описывают целевой демонстрационный сценарий и presenter runbook. Пока [`workshop/STATUS.md`](workshop/STATUS.md) не переведён в verified-state после реального dry-run, не считайте demo repository, checkpoints или meetup tag подтверждёнными артефактами.
