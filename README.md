# Agentic Repository Engineering Template

Практический шаблон репозитория для разработки с AI-агентами. Главная идея: **проектная память, правила, задачи, проверки, доказательства и измеримые циклы живут в Git**, а не растворяются в истории чатов.

Шаблон можно использовать с Claude Code, Codex CLI, OpenCode и любым другим coding agent. Он не привязан к языку программирования и не содержит продуктовых деталей SHEIP.

## Для чего этот шаблон

Он помогает сделать агентскую разработку управляемой:

1. Агент восстанавливает контекст из репозитория, а не из прошлой беседы.
2. Работа идёт по одной небольшой задаче за цикл.
3. До генерации фиксируются задача, критерии приёмки и архитектурные ограничения.
4. Изменения проходят тесты, самопроверку и независимую проверку.
5. Завершение подтверждается доказательствами: команды, логи, ссылки, review.
6. Существенные технические решения оформляются как ADR.
7. **Каждая попытка цикла записывается в append-only JSONL-телеметрию**, поэтому можно измерять скорость, переработки, проверки, стоимость, участие человека и дефекты.

## Быстрый старт

Если репозиторий опубликован как GitHub Template, нажмите **Use this template** и создайте свой проект.

Локально:

```bash
git clone https://github.com/mnevrov/agentic-repository-engineering-template.git my-project
cd my-project
rm -rf .git
git init
./scripts/repo-doctor
./scripts/new-task TASK-1 "Настроить команды проверки проекта"
```

Дальше:

```bash
make doctor
make check
make test
make test-template

python scripts/record-cycle.py \
  --task TASK-1 \
  --started 2026-08-20T12:00:00Z \
  --ended 2026-08-20T12:30:00Z \
  --result passed \
  --risk A \
  --model example-model \
  --review-rounds 1 \
  --human-minutes 5 \
  --evidence docs/tasks/TASK-1.md

make telemetry-check
make telemetry-summary
```

## Что показать агенту в первой сессии

Скопируйте в новый чат содержимое [`START_PROMPT.md`](START_PROMPT.md) или дайте агенту короткую команду:

> Изучи `AGENTS.md`, `CLAUDE.md`, `docs/INDEX.md`, `docs/process/development-cycle.md`, `docs/process/telemetry.md` и `docs/tasks/TASK-1.md`. Предложи план выполнения одной задачи, но не меняй файлы до подтверждения.

Для независимой проверки используйте [`REVIEW_PROMPT.md`](REVIEW_PROMPT.md).

## Структура

```text
.
├── AGENTS.md                    # общие правила для AI-агентов
├── CLAUDE.md                    # инструкция для Claude Code
├── START_PROMPT.md              # промт первой рабочей сессии
├── REVIEW_PROMPT.md             # промт независимой проверки
├── .claude/commands/            # команды /iterate и /develop
├── .ai/
│   ├── templates/               # шаблоны задачи, приёмки, review
│   ├── schemas/                 # схема JSONL-телеметрии
│   └── telemetry/               # append-only журнал циклов
├── docs/
│   ├── architecture/            # архитектура и инварианты
│   ├── adr/                     # архитектурные решения
│   ├── backlog/                 # ROADMAP и TODO
│   ├── process/                 # цикл, review, DoD, доказательства, телеметрия
│   ├── tasks/                   # задачи с критериями приёмки
│   ├── reviews/                 # результаты независимых проверок
│   ├── examples/                # пример первого агентского цикла
│   └── workshop/                # материалы для демонстрации подхода
├── scripts/                     # doctor, new-task, telemetry tools
├── src/                         # код вашего проекта
└── tests/                       # тесты проекта и тесты tooling шаблона
```

## Рабочий цикл

```text
Контекст → одна задача → критерии приёмки → подтверждение человеком
        → тест/реализация → самопроверка → независимая проверка
        → доказательства → обновление документации
        → запись телеметрии → коммит
```

Подробно: [`docs/process/development-cycle.md`](docs/process/development-cycle.md).

## Телеметрия и метрики

Каждая завершённая попытка (`passed`, `failed`, `partial`, `aborted`) добавляет одну строку в `.ai/telemetry/cycles.jsonl`.

Основные группы данных:

- длительность цикла и задачи;
- модель, провайдер и роль агента;
- input/output tokens;
- tool/test/CI runtime;
- review rounds, P0/P1;
- параллельность;
- human steering time;
- оценочная стоимость;
- live-validation;
- дефекты до выпуска и escaped defects;
- ссылка на evidence.

`scripts/telemetry-summary.py` агрегирует эти записи в:

- cycle time;
- task lead time;
- throughput;
- rework rate и cycles/task;
- review intensity;
- parallel share;
- live-validation pass rate;
- token/model usage;
- стоимость;
- human time;
- tool/test/CI runtime;
- defect escape rate.

См. [`docs/process/telemetry.md`](docs/process/telemetry.md).

## Уровни доказательств

Шаблон разделяет утверждения по надёжности:

- **E0** — утверждение без проверки;
- **E1** — локальная ручная проверка;
- **E2** — автоматический unit/contract тест;
- **E3** — интеграционный тест;
- **E4** — проверка в staging/production-like окружении;
- **E5** — реальная эксплуатационная проверка.

Подробно: [`docs/process/evidence-ladder.md`](docs/process/evidence-ladder.md).

## Уровни риска задач

- **A** — обычная задача: self-review + независимая проверка, P0 блокирует завершение.
- **B** — интеграция или контракт: P0/P1 блокируют завершение.
- **C** — безопасность, права, деньги, данные, destructive actions: требуется атакующая проверка до нулевых P0/P1.

Подробно: [`docs/process/code-review.md`](docs/process/code-review.md).

## Что обязательно заменить под свой проект

1. Команды в `Makefile`.
2. Описание системы в `docs/architecture/overview.md`.
3. Архитектурные инварианты в `docs/architecture/invariants.md`.
4. Реальные этапы в `docs/backlog/ROADMAP.md`.
5. Технологические решения в `docs/adr/`.
6. Первую настоящую задачу в `docs/tasks/`.
7. При необходимости — способ автоматического получения токенов/стоимости из используемого AI-инструмента.

## Материалы для презентации

- [`HANDOUT.md`](HANDOUT.md) — короткая памятка слушателя.
- [`docs/workshop/10-minute-demo.md`](docs/workshop/10-minute-demo.md) — сценарий демонстрации на 10 минут.
- [`docs/examples/first-agent-cycle.md`](docs/examples/first-agent-cycle.md) — пример первого агентского цикла.
- [`PUBLISH_TO_GITHUB.md`](PUBLISH_TO_GITHUB.md) — как опубликовать этот каталог как GitHub Template Repository.

## Лицензия

MIT. Можно копировать структуру, менять её под команду и использовать во внутренних проектах.
