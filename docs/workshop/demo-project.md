# Mini Task Board — спецификация demo-проекта

Этот документ фиксирует маленький продукт, на котором демонстрируется Agentic Repository Engineering workflow. Он специально достаточно прост, чтобы команда понимала результат без предметного контекста, и достаточно содержателен для нескольких независимых итераций.

## 1. Цель

Mini Task Board — локальный однопользовательский веб-трекер задач на Python standard library.

Demo показывает не сложность приложения, а процесс:

```text
repository context
→ bounded Task
→ risk / human gate
→ implementation
→ real checks
→ independent review
→ evidence
→ telemetry
→ Git checkpoint
```

## 2. Технические ограничения

- Python 3.10+;
- только standard library;
- без pip/runtime network dependencies;
- HTTP server слушает только `127.0.0.1:8000`;
- HTML/CSS без JS framework;
- `unittest`;
- JSON persistence появляется только в DEMO-3;
- runtime data: `.demo-data/tasks.json`.

`.demo-data/` должна быть в `.gitignore`.

## 3. Целевая архитектура

```text
Browser
   |
   v
HTTP application
   |
   +----> render HTML
   |
   +----> TaskStore
              |
              v
      .demo-data/tasks.json
```

Целевая схема не означает, что все компоненты существуют в bootstrap. `docs/architecture/overview.md` обязан отдельно описывать фактическое состояние каждой итерации.

## 4. Инварианты demo

1. пользовательский ввод никогда не вставляется в HTML без escaping;
2. пустой/whitespace-only title не сохраняется;
3. после появления TaskStore mutations выполняются через него;
4. persistence использует temporary file + atomic replace;
5. corrupt JSON не приводит к silent reset/overwrite;
6. server слушает только `127.0.0.1`;
7. `.demo-data/` не хранится в Git;
8. project gates не дают zero-work/zero-test false PASS;
9. будущая архитектура не документируется как уже реализованная.

---

# 5. Bootstrap

Bootstrap выполняется заранее и тоже проходит как отдельная Task.

После создания downstream repository:

```bash
./scripts/init-project "Mini Task Board" \
  --bootstrap-id DEMO-BOOTSTRAP \
  --bootstrap-title "Подготовить Mini Task Board к продуктовым итерациям"
```

## Bootstrap scope

- очистить inherited source history через initializer;
- настроить реальные `make check` и `make test`;
- оставить `make test-integration` fail-closed;
- создать `src/taskboard`;
- создать минимум один реальный product smoke test;
- заполнить architecture/invariants;
- создать DEMO-1…DEMO-4;
- обновить ROADMAP/TODO;
- исключить `.demo-data/` из Git.

## Проверенные gate semantics

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

`make test-template` отдельно запускает `template_tests/`.

Важно: пустой `unittest discover` может вернуть 0. Поэтому отсутствие tests не должно маскироваться как PASS.

Checkpoint после полного closure bootstrap:

```text
demo/00-bootstrap
```

---

# 6. DEMO-1 — показать список задач

**Risk:** A  
**Human gate:** delegated  
**Ожидаемый evidence:** E2

## Пользовательская ценность

При открытии браузера пользователь видит read-only список задач.

## Scope

- HTTP application;
- `GET /`;
- HTML rendering;
- seed data;
- title + priority;
- HTML escaping;
- localhost-only bind.

Не входит:

- создание;
- удаление;
- изменение статуса;
- persistence.

## Acceptance Criteria

- `GET /` возвращает HTTP 200;
- страница содержит `Mini Task Board`;
- отображаются три seed tasks;
- для каждой видны title и priority;
- HTML escaping подтверждён test;
- server слушает только `127.0.0.1`;
- `make check` и `make test` проходят.

## Seed data

```text
Подготовить демонстрацию — high
Проверить CI — medium
Обновить README — low
```

## Визуальный результат

```text
Mini Task Board

[high]   Подготовить демонстрацию
[medium] Проверить CI
[low]    Обновить README
```

Checkpoint после review/evidence/telemetry closure:

```text
demo/01-read-board
```

---

# 7. DEMO-2 — создать задачу

**Risk:** B  
**Human gate:** required  
**Ожидаемый evidence:** E2

Это рекомендуемая live-итерация презентации.

## Почему Risk B

Появляется write-operation и новый HTTP/state contract. Категория B позволяет явно показать mandatory human gate.

## Scope

- form UI;
- POST/write handler;
- validation;
- in-memory state;
- отображение созданной задачи.

Не входит persistence между restart.

## Acceptance Criteria

- valid task добавляется и сразу отображается;
- blank/whitespace-only title отклоняется;
- title > 80 символов отклоняется;
- unknown priority отклоняется;
- input HTML-escaped;
- DEMO-1 regression не ломается;
- `make check` и `make test` проходят.

## Human gate

До реализации агент должен показать:

```text
Task: DEMO-2
Risk: B
Human gate: required
plan
verification
```

и дождаться явного подтверждения.

## Negative live scenario

После successful create отправьте пустую форму. Состояние не должно меняться, пользователь должен увидеть понятную ошибку.

Checkpoint:

```text
demo/02-create-task
```

---

# 8. DEMO-3 — persistence между перезапусками

**Risk:** B  
**Human gate:** required  
**Ожидаемый evidence:** E3

## Пользовательская ценность

Созданные задачи переживают restart приложения.

## Scope

- TaskStore;
- JSON storage;
- load on start;
- temporary file + atomic replace;
- explicit corrupt-data failure;
- настоящий integration restart flow.

Не входит:

- база данных;
- migrations;
- multi-user/concurrent server support.

## Acceptance Criteria

- созданная задача сохраняется на диск;
- после restart снова отображается;
- запись использует temporary file + atomic replace;
- corrupt JSON вызывает явную ошибку и не перезаписывается пустым state;
- runtime data не попадает в Git;
- TaskStore unit tests проходят;
- integration `create → restart → read` проходит.

## Именно здесь включается integration gate

До DEMO-3 `make test-integration` был `NOT CONFIGURED`.

Теперь target получает guard и настоящий test suite:

```make
test-integration:
	@find tests -maxdepth 1 -type f -name 'test_integration_*.py' | grep -q . || \
		{ echo "NOT CONFIGURED: integration tests are not implemented yet" >&2; exit 2; }
	python3 -m unittest discover -s tests -p 'test_integration_*.py'
```

## Live evidence

1. запустить приложение;
2. создать `Задача переживает restart`;
3. остановить server;
4. запустить снова;
5. обновить браузер;
6. задача осталась.

Checkpoint:

```text
demo/03-persistence
```

---

# 9. DEMO-4 — завершение и фильтрация

**Risk:** A  
**Human gate:** delegated допустим  
**Ожидаемый evidence:** E2/E3

## Acceptance Criteria

- задачу можно отметить выполненной;
- есть filters `all/open/done`;
- видны counters `Открыто` и `Выполнено`;
- состояние/фильтрация корректны после reload;
- все regression tests проходят.

## Финальный экран

```text
Mini Task Board

Открыто: 2    Выполнено: 1

[Все] [Открытые] [Выполненные]

[high]   Подготовить демонстрацию      [Выполнить]
[medium] Проверить CI                   [Выполнить]
[low]    Обновить README                ✓

Название: [________________]
Приоритет: [medium]
[Добавить]
```

Checkpoint:

```text
demo/04-finished
```

---

# 10. Backlog semantics

В каждый момент только действительно готовые Tasks находятся в `Ready`.

После bootstrap:

```text
Ready:
  DEMO-1

Planned:
  DEMO-2
  DEMO-3
  DEMO-4
```

После DEMO-1:

```text
Ready:
  DEMO-2

Done:
  DEMO-BOOTSTRAP
  DEMO-1
```

Поле `**Статус:**` в Task обязано совпадать с секцией TODO. `repo-doctor` проверяет это автоматически.

---

# 11. Review artifacts

Каждая Task получает independent clean-context review:

```text
docs/reviews/DEMO-BOOTSTRAP-review.md
docs/reviews/DEMO-1-review.md
docs/reviews/DEMO-2-review.md
docs/reviews/DEMO-3-review.md
docs/reviews/DEMO-4-review.md
```

Reviewer проверяет фиксированный HEAD. Если после review внесены существенные изменения, новый HEAD требует повторной независимой проверки до closure.

---

# 12. Telemetry

Каждый фактический cycle записывается append-only. Retry/failed/partial attempts не удаляются.

Для presentation особенно полезны:

- duration;
- result;
- risk;
- review rounds;
- P0/P1;
- live validation;
- escaped defects;
- model/provider, если они реально известны.

Не заполняйте model/provider догадкой.

---

# 13. Рекомендуемый presentation flow

```text
demo/00-bootstrap
        ↓
demo/01-read-board      ← старт live
        ↓
demo/02-create-task     ← Risk B + human gate
        ↓
demo/03-persistence     ← E3 restart evidence
        ↓
demo/04-finished        ← финальный продукт
```

DEMO-2 — основной live segment. DEMO-3 лучше показать как готовый restart evidence. `demo/04-finished` — Plan B и финальное состояние.

---

# 14. Финальный audit

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
ls docs/reviews
grep -H "Статус:" docs/tasks/DEMO-*.md
```

Успешный dry-run означает:

- чистое дерево;
- пять closure checkpoints;
- все Tasks `done`;
- все final gates PASS;
- integration gate действительно проверяет restart flow;
- independent review есть для каждой Task;
- telemetry содержит только downstream project cycles;
- agent context восстанавливается без истории предыдущего чата.
