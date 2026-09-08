# Agentic Repository Engineering Template

Шаблон репозитория для управляемой разработки с AI-агентами. Основная идея: **долгоживущий контекст проекта, правила, задачи, архитектурные решения, проверки, review, доказательства и telemetry хранятся в Git**, а не в истории конкретного чата.

Шаблон не привязан к языку или AI-инструменту. Его можно использовать с OpenCode, Codex CLI, Claude Code и другими coding agents.

## Что было проверено реальным dry-run

Отдельный downstream demo repository прошёл bootstrap и четыре последовательные продуктовые итерации. Dry-run подтвердил сам workflow и выявил проблемы, которые теперь учитывает onboarding:

- product tests и template tooling tests должны быть разделены;
- source-only contract tests не должны наследоваться downstream;
- пустой test discovery не считается настроенным gate;
- project gates должны fail-closed при отсутствии реальной работы;
- source `TEMPLATE-*` Tasks и telemetry не должны становиться project history;
- TODO state и Task status должны быть согласованы;
- integration gate остаётся `NOT CONFIGURED`, пока настоящий integration/e2e test не существует.

## С чего начать

Подробно: [`docs/GETTING_STARTED.md`](docs/GETTING_STARTED.md).

Короткий путь:

```text
создать repository из template
        ↓
scripts/init-project <project-name>
        ↓
выполнить bootstrap Task
        ↓
настроить реальные make check / make test
        ↓
описать архитектуру, инварианты и backlog
        ↓
одна bounded Task
        ↓
human gate → реализация → реальные проверки
        ↓
self-review → independent clean-context review
        ↓
evidence → telemetry → commit / PR
```

## Быстрый старт

### Вариант 1 — GitHub Template

1. Нажмите **Use this template**.
2. Создайте новый repository.
3. Клонируйте его.
4. Выполните downstream initialization.

```bash
git clone <URL-ВАШЕГО-РЕПОЗИТОРИЯ>
cd <ИМЯ-РЕПОЗИТОРИЯ>

./scripts/init-project "Название проекта"
```

Для demo или другого заранее известного bootstrap ID:

```bash
./scripts/init-project "Mini Task Board" \
  --bootstrap-id DEMO-BOOTSTRAP \
  --bootstrap-title "Подготовить Mini Task Board к продуктовым итерациям"
```

Initializer:

- очищает source `TEMPLATE-*` / `EXAMPLE-1` Tasks;
- обнуляет inherited source telemetry;
- удаляет template-only publish artifacts;
- создаёт честный project README/architecture/ROADMAP/TODO;
- создаёт одну Ready bootstrap Task;
- защищён от случайного повторного запуска.

### Вариант 2 — локальная копия

```bash
git clone https://github.com/mnevrov/agentic-repository-engineering-template.git my-project
cd my-project
rm -rf .git
git init

./scripts/init-project "Название проекта"
```

Если клонировать source repository и **не** выполнить initialization, новый проект унаследует историю разработки самого template. Это не project memory и не должно использоваться как контекст downstream-проекта.

## Проверка после initialization

Сначала проверяем reusable tooling:

```bash
./scripts/repo-doctor
make test-template
make telemetry-check
```

В свежем downstream project команды:

```bash
make check
make test
make test-integration
```

намеренно должны завершаться `NOT CONFIGURED` с ненулевым кодом, пока реальные project gates не настроены.

`NOT CONFIGURED` — не ошибка template и не PASS. Это fail-closed состояние.

## Как настраивать project gates

`make check` и `make test` должны выполнять **реальную работу**. Zero-work / zero-test success недопустим.

Например, если используется `unittest discover`, сначала должна существовать отдельная проверка, что matching tests действительно есть:

```make
check:
	@[ -d src ] && [ -d tests ] || \
		{ echo "NOT CONFIGURED: expected src/ and tests/" >&2; exit 2; }
	@find src tests -type f -name '*.py' -print -quit | grep -q . || \
		{ echo "NOT CONFIGURED: no Python sources found" >&2; exit 2; }
	python3 -m compileall -q src tests

test:
	@find tests -maxdepth 1 -type f -name 'test_*.py' | grep -q . || \
		{ echo "NOT CONFIGURED: add at least one project test" >&2; exit 2; }
	python3 -m unittest discover -s tests -p 'test_*.py'
```

Не настраивайте `make test-integration` на пустой discovery только ради зелёного результата. Пока настоящего integration/e2e test нет, gate должен оставаться `NOT CONFIGURED`.

## Разделение tests

В downstream repository:

```text
tests/           product tests
template_tests/  reusable repository-tooling tests
```

`make test` не должен запускать `template_tests/`, а `make test-template` не должен запускать product tests.

## Память проекта

До feature-разработки bootstrap Task должна зафиксировать:

1. реальные project gates;
2. `docs/architecture/overview.md` — фактическое и целевое состояние отдельно;
3. `docs/architecture/invariants.md` — реальные ограничения;
4. `docs/backlog/ROADMAP.md`;
5. `docs/backlog/TODO.md`;
6. первые bounded Tasks;
7. пустую project telemetry до первого собственного цикла.

`repo-doctor` дополнительно проверяет, что секции `Ready / In progress / Planned / Done` в TODO согласованы с полем `**Статус:**` соответствующей Task.

## Как запустить агента

Запускайте coding agent из корня repository:

```bash
opencode
codex
claude
```

Общий контракт находится в `AGENTS.md`, `START_PROMPT.md` и `docs/process/`.

Для Claude Code доступны repository commands:

```text
/develop  — полностью выполнить одну bounded Task
/iterate  — провести небольшую архитектурную/планировочную итерацию
```

Для обычной feature-задачи предпочтителен `/develop`.

## Рабочий цикл

```text
repository context
  ↓
одна Task + Acceptance Criteria
  ↓
risk A/B/C + human gate
  ↓
проверочный сценарий / тест
  ↓
минимальная реализация
  ↓
реальные check/test/integration gates
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

## Риски и human gate

| Риск | Типичный пример | Human gate | Review |
|---|---|---|---|
| A | локальная логика, UI, документация, небольшой refactoring | `required` или заранее `delegated` | independent review |
| B | API, интеграция, миграция, concurrency, важные данные | обязательный | усиленный independent review |
| C | auth, права, destructive actions, деньги, криптография | обязательный | adversarial review до 0 P0/P1 |

Подробнее: [`docs/process/code-review.md`](docs/process/code-review.md).

## Evidence levels

- **E0** — изменение создано;
- **E1** — static check / lint / compile;
- **E2** — unit/contract tests;
- **E3** — integration/e2e;
- **E4** — target / production-like environment;
- **E5** — повторяемое подтверждение в реальной эксплуатации.

Уровень нельзя повысить формулировкой. Пустой test discovery и `NOT CONFIGURED` не являются evidence.

## Telemetry

Каждая попытка работы записывается в `.ai/telemetry/cycles.jsonl`, включая `failed`, `partial` и `aborted`.

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

Model/provider передавайте только когда они реально известны. Неизвестные значения не нужно угадывать.

## Навигация

- [`docs/GETTING_STARTED.md`](docs/GETTING_STARTED.md) — onboarding.
- [`docs/INDEX.md`](docs/INDEX.md) — карта project memory.
- [`docs/reference/commands.md`](docs/reference/commands.md) — команды.
- [`docs/process/development-cycle.md`](docs/process/development-cycle.md) — рабочий цикл.
- [`docs/workshop/real-repository-dry-run.md`](docs/workshop/real-repository-dry-run.md) — полный проверенный dry-run.

## Главный принцип

Не поручайте агенту первым промтом «сделать весь проект». Сначала repository должен стать корректной долговременной памятью, после чего работа идёт маленькими, ограниченными и доказуемыми циклами.

## Лицензия

MIT.
