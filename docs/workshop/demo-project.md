# Demo Project — Mini Task Board

Этот документ задаёт **фиксированную демонстрационную спецификацию**, чтобы командная презентация была воспроизводимой и не зависела от того, что именно предложит AI в конкретной сессии.

Сценарий выступления: [`team-demo-scenario.md`](team-demo-scenario.md).

---

## 1. Почему выбран именно такой проект

Demo должен удовлетворять нескольким условиям одновременно:

- понятен любому разработчику без предметного контекста;
- итог можно увидеть глазами, а не только в тестах;
- каждая следующая итерация естественно продолжает предыдущую;
- есть read‑операция, write‑операция и работа с данными;
- весь проект запускается локально;
- установка сторонних библиотек не должна быть обязательной;
- тесты должны выполняться быстро;
- код достаточно мал, чтобы diff можно было понять во время презентации.

Поэтому предлагается **Mini Task Board** — маленький локальный веб‑трекер задач.

---

## 2. Технические ограничения demo

Рекомендуемый стек:

- Python 3.11+;
- только стандартная библиотека Python;
- `http.server` / `BaseHTTPRequestHandler` или эквивалентный минимальный HTTP слой;
- HTML/CSS без JavaScript framework;
- `unittest`;
- JSON‑файл для persistence;
- запуск на `127.0.0.1:8000`.

Почему без Flask/FastAPI/Node:

- не нужен `pip install` перед выступлением;
- нет риска сломанного registry/network;
- dependencies не отвлекают от repository workflow;
- приложение запускается практически на любой машине с Python.

Если команда преимущественно работает с другим стеком, сам сценарий можно перенести на него без изменения Task structure.

---

## 3. Целевая структура demo repository

После bootstrap:

```text
.
├── AGENTS.md
├── Makefile
├── src/
│   └── taskboard/
│       ├── __init__.py
│       ├── app.py
│       ├── model.py
│       └── store.py
├── tests/
│   ├── test_app.py
│   └── test_store.py
├── docs/
│   ├── architecture/
│   │   ├── overview.md
│   │   └── invariants.md
│   ├── backlog/
│   │   ├── ROADMAP.md
│   │   └── TODO.md
│   ├── tasks/
│   │   ├── DEMO-1.md
│   │   ├── DEMO-2.md
│   │   ├── DEMO-3.md
│   │   └── DEMO-4.md
│   └── reviews/
└── .ai/telemetry/cycles.jsonl
```

Runtime data можно хранить в:

```text
.demo-data/tasks.json
```

Эта директория должна быть в `.gitignore`.

---

## 4. Минимальная архитектура

```text
Browser
   |
   v
HTTP handler / app.py
   |
   +----> render HTML
   |
   +----> TaskStore
              |
              v
      .demo-data/tasks.json
```

### Инварианты demo

Зафиксируйте их в `docs/architecture/invariants.md`:

1. пользовательский ввод никогда не вставляется в HTML без escaping;
2. пустое название задачи не сохраняется;
3. изменение состояния выполняется только через `TaskStore`;
4. файл persistence должен обновляться атомарно;
5. повреждённый файл данных не должен молча перезаписываться пустым состоянием;
6. demo не слушает внешний интерфейс сети — только `127.0.0.1`.

Эти правила нужны не ради сложности приложения, а чтобы показать, что агент работает внутри заранее известных границ.

---

# 5. Bootstrap — до продуктовых итераций

Bootstrap лучше подготовить заранее, не тратить на него live‑время.

## Цель

Превратить generic template в конкретный маленький проект.

## Сделать заранее

- заполнить architecture overview/invariants;
- настроить `Makefile`;
- создать package structure;
- создать четыре Task;
- обновить ROADMAP/TODO;
- добавить `.gitignore` для runtime data;
- убедиться, что project gates больше не `NOT CONFIGURED`.

Рекомендуемые команды:

```make
check:
	python3 -m compileall -q src tests

test:
	python3 -m unittest discover -s tests -p 'test_*.py'

test-integration:
	python3 -m unittest discover -s tests -p 'test_integration_*.py'
```

В bootstrap тесты могут быть минимальными smoke tests.

Checkpoint:

```text
demo/00-bootstrap
```

---

# 6. Итерация DEMO-1 — показать список задач

**Risk:** A  
**Human gate:** delegated или required — для презентации удобнее delegated  
**Ожидаемый evidence:** E2

## Пользовательская ценность

При открытии браузера пользователь видит простой список задач.

## Scope

Реализовать только read‑only отображение.

Не входит:

- создание;
- удаление;
- изменение статуса;
- persistence.

## Acceptance Criteria

- `GET /` возвращает HTTP 200;
- страница содержит заголовок `Mini Task Board`;
- отображаются три seed‑задачи;
- для каждой задачи видны название и приоритет;
- HTML escaping проверен тестом;
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

## Что показать в Git

```bash
git show --stat demo/01-read-board
git diff demo/00-bootstrap..demo/01-read-board
```

Checkpoint:

```text
demo/01-read-board
```

---

# 7. Итерация DEMO-2 — создать задачу

**Risk:** B  
**Human gate:** required  
**Ожидаемый evidence:** E2

Это лучшая итерация для live‑показа.

## Почему B

Появляется write‑операция и новый HTTP/state contract. Риск невысокий в абсолютном смысле, но классификация B позволяет наглядно показать обязательный human gate и негативные сценарии.

## Пользовательская ценность

На странице появляется форма:

```text
Название: [________________________]
Приоритет: [low | medium | high]
[Добавить]
```

## Acceptance Criteria

- валидная задача добавляется и сразу отображается;
- пустое/whitespace‑only название отклоняется;
- название длиннее 80 символов отклоняется;
- неизвестный priority отклоняется;
- пользовательский ввод HTML‑escaped;
- read‑only поведение DEMO-1 не ломается;
- `make check` и `make test` проходят.

## Отрицательный сценарий для live

После успешного добавления отправьте пустую форму.

Ожидаемо пользователь видит понятную ошибку, состояние не меняется.

## Что должен сказать агент до реализации

Пример ожидаемого плана:

```text
Task: DEMO-2
Risk: B
Human gate: required

1. Добавить handler записи.
2. Добавить validation function.
3. Добавить form rendering.
4. Покрыть valid/invalid cases тестами.
5. Запустить make check && make test.
```

После этого человек подтверждает план.

Checkpoint:

```text
demo/02-create-task
```

---

# 8. Итерация DEMO-3 — persistence между перезапусками

**Risk:** B  
**Human gate:** required  
**Ожидаемый evidence:** E3

Эту итерацию лучше подготовить заранее и на выступлении показать только результат + tests/review.

## Пользовательская ценность

Созданные задачи не исчезают после перезапуска приложения.

## Scope

- JSON storage;
- загрузка при старте;
- атомарная запись;
- отдельный store abstraction.

Не входит:

- база данных;
- миграционная система;
- multi-user/concurrent server support.

## Acceptance Criteria

- созданная задача сохраняется на диск;
- после restart она снова отображается;
- запись идёт через temporary file + atomic replace;
- повреждённый JSON приводит к явной ошибке и не перезаписывается автоматически;
- runtime data не попадает в Git;
- unit tests store проходят;
- integration test `create → restart → read` проходит.

## Почему эта итерация важна для презентации

Она показывает отличие evidence level:

- unit test serialization — ещё не подтверждает restart flow;
- integration `create → stop → start → read` — более сильное доказательство.

Именно здесь удобно показать E2 vs E3.

## Live‑проверка

1. запустить приложение;
2. создать `Задача переживает restart`;
3. остановить сервер;
4. запустить снова;
5. обновить браузер;
6. задача осталась.

Checkpoint:

```text
demo/03-persistence
```

---

# 9. Итерация DEMO-4 — завершение и фильтрация

**Risk:** A  
**Human gate:** delegated допустим  
**Ожидаемый evidence:** E2/E3

## Пользовательская ценность

Demo начинает выглядеть как законченный маленький продукт.

## Acceptance Criteria

- задачу можно отметить выполненной;
- есть фильтры `all/open/done`;
- видны счётчики `Открыто` и `Выполнено`;
- фильтр сохраняет корректность после reload;
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

# 10. Backlog для demo

В `docs/backlog/TODO.md` перед выступлением:

```text
## Ready

- [ ] DEMO-2 — добавить создание задачи
- [ ] DEMO-3 — persistence между перезапусками
- [ ] DEMO-4 — завершение и фильтры

## Done

- [x] DEMO-1 — показать список задач
```

Для live‑демонстрации стартуйте с `demo/01-read-board`.

Так первая видимая страница уже существует, а агент получает одну понятную следующую Task.

---

# 11. Review artifacts

Минимально заранее подготовьте:

```text
docs/reviews/DEMO-2-review.md
docs/reviews/DEMO-3-review.md
```

Особенно полезен `DEMO-3-review.md`.

Reviewer должен проверить:

- atomic replace;
- corrupt file behavior;
- отсутствие silent data loss;
- path/runtime data isolation;
- соответствие integration evidence фактическому тесту.

Не нужно искусственно добавлять дефект ради шоу. Если reviewer не нашёл P0/P1 — это нормальный результат.

---

# 12. Telemetry demo data

В финальном checkpoint желательно иметь четыре реальные записи циклов.

На выступлении достаточно показать агрегат:

```bash
make telemetry-summary
```

Хороший пример результата:

```text
cycles: 4
passed: 4
avg duration: ...
review rounds: ...
A tasks: 2
B tasks: 2
```

Не подставляйте фиктивные token/cost значения. Если provider их не даёт — `null`.

---

# 13. Checkpoints и восстановление

Рекомендуемая история:

```text
00-bootstrap
    |
01-read-board
    |
02-create-task
    |
03-persistence
    |
04-finished
```

Создать tags можно так:

```bash
git tag demo/00-bootstrap <sha>
git tag demo/01-read-board <sha>
git tag demo/02-create-task <sha>
git tag demo/03-persistence <sha>
git tag demo/04-finished <sha>
```

Перед презентацией обязательно проверить каждый:

```bash
git switch --detach demo/04-finished
make check
make test
make test-integration
```

И затем вернуть старт:

```bash
git switch --detach demo/01-read-board
```

Если нужно вносить live изменения, лучше создать временную ветку:

```bash
git switch -c presentation/live demo/01-read-board
```

После выступления её можно удалить.

---

# 14. Проверка готовности demo

За день до презентации пройти checklist:

- [ ] demo repo открывается без доступа к внутренним корпоративным системам;
- [ ] Python version совместима;
- [ ] `make check` PASS;
- [ ] `make test` PASS;
- [ ] `make test-integration` PASS;
- [ ] `./scripts/repo-doctor` PASS;
- [ ] все checkpoints существуют;
- [ ] `demo/01-read-board` запускается;
- [ ] `demo/04-finished` запускается;
- [ ] браузер открывает `127.0.0.1:8000`;
- [ ] runtime data очищены перед началом;
- [ ] coding agent авторизован;
- [ ] запасной checkpoint для live DEMO-2 проверен;
- [ ] terminal font достаточно крупный;
- [ ] никакие tokens/secrets не попадут на экран.

---

# 15. Что будет считаться хорошим результатом

Сам Task Board специально прост.

Если аудитория обсуждает только HTML или Python, demo не достиг цели.

Хороший результат — когда после показа обсуждение смещается к вопросам:

- как заполнить repository context для нашего проекта;
- какие checks считать обязательными;
- как классифицировать risk;
- каким агентом делать author/reviewer;
- какие метрики действительно полезны;
- как использовать этот template в существующих репозиториях.

Именно эти вопросы означают, что команда увидела **инженерный процесс**, а не очередную демонстрацию генерации кода.
