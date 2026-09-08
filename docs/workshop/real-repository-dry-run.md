# Контрольный прогон на реальном репозитории

Эта инструкция описывает полный validated dry-run Agentic Repository Engineering Template на отдельном downstream repository и последующую репетицию командной демонстрации.

Dry-run нужен не только для получения Mini Task Board. Он проверяет сам инженерный процесс:

- downstream initialization действительно отделяет source template history;
- новый агент восстанавливает контекст из Git;
- project gates не дают zero-work/zero-test false-green;
- одна Task ограничивает scope;
- human gate реально останавливает Risk B/C до подтверждения;
- independent review работает с clean context;
- evidence соответствует силе проверки;
- telemetry содержит только реальные project cycles;
- Git checkpoints позволяют воспроизводить каждую итерацию.

Связанные документы:

- [`demo-project.md`](demo-project.md) — спецификация Mini Task Board;
- [`team-demo-scenario.md`](team-demo-scenario.md) — сценарий выступления;
- [`../GETTING_STARTED.md`](../GETTING_STARTED.md) — общий onboarding.

---

# 1. Два разных прогона

## 1.1. Полный engineering dry-run

Выполняется один раз:

```text
downstream init
→ bootstrap
→ DEMO-1
→ DEMO-2
→ DEMO-3
→ DEMO-4
→ reviews/evidence/telemetry
→ checkpoints
```

## 1.2. Timed rehearsal

Проводится после успешного engineering dry-run.

Для выступления не нужно повторно генерировать все фичи. Рекомендуемый live segment — DEMO-2 от checkpoint `demo/01-read-board`; остальные состояния показываются через заранее проверенные tags.

---

# 2. Проверенный конечный результат

После полного прогона downstream repository должен содержать:

```text
AGENTS.md
README.md
Makefile
src/taskboard/...
tests/...
template_tests/...
docs/architecture/...
docs/backlog/...
docs/tasks/DEMO-BOOTSTRAP.md
docs/tasks/DEMO-1.md
docs/tasks/DEMO-2.md
docs/tasks/DEMO-3.md
docs/tasks/DEMO-4.md
docs/reviews/...
.ai/telemetry/cycles.jsonl
```

Checkpoints:

```text
demo/00-bootstrap
demo/01-read-board
demo/02-create-task
demo/03-persistence
demo/04-finished
```

---

# 3. Требования

Проверьте:

```bash
git --version
python3 --version
make --version
```

Для Mini Task Board достаточно **Python 3.10+**. Реальный dry-run успешно выполнен на Python 3.10; код demo не требует 3.11-specific возможностей.

Также нужен coding agent, например OpenCode, Codex CLI или Claude Code.

Для воспроизводимости используйте в dry-run тот же инструмент, который планируется показывать команде.

---

# 4. Создайте downstream repository

## GitHub Template

1. Нажмите **Use this template**.
2. Создайте `agentic-template-demo`.
3. Клонируйте новый repository.

```bash
git clone <URL-DEMO-REPOSITORY>
cd agentic-template-demo
```

## Локальная копия

```bash
git clone https://github.com/mnevrov/agentic-repository-engineering-template.git agentic-template-demo
cd agentic-template-demo
rm -rf .git
git init
```

---

# 5. Выполните downstream initialization

Это обязательный шаг. GitHub Template копирует tracked source files, включая историю разработки самого template.

Для demo:

```bash
./scripts/init-project "Mini Task Board" \
  --bootstrap-id DEMO-BOOTSTRAP \
  --bootstrap-title "Подготовить Mini Task Board к продуктовым итерациям"
```

Проверьте:

```bash
ls docs/tasks
wc -l .ai/telemetry/cycles.jsonl
```

Ожидаемо:

- `TEMPLATE-*` и `EXAMPLE-1` отсутствуют;
- существует `DEMO-BOOTSTRAP.md`;
- source telemetry очищена;
- README/architecture/ROADMAP/TODO больше не заявляют source template history как project state.

---

# 6. Проверьте исходный fail-closed contract

```bash
./scripts/repo-doctor
make test-template
make telemetry-check
```

Эти команды должны PASS.

Project gates до bootstrap:

```bash
make check
make test
make test-integration
```

должны завершиться `NOT CONFIGURED` с ненулевым кодом.

Если `make check` или `make test` дают 0 до настройки реальной проверки — остановите dry-run: contract нарушен.

---

# 7. Bootstrap — отдельная Task

`scripts/init-project` уже создал:

```text
docs/tasks/DEMO-BOOTSTRAP.md
```

Task имеет:

```text
Risk: A
Human gate: delegated
Status: ready
```

Переведите её в `in progress` одновременно в Task и TODO перед началом работы.

Bootstrap должен:

- настроить реальные `make check` и `make test`;
- оставить `make test-integration` fail-closed до DEMO-3;
- создать минимум один настоящий product smoke test;
- заполнить architecture overview/invariants;
- создать DEMO-1…DEMO-4;
- обновить ROADMAP/TODO;
- добавить runtime data в `.gitignore`;
- подтвердить, что product tests и template tooling tests разделены.

---

# 8. Настройте честные project gates

Для demo можно использовать:

```make
check:
	@[ -d src ] && [ -d tests ] || \
		{ echo "NOT CONFIGURED: expected src/ and tests/ directories" >&2; exit 2; }
	@find src tests -type f -name '*.py' -print -quit | grep -q . || \
		{ echo "NOT CONFIGURED: no Python sources found in src/ or tests/" >&2; exit 2; }
	python3 -m compileall -q src tests

test:
	@find tests -maxdepth 1 -type f -name 'test_*.py' | grep -q . || \
		{ echo "NOT CONFIGURED: add at least one project test" >&2; exit 2; }
	python3 -m unittest discover -s tests -p 'test_*.py'

test-integration:
	@echo "NOT CONFIGURED: integration tests are not implemented yet" >&2
	@exit 2
```

`test-template` оставьте отдельным reusable target:

```make
test-template:
	@[ -d template_tests ] || \
		{ echo "NOT CONFIGURED: template_tests/ directory is missing" >&2; exit 2; }
	@find template_tests -maxdepth 1 -type f -name 'test_*.py' | grep -q . || \
		{ echo "NOT CONFIGURED: no template tooling tests found" >&2; exit 2; }
	python3 -m unittest discover -s template_tests -p 'test_*.py'
```

## Почему guards обязательны

`unittest discover` может вернуть exit 0 при нуле найденных тестов. Поэтому команда вида:

```make
test:
	python3 -m unittest discover -s tests -p 'test_*.py'
```

сама по себе ещё не гарантирует, что gate что-то проверил.

---

# 9. Bootstrap smoke test

Создайте package skeleton и хотя бы один реальный product test:

```bash
mkdir -p src/taskboard
: > src/taskboard/__init__.py

cat > tests/test_bootstrap.py <<'PY'
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import taskboard


class BootstrapTests(unittest.TestCase):
    def test_taskboard_package_can_be_imported(self):
        self.assertIsNotNone(taskboard)


if __name__ == "__main__":
    unittest.main()
PY
```

Теперь:

```bash
make check
make test
make test-template
```

должны PASS.

А:

```bash
make test-integration
echo $?
```

должен вернуть `NOT CONFIGURED`, exit 2.

Это **правильное bootstrap состояние**, а не незавершённый тест.

---

# 10. Заполните project memory

## Architecture overview

Опишите целевую схему:

```text
Browser
   |
   v
HTTP application
   |
   +----> HTML rendering
   |
   +----> TaskStore
              |
              v
      .demo-data/tasks.json
```

Но отдельно зафиксируйте фактическое bootstrap состояние: HTTP app, TaskStore и persistence ещё не реализованы.

## Invariants

Минимум:

1. пользовательский ввод HTML-escaped;
2. пустой title не сохраняется;
3. после появления TaskStore mutations идут через него;
4. persistence использует atomic replace;
5. corrupt JSON не приводит к silent reset;
6. server слушает только `127.0.0.1`;
7. `.demo-data/` не хранится в Git;
8. gates не дают zero-work false PASS;
9. документация не описывает будущее как уже существующее.

## Backlog

После bootstrap:

```text
Ready:
  DEMO-1

Planned:
  DEMO-2
  DEMO-3
  DEMO-4
```

И обязательно:

```text
DEMO-1 Task status = ready
DEMO-2/3/4 Task status = planned
```

`repo-doctor` проверит согласованность.

---

# 11. Создайте DEMO-1…DEMO-4

```bash
./scripts/new-task DEMO-1 "Показать список задач"
./scripts/new-task DEMO-2 "Добавить создание задачи"
./scripts/new-task DEMO-3 "Сохранять задачи между перезапусками"
./scripts/new-task DEMO-4 "Добавить завершение, фильтры и счётчики"
```

Acceptance Criteria берите из [`demo-project.md`](demo-project.md).

Риски:

```text
DEMO-1  A / delegated / E2
DEMO-2  B / required  / E2
DEMO-3  B / required  / E3
DEMO-4  A / delegated / E2/E3
```

---

# 12. Закройте bootstrap полным циклом

Проверьте:

```bash
./scripts/repo-doctor
make check
make test
make test-template
make telemetry-check

make test-integration
echo $?
```

Integration ожидаемо exit 2.

Сделайте implementation/bootstrap commit, затем clean-context independent review текущего HEAD.

Если review приводит к изменениям, reviewer должен повторно проверить новый HEAD.

После approved review:

- `DEMO-BOOTSTRAP` → `done`;
- TODO переносит bootstrap в Done;
- записывается собственная telemetry row;
- делается closure commit;
- ставится tag:

```bash
git tag demo/00-bootstrap
```

Tag ставится **после** review/evidence/telemetry closure, не до него.

---

# 13. DEMO-1…DEMO-4: используйте один и тот же цикл

Для каждой Task:

```text
1. clean/new agent session
2. repository context recovery
3. одна Ready Task
4. plan + risk + human gate + AC + verification
5. approval для B/C
6. minimal implementation
7. real tests/checks
8. self-review
9. implementation commit / fixed reviewable HEAD
10. independent clean-context review
11. fixes + repeat review when HEAD changed materially
12. evidence
13. Task/TODO state sync
14. telemetry
15. closure commit
16. checkpoint tag
```

Для Claude Code используйте `/develop`. Для других agents можно использовать `START_PROMPT.md` с тем же repository contract.

---

# 14. DEMO-1 — read-only board

Ожидаемый scope:

- `GET /` → 200;
- `Mini Task Board`;
- три seed tasks;
- title + priority;
- HTML escaping;
- bind только `127.0.0.1`.

Не входит:

- create;
- persistence;
- status mutation;
- filters.

Проверки:

```bash
make check
make test
```

Live:

```bash
PYTHONPATH=src python3 -m taskboard.app
curl -i http://127.0.0.1:8000/
ss -ltnp | grep 8000
```

После approved review/evidence/telemetry:

```bash
git tag demo/01-read-board
```

---

# 15. DEMO-2 — validated create flow

Risk B, human gate required.

Агент **до изменения кода** должен показать план и остановиться на подтверждении.

Acceptance Criteria:

- valid task добавляется;
- blank/whitespace title отклоняется;
- title > 80 отклоняется;
- unknown priority отклоняется;
- input escaped;
- DEMO-1 regression не ломается.

После closure:

```bash
git tag demo/02-create-task
```

Это лучший live segment презентации: видимая feature + mandatory human gate.

---

# 16. DEMO-3 — persistence и настоящий integration gate

Risk B, evidence E3.

Здесь впервые появляется реальный `make test-integration`.

Scope:

- TaskStore;
- JSON persistence;
- load on start;
- temporary file + atomic replace;
- corrupt JSON explicit failure;
- integration `create → restart → read`.

Только на этой итерации замените fail-closed placeholder:

```make
test-integration:
	@find tests -maxdepth 1 -type f -name 'test_integration_*.py' | grep -q . || \
		{ echo "NOT CONFIGURED: integration tests are not implemented yet" >&2; exit 2; }
	python3 -m unittest discover -s tests -p 'test_integration_*.py'
```

После этого `make test-integration` обязан PASS с реально найденным integration test.

Live evidence:

```text
create task
→ stop server
→ start server
→ task remains
```

После closure:

```bash
git tag demo/03-persistence
```

---

# 17. DEMO-4 — done/filter/counters

Risk A.

Acceptance Criteria:

- mark done;
- filters all/open/done;
- counters open/done;
- состояние корректно после reload;
- regression tests проходят.

После closure:

```bash
git tag demo/04-finished
```

---

# 18. Финальный аудит dry-run

```bash
git status

git --no-pager log --oneline --decorate -15

git --no-pager tag --list 'demo/*'

./scripts/repo-doctor
make check
make test
make test-template
make test-integration
make telemetry-check
make telemetry-summary

cat docs/backlog/TODO.md
ls -1 docs/reviews/
grep -H "Статус:" docs/tasks/DEMO-*.md
```

Ожидаемо:

```text
working tree clean
5 demo tags
5 Tasks done
5 independent review artifacts
all final gates PASS
integration tests PASS
telemetry содержит project cycles, а не source template history
```

Количество telemetry rows не обязано быть ровно числу Tasks: failed/partial/retry cycles должны сохраняться append-only.

---

# 19. Проверка context recovery

Откройте новую agent session и дайте только:

```text
Изучи репозиторий и скажи:
что уже реализовано,
какая следующая готовая задача
и чем она должна быть проверена.
Код пока не меняй.
```

Агент не должен использовать сведения прошлой беседы и не должен придумывать отсутствующий backlog.

---

# 20. Timed rehearsal

Рекомендуемый сценарий:

```text
1. показать demo/01-read-board
2. новая agent session
3. /develop или общий START_PROMPT contract
4. агент сам выбирает DEMO-2
5. показывает Risk B + required human gate
6. человек подтверждает
7. короткий live implementation / заранее ограниченный segment
8. показать review/evidence/telemetry
9. перейти на demo/03-persistence и показать restart evidence
10. перейти на demo/04-finished и показать финальный продукт
```

Plan B при проблемах модели/сети: честно перейти на заранее проверенный следующий checkpoint, не изображая незавершённую live-операцию как успешную.

---

# 21. Что считать успешным dry-run

Dry-run успешен, если подтверждено не только приложение, но и workflow:

- downstream initialization очистила source history;
- repository context восстановим clean-session агентом;
- Risk B реально вызывает human gate;
- zero-test false-green отсутствует;
- integration gate эволюционировал `NOT CONFIGURED → real E3`;
- independent review относится к закрываемому HEAD;
- Task/TODO statuses согласованы;
- telemetry append-only и project-specific;
- checkpoints воспроизводимы;
- финальное дерево чистое.

Если один из этих пунктов нарушен, фиксируйте это как finding template/process, а не скрывайте workaround'ом.
