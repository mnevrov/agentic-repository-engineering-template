# Памятка: инженерный репозиторий для AI-разработки

Публичный шаблон: https://github.com/mnevrov/agentic-repository-engineering-template

Короткая точка входа после митапа: [`docs/MEETUP.md`](docs/MEETUP.md).

> Статус demo и репетиции хранится в [`docs/workshop/STATUS.md`](docs/workshop/STATUS.md). Пока полный dry-run не завершён, meetup-tag/release не создаётся и demo/checkpoints не считаются подтверждёнными.

## Главная идея

AI-агент не должен быть носителем памяти проекта. **Память проекта — сам репозиторий.**

До изменения кода агент должен понимать:

- какую одну задачу он решает;
- scope и Acceptance Criteria;
- архитектурные ограничения;
- риск и Human Gate;
- какими реальными проверками будет подтверждён результат.

## Два режима

### Greenfield — новый проект

Создайте repository через **Use this template**, затем:

```bash
./scripts/repo-doctor
make test-template
```

После этого настройте реальные project gates: `make check`, `make test` и при необходимости `make test-integration`. В исходном template они намеренно `NOT CONFIGURED`.

Полный путь: [`docs/GETTING_STARTED.md`](docs/GETTING_STARTED.md).

### Brownfield — существующий проект

Не копируйте template поверх существующего repository. Сначала выполните read-only audit:

```bash
git clone --depth 1 https://github.com/mnevrov/agentic-repository-engineering-template.git /tmp/agentic-repository-template
cd existing-project
python3 /tmp/agentic-repository-template/scripts/repo-audit --repo . > /tmp/agentic-repository-audit.md
```

Дальше: discovery → verification → context/truth → gap analysis → Human Gate → минимальный adoption layer → одна существующая bounded Task.

Полный путь: [`docs/ADOPT_EXISTING_REPOSITORY.md`](docs/ADOPT_EXISTING_REPOSITORY.md).

## Один инженерный цикл

```text
repository context
→ одна Task + Acceptance Criteria
→ risk + Human Gate
→ минимальная реализация
→ реальные checks/tests
→ self-review
→ independent clean-context review
→ evidence
→ telemetry
→ commit / PR
```

## Уровни риска

- **A** — локальная логика, документация, низкий риск.
- **B** — API, интеграции, данные, миграции, concurrency.
- **C** — auth, права, секреты, destructive actions, деньги, криптография.

Чем выше риск, тем сильнее Human Gate и независимая проверка.

## «Готово» означает evidence

- **E0** — изменение только создано.
- **E1** — static check / compile / lint.
- **E2** — unit/contract tests.
- **E3** — integration/e2e.
- **E4** — target/production-like verification.
- **E5** — повторяемое подтверждение в эксплуатации.

Сообщение модели «готово» не повышает evidence level.

## Что открыть дальше

- [`docs/MEETUP.md`](docs/MEETUP.md) — маршрут после выступления.
- [`docs/INDEX.md`](docs/INDEX.md) — карта документации.
- [`docs/reference/commands.md`](docs/reference/commands.md) — команды.
- [`docs/workshop/STATUS.md`](docs/workshop/STATUS.md) — статус тестового прогона.
