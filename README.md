# Agentic Repository Engineering Template

Шаблон репозитория для управляемой разработки с AI-агентами. Основная идея: **долгоживущий контекст проекта, правила, задачи, архитектурные решения, проверки, review, доказательства и телеметрия хранятся в Git**, а не в истории конкретного чата.

Шаблон не привязан к конкретному языку программирования или AI-инструменту. Его можно использовать с OpenCode, Codex CLI, Claude Code и другими coding agents.

## С чего начать

Если вы впервые открыли этот репозиторий, начните с подробной инструкции:

**[`docs/GETTING_STARTED.md`](docs/GETTING_STARTED.md) — пошаговый запуск нового проекта и первый полный агентский цикл.**

Краткий путь выглядит так:

```text
создать проект из шаблона
        ↓
проверить каркас репозитория
        ↓
настроить реальные make check / make test
        ↓
описать архитектуру и инварианты
        ↓
создать одну небольшую Task с Acceptance Criteria
        ↓
запустить coding agent из корня репозитория
        ↓
human gate → реализация → проверки
        ↓
self-review → independent clean-context review
        ↓
evidence → telemetry → commit / PR
```

## Быстрый старт

### Вариант 1 — GitHub Template

Если этот репозиторий отмечен как GitHub Template Repository:

1. Нажмите **Use this template**.
2. Создайте новый репозиторий.
3. Клонируйте уже созданный проект.
4. Выполните первичную диагностику.

```bash
git clone <URL-ВАШЕГО-РЕПОЗИТОРИЯ>
cd <ИМЯ-РЕПОЗИТОРИЯ>
./scripts/repo-doctor
make test-template
```

### Вариант 2 — копирование шаблона вручную

```bash
git clone https://github.com/mnevrov/agentic-repository-engineering-template.git my-project
cd my-project
rm -rf .git
git init
./scripts/repo-doctor
make test-template
```

После этого **сначала настройте реальные проектные проверки** в `Makefile`.

В исходном шаблоне команды:

```bash
make check
make test
make test-integration
```

намеренно завершаются сообщением `NOT CONFIGURED` и ненулевым кодом. Это защитное fail-closed поведение: шаблон не должен создавать впечатление, что проект проверен, пока реальные команды ещё не определены.

## Что нужно заполнить перед разработкой продукта

Минимально настройте:

1. `Makefile` — реальные команды сборки/lint/static checks/tests.
2. `docs/architecture/overview.md` — что строится и из каких частей.
3. `docs/architecture/invariants.md` — правила, которые агент не имеет права нарушать молча.
4. `docs/backlog/ROADMAP.md` — ближайшие этапы и измеримые результаты.
5. `docs/backlog/TODO.md` — небольшие готовые к работе задачи.
6. `docs/adr/` — уже принятые архитектурные решения.
7. `AGENTS.md` — общие правила для любых AI-агентов, если проекту нужны дополнительные ограничения.

После этого создайте первую реальную задачу:

```bash
./scripts/new-task TASK-1 "Короткое название задачи"
```

Заполните `docs/tasks/TASK-1.md`: scope, Acceptance Criteria, риск A/B/C, режим human gate, архитектурные ограничения и способ проверки.

## Как запустить агента

Запускайте выбранный coding agent **из корня репозитория**, чтобы он видел весь project context.

Примеры точек входа:

```bash
opencode
codex
claude
```

После запуска дайте агенту содержимое [`START_PROMPT.md`](START_PROMPT.md) или попросите его выполнить одну конкретную Task по правилам репозитория.

Для Claude Code дополнительно доступны repository commands:

```text
/develop   — выполнить одну небольшую задачу разработки
/iterate   — провести небольшую архитектурную итерацию
```

Для OpenCode, Codex CLI и других агентов используйте `START_PROMPT.md` и файлы из `docs/process/` как общий контракт.

## Рабочий цикл

```text
контекст
  ↓
одна Task + Acceptance Criteria
  ↓
оценка риска A/B/C
  ↓
human gate
  ↓
проверочный сценарий / тест
  ↓
минимальная реализация
  ↓
make check / make test / применимые integration checks
  ↓
self-review
  ↓
independent clean-context review
  ↓
Definition of Done
  ↓
evidence + telemetry
  ↓
commit / PR
```

Подробное описание: [`docs/process/development-cycle.md`](docs/process/development-cycle.md).

## Риски и human gate

| Риск | Типичный пример | Human gate | Review |
|---|---|---|---|
| A | локальная логика, UI, документация, небольшой refactoring | `required` или заранее `delegated` | independent review |
| B | API, интеграция, миграция, concurrency, важные данные | обязательный | усиленный independent review |
| C | auth, права, секреты, destructive actions, деньги, криптография | обязательный | adversarial review до 0 P0/P1 |

Подробно: [`docs/process/code-review.md`](docs/process/code-review.md).

## Доказательства результата

Шаблон различает силу фактической проверки:

- **E0** — изменение только создано;
- **E1** — static check / lint / compile;
- **E2** — unit/contract tests;
- **E3** — integration/e2e;
- **E4** — проверка в целевой или production-like среде;
- **E5** — повторяемое подтверждение в реальной эксплуатации.

Нельзя повышать уровень доказательства формулировкой. Mock не является live integration, а успешная компиляция не является подтверждением пользовательского сценария.

Подробнее: [`docs/process/evidence-ladder.md`](docs/process/evidence-ladder.md).

## Телеметрия

Каждая попытка работы записывается в `.ai/telemetry/cycles.jsonl`, включая `failed`, `partial` и `aborted`.

Пример:

```bash
python3 scripts/record-cycle.py \
  --task TASK-1 \
  --started 2026-09-01T10:00:00Z \
  --ended 2026-09-01T10:40:00Z \
  --result passed \
  --risk A \
  --model example-model \
  --provider example-provider \
  --review-rounds 1 \
  --evidence docs/tasks/TASK-1.md

make telemetry-check
make telemetry-summary
```

`scripts/record-cycle.py` автоматически добавляет доступные Git-данные и длительность цикла. Неизвестные значения оставляйте `null`; не оценивайте токены, стоимость или время человека на глаз.

## Навигация по документации

- [`docs/GETTING_STARTED.md`](docs/GETTING_STARTED.md) — полный onboarding.
- [`docs/INDEX.md`](docs/INDEX.md) — карта проектной памяти.
- [`docs/reference/commands.md`](docs/reference/commands.md) — справочник команд.
- [`docs/process/development-cycle.md`](docs/process/development-cycle.md) — полный рабочий цикл.
- [`docs/process/definition-of-done.md`](docs/process/definition-of-done.md) — Definition of Done.
- [`docs/process/code-review.md`](docs/process/code-review.md) — review, risk levels и исключения.
- [`docs/process/evidence-ladder.md`](docs/process/evidence-ladder.md) — уровни доказательств.
- [`docs/process/telemetry.md`](docs/process/telemetry.md) — телеметрия и метрики.
- [`docs/process/traceability.md`](docs/process/traceability.md) — трассируемость решений и изменений.
- [`docs/examples/first-agent-cycle.md`](docs/examples/first-agent-cycle.md) — конкретный пример первого цикла.

## Главный принцип

Не пытайтесь первым промтом поручить агенту «сделать весь проект». Шаблон рассчитан на **маленькие, ограниченные, проверяемые циклы**, после каждого из которых репозиторий содержит актуальную память о том, что было сделано, почему и чем это подтверждено.

## Лицензия

MIT. Шаблон можно адаптировать под внутренние и публичные проекты.
