# Начало работы с Agentic Repository Engineering Template

Эта инструкция описывает путь от repository, созданного из template, до первой завершённой задачи AI-агента с реальными проверками, independent review, evidence и telemetry.

Если нужны только команды, используйте [`reference/commands.md`](reference/commands.md).

---

## 1. Что даёт template

Template не является IDE или model orchestrator. Он задаёт инженерный контракт repository:

- где хранится актуальный project context;
- какая Task готова к работе;
- что входит и не входит в scope;
- когда нужен human gate;
- какие проверки считаются реальными;
- как отделить self-review от independent review;
- как фиксировать evidence и telemetry;
- как оставить воспроизводимую историю в Git.

Главный принцип:

```text
чат агента — временный рабочий контекст
Git repository — долговременная память проекта
```

---

## 2. Что понадобится

Минимально:

- Git;
- Python 3;
- `make`;
- coding agent;
- реальные команды проверки вашего проекта.

Подход проверен с OpenCode и совместим по контракту с Codex CLI, Claude Code и другими агентами, способными работать с файлами repository.

---

## 3. Создайте downstream repository

### Способ A — GitHub Template

1. Нажмите **Use this template**.
2. Создайте новый repository.
3. Клонируйте его.

```bash
git clone <URL-НОВОГО-РЕПОЗИТОРИЯ>
cd <ИМЯ-ПРОЕКТА>
```

### Способ B — локальная копия

```bash
git clone https://github.com/mnevrov/agentic-repository-engineering-template.git my-project
cd my-project
rm -rf .git
git init
```

После этого настройте `origin` нового проекта.

---

## 4. Обязательно выполните downstream initialization

GitHub Template копирует tracked files source repository. Поэтому без отдельной initialization новый проект унаследует source `TEMPLATE-*` Tasks, source telemetry и часть publish/demo artifacts.

Это **не project history** нового проекта.

Выполните:

```bash
./scripts/init-project "Название проекта"
```

Пример с собственным bootstrap ID:

```bash
./scripts/init-project "Mini Task Board" \
  --bootstrap-id DEMO-BOOTSTRAP \
  --bootstrap-title "Подготовить Mini Task Board к продуктовым итерациям"
```

Initializer:

- удаляет `docs/tasks/TEMPLATE-*.md` и `EXAMPLE-1.md`;
- очищает `.ai/telemetry/cycles.jsonl`;
- удаляет template-only publish artifacts;
- создаёт новый project README;
- создаёт честные placeholder architecture/ROADMAP/TODO;
- создаёт одну Ready bootstrap Task;
- создаёт `.ai/project-initialized`;
- блокирует случайный повторный запуск.

Если повторная initialization действительно нужна:

```bash
./scripts/init-project "Название проекта" --force
```

Используйте `--force` только осознанно: операция предназначена для bootstrap свежего downstream repository.

---

## 5. Проверьте reusable tooling

После initialization:

```bash
./scripts/repo-doctor
make test-template
make telemetry-check
```

Ожидаемо эти команды проходят.

`repo-doctor` теперь также проверяет согласованность:

```text
TODO Ready       ↔ Task status ready
TODO In progress ↔ Task status in progress
TODO Planned     ↔ Task status planned
TODO Done        ↔ Task status done
```

Это защищает новую agent session от противоречивого project context.

---

## 6. Project gates должны начинаться fail-closed

В свежем downstream:

```bash
make check
make test
make test-integration
```

должны возвращать `NOT CONFIGURED` с ненулевым exit code.

Это правильное состояние.

### Почему нельзя просто написать test discovery

Некоторые test runners возвращают exit 0 при нуле найденных тестов. Например, `unittest discover` может создать ложный зелёный gate, если matching tests отсутствуют.

Поэтому нельзя считать target настроенным только потому, что он вызывает test runner.

### Пример честного Python bootstrap

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

Главное не конкретные команды, а семантика:

- target возвращает 0 только если реально выполнил применимую проверку;
- отсутствие inputs/tests не превращается в PASS;
- `NOT CONFIGURED` не считается evidence.

---

## 7. Не делайте integration gate зелёным заранее

Если настоящего integration/e2e scenario ещё нет, оставьте:

```make
test-integration:
	@echo "NOT CONFIGURED: integration tests are not implemented yet" >&2
	@exit 2
```

Не используйте пустой `unittest discover`, `pytest` или другую команду только для того, чтобы target завершился 0.

Настраивайте `make test-integration` одновременно с появлением первого настоящего integration/e2e test.

Это было отдельно подтверждено real dry-run: до DEMO-3 integration gate честно возвращал exit 2, а в DEMO-3 был заменён настоящим restart-flow test.

---

## 8. Product tests и template tooling tests — разные наборы

Рекомендуемая структура:

```text
tests/           project/product tests
template_tests/  reusable repository tooling tests
```

Targets:

```text
make test           → tests/
make test-template  → template_tests/
```

Не смешивайте их. Source-only contract tests не должны жить в downstream product test suite.

---

## 9. Завершите bootstrap Task до feature-разработки

`scripts/init-project` создаёт одну Ready bootstrap Task. Она должна зафиксировать реальные сведения о проекте.

### Architecture overview

`docs/architecture/overview.md` должен содержать:

- проблему и пользователей;
- компоненты;
- data/control flows;
- внешние системы;
- trust boundaries;
- нефункциональные требования;
- **отдельно** текущее состояние и целевое состояние.

Не описывайте будущий компонент как уже реализованный.

### Invariants

`docs/architecture/invariants.md` содержит только реальные правила, которые feature Task не должна нарушать молча.

### ROADMAP/TODO

`ROADMAP` — крупные измеримые этапы.

`TODO` — ближайшие bounded Tasks. Для каждой Task состояние TODO должно совпадать с полем `**Статус:**` в `docs/tasks/<ID>.md`.

### Telemetry

После initialization `.ai/telemetry/cycles.jsonl` должна быть пустой. Source telemetry не переносится в project history.

Первую строку записывает уже собственный bootstrap cycle.

---

## 10. Создавайте Tasks маленькими и самодостаточными

Если bootstrap завершён, создайте следующую Task:

```bash
./scripts/new-task TASK-1 "Короткое название"
```

Заполните:

- статус;
- risk A/B/C;
- human gate;
- зачем;
- scope / non-scope;
- Acceptance Criteria;
- архитектурные ограничения;
- verification plan;
- ожидаемый evidence level.

После добавления в `TODO Ready` установите:

```text
**Статус:** ready
```

`repo-doctor` обнаружит несоответствие.

---

## 11. Human gate

### Risk A

Допустимы:

```text
Human gate: required
```

или заранее:

```text
Human gate: delegated
```

### Risk B/C

Требуется явное подтверждение человека до реализации.

Опасные или необратимые действия требуют подтверждения независимо от категории.

---

## 12. Запуск coding agent

Из корня repository:

```bash
opencode
codex
claude
```

Общий prompt: [`../START_PROMPT.md`](../START_PROMPT.md).

Claude Code repository commands:

```text
/develop
/iterate
```

Для обычной bounded feature Task используйте `/develop`.

`/iterate` предназначен прежде всего для небольшого изменения архитектуры/плана и не должен автоматически превращаться в большую реализацию.

---

## 13. Полный цикл одной Task

```text
1. прочитать repository context
2. выбрать одну Ready Task
3. показать risk / human gate / AC / plan / verification
4. получить human approval, если required
5. добавить test или другой воспроизводимый scenario
6. реализовать минимальный scope
7. запустить реальные gates
8. self-review
9. implementation commit или фиксированный reviewable HEAD
10. independent clean-context review
11. исправить P0/P1 и применимые замечания
12. заполнить evidence
13. синхронизировать Task status и TODO
14. записать telemetry
15. closure commit / PR
```

Independent reviewer должен проверять **тот HEAD, который реально будет закрыт**, либо после исправлений нужен повторный review.

---

## 14. Evidence

Используйте уровни:

- E0 — изменение создано;
- E1 — static check / compile / lint;
- E2 — unit/contract tests;
- E3 — integration/e2e;
- E4 — target/production-like environment;
- E5 — повторяемая реальная эксплуатация.

Примеры ошибок:

```text
0 tests + exit 0       ≠ E2
NOT CONFIGURED         ≠ PASS
unit serialization     ≠ restart integration
curl к localhost       ≠ production validation
```

---

## 15. Independent review

Self-review не заменяет независимый clean-context review.

Результат сохраняется:

```text
docs/reviews/<TASK-ID>-review.md
```

Если independent review недоступен, цикл не должен маркироваться `passed`; используйте `partial` или `failed` согласно фактическому состоянию.

---

## 16. Telemetry

Минимальная запись:

```bash
python3 scripts/record-cycle.py \
  --task TASK-1 \
  --started <ISO-8601> \
  --ended <ISO-8601> \
  --result passed
```

Добавляйте только реально известные поля:

```bash
--risk A
--model <known-model>
--provider <known-provider>
--review-rounds 1
--review-p0 0
--review-p1 0
--evidence docs/tasks/TASK-1.md
```

Не угадывайте model/provider, token usage, cost или human time.

После записи:

```bash
make telemetry-check
make telemetry-summary
```

---

## 17. Финальная проверка Task

Перед closure:

```bash
./scripts/repo-doctor
make check
make test
make test-template
make telemetry-check
```

Если integration gate уже настроен и применим:

```bash
make test-integration
```

Если ещё нет, expected `NOT CONFIGURED` должен быть явно отражён в evidence и не засчитываться как успешный gate.

---

## 18. Что подтвердил полный demo dry-run

Отдельный Mini Task Board repository прошёл:

```text
bootstrap
DEMO-1 read-only
DEMO-2 validated write + required human gate
DEMO-3 persistence + restart integration
DEMO-4 done/filter/counters
```

В финальном состоянии были подтверждены product, template tooling и integration test suites, independent review каждой Task, telemetry каждого цикла и Git checkpoints.

Именно этот прогон выявил hardening, описанный выше.

Полная инструкция: [`workshop/real-repository-dry-run.md`](workshop/real-repository-dry-run.md).

---

## 19. Что не делать

Не:

- начинать feature-разработку до initialization/bootstrap;
- считать source `TEMPLATE-*` Tasks историей нового проекта;
- смешивать product и template tooling tests;
- превращать zero-test discovery в зелёный gate;
- делать integration target зелёным до настоящего integration scenario;
- оставлять `TODO Ready` при `Task status: planned`;
- завышать evidence level;
- переписывать старые telemetry rows вместо append-only истории;
- поручать агенту «сделать весь проект» одной неограниченной задачей.

---

## 20. Короткий checklist

Перед первой feature Task:

```text
[ ] scripts/init-project выполнен
[ ] inherited source Tasks/telemetry очищены
[ ] bootstrap Task закрыта
[ ] architecture описывает фактическое состояние
[ ] invariants реальны
[ ] TODO и Task statuses согласованы
[ ] make check выполняет реальную работу
[ ] make test запускает реальные product tests
[ ] make test-template запускает только reusable tooling tests
[ ] integration gate либо настоящий, либо честно NOT CONFIGURED
[ ] telemetry нового проекта содержит только его собственные cycles
```

После этого repository готов к управляемой agentic development.
