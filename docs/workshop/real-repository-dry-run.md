# Контрольный прогон на реальном репозитории

Эта инструкция описывает, как **один раз полностью пройти Agentic Repository Engineering Template на отдельном настоящем Git-репозитории**, а затем использовать получившийся репозиторий для репетиции командной демонстрации.

Цель прогона — не просто получить работающий Mini Task Board. Нужно проверить, что весь процесс действительно работает на практике:

- новый проект можно создать из template без скрытых ручных шагов;
- агент восстанавливает контекст из Git;
- project gates не дают ложный PASS;
- одна Task действительно ограничивает scope;
- human gate срабатывает там, где должен;
- acceptance criteria можно подтвердить воспроизводимыми проверками;
- independent review отделён от self-review;
- evidence соответствует фактической силе проверки;
- telemetry остаётся append-only и проходит CI;
- после нескольких итераций новый агент понимает текущее состояние проекта;
- Git checkpoints позволяют безопасно провести презентацию даже при проблемах с моделью или сетью.

Связанные документы:

- [`demo-project.md`](demo-project.md) — фиксированная спецификация Mini Task Board и DEMO-1…DEMO-4;
- [`team-demo-scenario.md`](team-demo-scenario.md) — рекомендуемый сценарий 15-минутного выступления;
- [`../GETTING_STARTED.md`](../GETTING_STARTED.md) — общий onboarding шаблона.

---

# 1. Два разных вида прогона

Не смешивайте их.

## 1.1. Полный контрольный прогон

Проводится один раз при подготовке demo repository.

В нём:

- создаётся настоящий новый репозиторий из template;
- bootstrap выполняется как отдельный цикл;
- DEMO-1…DEMO-4 реально выполняются последовательно;
- запускаются настоящие проверки;
- создаются реальные commits/PR или эквивалентные зафиксированные циклы;
- создаются review artifacts;
- записывается реальная telemetry;
- фиксируются demo checkpoints.

Это проверка **самого инженерного процесса**.

## 1.2. Репетиция выступления

Проводится после полного прогона.

В ней:

- не нужно повторно генерировать все четыре фичи;
- стартуем с заранее подготовленных checkpoints;
- только DEMO-2 можно повторить live;
- проверяем тайминг, переключение между терминалом/браузером/Git;
- проверяем Plan B;
- измеряем, укладывается ли демонстрация в 15 минут.

Это проверка **устойчивости презентации**.

---

# 2. Ожидаемый конечный результат

После полного прогона должен существовать отдельный GitHub repository, например:

```text
agentic-template-demo
```

В нём должны быть:

```text
AGENTS.md
CLAUDE.md
README.md
Makefile
src/taskboard/...
tests/...
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

и Git checkpoints:

```text
demo/00-bootstrap
demo/01-read-board
demo/02-create-task
demo/03-persistence
demo/04-finished
```

Финальное приложение должно запускаться локально и визуально показывать результат всех четырёх итераций.

---

# 3. Что понадобится

На машине ведущего заранее должны работать:

```bash
git --version
python3 --version
make --version
```

Рекомендуется Python 3.11+.

Также должен быть установлен хотя бы один coding agent:

- OpenCode;
- Codex CLI;
- Claude Code;
- другой агент, способный читать и менять файлы Git repository.

Для контрольного прогона лучше использовать **тот же инструмент, который планируется показывать команде**.

Если на выступлении предполагается OpenCode — полный dry-run также лучше сделать через OpenCode.

---

# 4. Создание реального demo repository

## Вариант A — через GitHub Template

Это предпочтительный вариант, потому что именно его будет использовать команда.

1. Откройте `agentic-repository-engineering-template`.
2. Нажмите **Use this template**.
3. Создайте новый repository, например:

```text
agentic-template-demo
```

4. Репозиторий можно сделать private, если он нужен только для внутренней репетиции.
5. Клонируйте его:

```bash
git clone <URL-DEMO-REPOSITORY>
cd agentic-template-demo
```

## Вариант B — локальная копия

Используйте только если GitHub Template пока недоступен:

```bash
git clone https://github.com/mnevrov/agentic-repository-engineering-template.git agentic-template-demo
cd agentic-template-demo
rm -rf .git
git init
```

После этого настройте `origin` на новый пустой repository.

---

# 5. Сохраните исходное состояние

Сразу после создания:

```bash
git status
git log --oneline --max-count=5
```

Рабочее дерево должно быть чистым.

Запустите только template checks:

```bash
./scripts/repo-doctor
make test-template
```

Ожидаемо обе команды проходят.

Теперь специально выполните:

```bash
make check
make test
make test-integration
```

В нетронутом template они должны завершиться примерно так:

```text
NOT CONFIGURED: ...
```

с ненулевым кодом.

Это **успешная проверка fail-closed поведения**, а не дефект.

Зафиксируйте для себя:

```text
[PASS] template tooling работает
[PASS] project gates ещё не настроены и не дают ложный зелёный результат
```

Если `make check` или `make test` возвращают 0 до настройки проекта — остановите прогон: template contract нарушен.

---

# 6. Bootstrap как отдельный цикл

Bootstrap — тоже содержательное изменение repository. Не выполняйте его «вне процесса».

Создайте Task:

```bash
./scripts/new-task DEMO-BOOTSTRAP "Подготовить Mini Task Board к продуктовым итерациям"
```

Откройте:

```text
docs/tasks/DEMO-BOOTSTRAP.md
```

Заполните минимум:

```text
Risk: A
Human gate: delegated
```

## Acceptance Criteria bootstrap

Рекомендуемый набор:

- [ ] `make check` выполняет реальную проверку Python исходников;
- [ ] `make test` запускает unit tests;
- [ ] `make test-integration` запускает integration tests;
- [ ] заполнено `docs/architecture/overview.md`;
- [ ] заполнены реальные demo invariants;
- [ ] созданы DEMO-1…DEMO-4;
- [ ] ROADMAP/TODO отражают порядок DEMO-1 → DEMO-4;
- [ ] runtime data исключены из Git;
- [ ] `repo-doctor`, `make test-template`, `make check`, `make test` проходят.

---

# 7. Настройте project gates

Для Mini Task Board достаточно стандартной библиотеки Python.

В `Makefile` замените placeholders, например на:

```make
check:
	python3 -m compileall -q src tests

test:
	python3 -m unittest discover -s tests -p 'test_*.py'

test-integration:
	python3 -m unittest discover -s tests -p 'test_integration_*.py'
```

Важно: не используйте команду вида:

```make
check:
	@echo PASS
```

Это снова создаст false-green gate.

После изменения:

```bash
make check
make test
```

На bootstrap-этапе допустимо иметь минимальные smoke tests, но команды должны реально что-то проверять.

---

# 8. Заполните project memory

## 8.1. Architecture overview

В `docs/architecture/overview.md` опишите фактическую систему:

```text
Browser
   |
   v
HTTP handler
   |
   v
TaskStore
   |
   v
.demo-data/tasks.json
```

Явно разделите:

- что существует уже сейчас;
- что будет добавлено в DEMO-1…DEMO-4.

## 8.2. Architecture invariants

Зафиксируйте минимум:

1. пользовательский ввод HTML-escaped;
2. пустое название задачи не сохраняется;
3. изменение данных идёт через TaskStore;
4. persistence использует atomic replace;
5. повреждённый JSON не приводит к silent reset;
6. HTTP server слушает только `127.0.0.1`.

## 8.3. ROADMAP

Пример:

```text
Milestone 1 — Read-only board
Milestone 2 — Validated write flow
Milestone 3 — Durable storage
Milestone 4 — Finished demo UX
```

## 8.4. TODO

После bootstrap:

```text
## Ready

- [ ] DEMO-1 — показать список задач
- [ ] DEMO-2 — добавить создание задачи
- [ ] DEMO-3 — persistence между перезапусками
- [ ] DEMO-4 — завершение и фильтры
```

---

# 9. Создайте четыре Task

Используйте:

```bash
./scripts/new-task DEMO-1 "Показать список задач"
./scripts/new-task DEMO-2 "Добавить создание задачи"
./scripts/new-task DEMO-3 "Сохранять задачи между перезапусками"
./scripts/new-task DEMO-4 "Добавить завершение, фильтры и счётчики"
```

Acceptance Criteria берите из [`demo-project.md`](demo-project.md).

Не сокращайте их перед контрольным прогоном: смысл dry-run в том, чтобы проверить реальный contract Task → implementation → evidence.

---

# 10. Завершите bootstrap

Запустите:

```bash
./scripts/repo-doctor
make test-template
make check
make test
make telemetry-check
```

Если integration tests пока отсутствуют, `make test-integration` всё равно должен запускать реальную test discovery и завершаться корректно.

Проведите self-review bootstrap diff:

```bash
git diff
```

Проверьте:

- placeholders в Makefile действительно удалены;
- документация описывает Mini Task Board, а не generic template;
- нет продуктовой реализации DEMO-1;
- `.demo-data/` исключена из Git.

Запишите цикл telemetry согласно `docs/process/telemetry.md`.

После этого:

```bash
git add -A
git commit -m "DEMO-BOOTSTRAP prepare task board project"
git tag demo/00-bootstrap
```

Если используется remote:

```bash
git push origin HEAD
git push origin demo/00-bootstrap
```

## Контрольная точка

```bash
git status
```

Ожидаемо:

```text
working tree clean
```

---

# 11. Принцип проведения DEMO-1…DEMO-4

Для каждой Task повторяется один и тот же шаблон:

```text
1. новая/чистая сессия агента
2. восстановление repository context
3. выбор только одной Task
4. план + risk + AC + verification
5. human gate, если required
6. реализация
7. реальные checks/tests
8. self-review
9. independent review
10. evidence
11. update Task/TODO
12. telemetry
13. commit
14. tag checkpoint
```

Не пропускайте шаги на первом полном dry-run, даже если они кажутся избыточными для маленького demo.

Именно сейчас проверяется методика.

---

# 12. DEMO-1 — read-only board

Вернитесь к bootstrap checkpoint:

```bash
git checkout main
```

Убедитесь, что `DEMO-1` — первая Ready Task.

Запустите **новую** сессию coding agent из корня repository.

Первый prompt:

```text
Следуй AGENTS.md и project memory в Git.
Найди следующую готовую Task.
Сначала покажи:
- Task ID и название;
- scope;
- Acceptance Criteria;
- risk и human gate;
- затрагиваемые компоненты;
- короткий план;
- какие проверки будут доказательством результата.
Код до этого не меняй.
```

## Что проверяем в поведении агента

До изменения кода он должен:

- найти DEMO-1;
- не предлагать сразу DEMO-2…4;
- прочитать architecture/invariants;
- назвать read-only scope;
- назвать `make check` и `make test`;
- не заявлять о persistence/create flow.

Если агент пытается сделать весь Task Board целиком — остановите его.

Запишите это как наблюдение dry-run.

### Для DEMO-1

Risk A может иметь:

```text
Human gate: delegated
```

Поэтому после корректного плана агент может продолжить без отдельного подтверждения, если Task это явно разрешает.

После реализации выполните или проверьте вывод агента:

```bash
make check
make test
```

Затем вручную запустите приложение.

Рекомендуемая команда должна быть зафиксирована в README demo repository, например:

```bash
python3 -m taskboard.app
```

или эквивалентная реальная команда проекта.

Откройте:

```text
http://127.0.0.1:8000
```

Должны отображаться три seed-задачи.

Проверьте отдельно HTML escaping тестом.

---

# 13. Review DEMO-1

Self-review выполняет author session.

Independent review выполняйте:

- в новой clean-context сессии;
- по возможности другой моделью;
- либо другим reviewer-инструментом.

Передайте reviewer только:

- `docs/tasks/DEMO-1.md`;
- architecture invariants;
- diff;
- реальные результаты checks/tests.

Используйте `REVIEW_PROMPT.md`.

Сохраните результат:

```text
docs/reviews/DEMO-1-review.md
```

Для DEMO-1 допустим `approved` при отсутствии блокирующих findings.

После review обновите Task evidence.

Запишите telemetry.

Коммит:

```bash
git add -A
git commit -m "DEMO-1 render task board"
git tag demo/01-read-board
```

Запушьте branch/tag.

---

# 14. Проверка смены сессии после DEMO-1

Это обязательный тест template philosophy.

Полностью закройте author session.

Откройте новый coding agent session.

Не пересказывайте ему историю.

Дайте только:

```text
Изучи репозиторий.
Кратко скажи:
1. что уже реализовано;
2. какая следующая Ready Task;
3. её risk/human gate;
4. какие архитектурные ограничения для неё важны;
5. чем она должна быть проверена.
Код не меняй.
```

Ожидаемо:

```text
DEMO-1 done
DEMO-2 next
risk B
human gate required
нужна validation positive/negative cases
```

Если новый агент не может это восстановить без прошлого чата — зафиксируйте пробел в project memory и исправьте документацию **до дальнейших итераций**.

Это один из главных критериев успешного dry-run.

---

# 15. DEMO-2 — validated create flow

Это наиболее важная итерация для будущей live-презентации.

Запускайте её особенно аккуратно.

Task должна содержать:

```text
Risk: B
Human gate: required
```

## Ожидаемое поведение агента

Он должен остановиться после плана.

Ожидаемый план примерно такой:

```text
1. Добавить form/POST handler.
2. Выделить validation.
3. Проверить empty/whitespace title.
4. Проверить >80 chars.
5. Проверить invalid priority.
6. Сохранить DEMO-1 read behavior.
7. Запустить make check и make test.
```

До подтверждения не должно быть изменений файлов.

Проверьте:

```bash
git status
```

Если файлы уже изменены до human gate — отметьте это как FAIL процесса.

Подтверждение:

```text
План подтверждаю. Выполняй только DEMO-2.
```

## Acceptance-проверка

После реализации:

```bash
make check
make test
```

Запустите приложение.

В браузере:

1. создайте `Подготовить демонстрацию`;
2. убедитесь, что задача появилась;
3. отправьте пустое название;
4. убедитесь, что состояние не изменилось;
5. попробуйте значение >80 символов;
6. убедитесь, что оно отклоняется;
7. при наличии прямого HTTP теста проверьте invalid priority.

### Evidence

Для DEMO-2 ожидаемо:

```text
E2
```

потому что positive/negative behavior подтверждён автоматическими unit/contract tests.

Ручной браузерный показ полезен, но сам по себе не повышает evidence автоматически до E3.

---

# 16. Review DEMO-2

Independent reviewer должен обратить внимание на:

- HTML escaping;
- server-side validation;
- отсутствие обхода validation прямым POST;
- regression DEMO-1;
- соответствие фактических тестов заявленным AC.

Сохраните:

```text
docs/reviews/DEMO-2-review.md
```

Если найдены P1/P0 — исправьте их и повторите review согласно процессу risk B.

После закрытия findings:

- обновите Task;
- обновите TODO;
- запишите telemetry;
- сделайте commit.

```bash
git add -A
git commit -m "DEMO-2 add validated task creation"
git tag demo/02-create-task
```

Этот checkpoint **обязателен**, потому что именно с него удобно спасать live-демонстрацию.

---

# 17. Контрольный тест DEMO-2 как live-фрагмента

До перехода к DEMO-3 выполните маленькую репетицию.

1. Вернитесь на:

```bash
git checkout demo/01-read-board
```

2. Запустите новую agent session.
3. Дайте тот же короткий prompt будущей презентации.
4. Засеките время до появления корректного плана.
5. Не обязательно повторно ждать полную генерацию: цель — проверить, что агент быстро восстанавливает context и human gate выглядит понятно.

Запишите:

```text
Время до Task/risk/plan: ___
Время до human gate: ___
```

Если уже на этом этапе live-фрагмент занимает больше 3–4 минут до начала реализации, на выступлении используйте более короткий prompt или сильнее подготовленный checkpoint.

После мини-репетиции вернитесь на main/последний commit.

---

# 18. DEMO-3 — persistence

Эта итерация проверяет наиболее важную часть evidence ladder в demo.

Task:

```text
Risk: B
Human gate: required
Expected evidence: E3
```

До реализации агент должен назвать как минимум:

- TaskStore abstraction;
- JSON persistence;
- atomic replace;
- corrupt data behavior;
- restart integration test.

Если предлагается просто `open(..., 'w')` без atomic strategy — план не подтверждайте.

## Unit tests

Минимум:

- serialize/deserialize valid tasks;
- invalid/corrupt JSON behavior;
- atomic write path;
- TaskStore API.

## Integration test

Обязательный flow:

```text
create task
→ terminate application/store instance
→ create a new instance / restart
→ read task
→ task exists
```

Именно он даёт основание заявлять E3 для persistence flow.

---

# 19. Ручная restart-проверка DEMO-3

После автоматических tests:

1. удалите старые demo runtime data либо используйте чистую временную директорию;
2. запустите приложение;
3. создайте:

```text
Задача переживает restart
```

4. остановите процесс `Ctrl+C`;
5. убедитесь, что JSON существует;
6. снова запустите приложение;
7. обновите браузер;
8. задача должна остаться.

Затем отдельно проверьте corrupt file behavior на тестовом пути, а не на единственном demo data файле.

Ожидаемо приложение:

- сообщает явную ошибку;
- не превращает corrupted storage в пустой список молча;
- не перезаписывает повреждённый файл пустым состоянием.

---

# 20. Review DEMO-3

Это самый полезный review artifact для выступления.

Reviewer должен проверить:

- atomic replace реализован фактически;
- temporary file находится на совместимом filesystem path;
- corrupted JSON не приводит к silent data loss;
- runtime data не tracked Git;
- integration test действительно пересоздаёт runtime/store state;
- заявленный E3 соответствует реальному тесту.

Сохраните:

```text
docs/reviews/DEMO-3-review.md
```

На выступлении именно этот файл удобно показать аудитории.

После завершения:

```bash
git add -A
git commit -m "DEMO-3 persist tasks atomically"
git tag demo/03-persistence
```

---

# 21. DEMO-4 — finished UX

Последняя итерация должна быть маленькой.

Она не должна превращаться в redesign проекта.

Scope:

- mark done;
- filters `all/open/done`;
- counters;
- regression tests.

Не добавляйте:

- пользователей;
- authentication;
- REST API «на будущее»;
- JavaScript framework;
- database;
- CSS redesign вне минимально необходимого.

Это хороший тест способности агента соблюдать scope.

Если агент предлагает дополнительную архитектуру — вынесите её как future TODO, но не реализуйте в DEMO-4.

После проверки:

```bash
make check
make test
make test-integration
```

Запустите финальное приложение и визуально проверьте:

- counters;
- filters;
- done state;
- create flow;
- persistence после reload/restart.

После review/evidence/telemetry:

```bash
git add -A
git commit -m "DEMO-4 add task filters and counters"
git tag demo/04-finished
```

---

# 22. Проверка итоговой Git-истории

Выполните:

```bash
git log --oneline --decorate --graph --max-count=15
```

История должна читаться примерно так:

```text
DEMO-4 add task filters and counters      (demo/04-finished)
DEMO-3 persist tasks atomically           (demo/03-persistence)
DEMO-2 add validated task creation        (demo/02-create-task)
DEMO-1 render task board                  (demo/01-read-board)
DEMO-BOOTSTRAP prepare task board project (demo/00-bootstrap)
```

Точные SHA не важны.

Важно, чтобы каждая итерация была отдельной и понятной.

---

# 23. Проверка telemetry

Запустите:

```bash
make telemetry-check
make telemetry-summary
```

Затем:

```bash
tail -n 10 .ai/telemetry/cycles.jsonl
```

Проверьте:

- bootstrap имеет собственный cycle;
- DEMO-1…DEMO-4 представлены отдельными cycles;
- failed/partial attempts не удалены;
- отсутствующие token/cost значения остались `null`, а не придуманы;
- review rounds соответствуют реальности;
- risk A/B соответствует Task;
- evidence_ref существует.

Важно: dry-run будет более убедительным, если telemetry содержит не только идеальные `passed` rows.

Если реально была неудачная попытка, оставьте её в append-only журнале.

Не очищайте telemetry ради красивой презентации.

---

# 24. Проверка CI на GitHub

После каждого важного checkpoint push должен запускать repository CI.

Минимально финальный `demo/04-finished` должен иметь зелёный CI.

Проверьте:

- repo-doctor;
- telemetry validation;
- telemetry append-only contract;
- telemetry-required contract;
- template tests;
- project `make check`;
- project `make test`.

Если demo repository использует PR flow — полезно хотя бы DEMO-2 или DEMO-3 провести через настоящий PR, чтобы убедиться, что проверки работают именно на merge ref, а не только локально.

---

# 25. Полная проверка новой сессии на финальном состоянии

Откройте совершенно новую agent session после DEMO-4.

Дайте только:

```text
Изучи этот репозиторий как новый разработчик.
Не меняй код.
Ответь:
1. что это за система;
2. какие четыре продуктовые итерации уже завершены;
3. какие архитектурные инварианты действуют;
4. какие проверки являются project gates;
5. где находятся evidence и review;
6. есть ли сейчас Ready Task;
7. что подтверждено E2, а что E3.
```

Ожидаемо агент должен ответить по repository contents без старого чата.

Если он:

- путает completed/ready tasks;
- не знает, где review;
- не понимает persistence invariant;
- утверждает E3 там, где есть только unit tests;

то project memory требует исправления до презентации.

---

# 26. Проверка воспроизводимости другим человеком

По возможности попросите коллегу, который не участвовал в подготовке, сделать только следующее:

```bash
git clone <DEMO-REPO>
cd agentic-template-demo
./scripts/repo-doctor
make check
make test
```

Затем дать ему ссылку только на:

```text
docs/INDEX.md
```

и попросить ответить:

- как запустить приложение;
- какая архитектура;
- где история Task;
- где review DEMO-3;
- где telemetry.

Если это занимает больше нескольких минут или требует устных подсказок, onboarding demo repository недостаточно самодостаточен.

---

# 27. Подготовка checkpoints для выступления

Проверьте наличие tags:

```bash
git tag --list 'demo/*'
```

Ожидаемо:

```text
demo/00-bootstrap
demo/01-read-board
demo/02-create-task
demo/03-persistence
demo/04-finished
```

Проверьте каждый tag:

```bash
git show --no-patch --oneline demo/00-bootstrap
git show --no-patch --oneline demo/01-read-board
git show --no-patch --oneline demo/02-create-task
git show --no-patch --oneline demo/03-persistence
git show --no-patch --oneline demo/04-finished
```

Затем реально checkout каждый checkpoint и убедитесь, что состояние соответствует названию.

Особенно:

```bash
git checkout demo/01-read-board
```

должно давать состояние **до DEMO-2**, с которого безопасно начинать live-фрагмент.

---

# 28. Подготовьте отдельную rehearsal branch

Чтобы live-репетиция не портила готовые checkpoints:

```bash
git checkout -b rehearsal/demo-2 demo/01-read-board
```

Именно на этой branch можно повторять DEMO-2 сколько угодно.

После репетиции её можно удалить:

```bash
git checkout main
git branch -D rehearsal/demo-2
```

Tags при этом остаются неизменными.

---

# 29. Репетиция 15-минутного выступления

После полного dry-run откройте [`team-demo-scenario.md`](team-demo-scenario.md).

Поставьте настоящий таймер.

Нельзя останавливать таймер на переключение окон или команд.

## До старта таймера

Подготовьте:

- терминал №1 — repository;
- терминал №2 — server;
- браузер — `127.0.0.1:8000`;
- coding agent — новая чистая session;
- editor — `docs/tasks/DEMO-2.md` и `docs/reviews/DEMO-3-review.md`;
- branch `rehearsal/demo-2` на checkpoint `demo/01-read-board`.

Проверьте:

```bash
git status
make check
make test
```

---

# 30. Что измерять во время репетиции

Запишите фактические времена:

| Этап | Целевое время | Фактическое |
|---|---:|---:|
| вводная проблема | 1:30 | |
| Task/project memory | 1:30 | |
| live DEMO-2 | 4:00 | |
| новая session/context restore | 2:00 | |
| DEMO-3/4 checkpoints | 2:30 | |
| review/evidence | 1:30 | |
| telemetry | 1:00 | |
| финал | 1:00 | |

Суммарно целимся примерно в 15 минут.

Если live DEMO-2 регулярно занимает больше 5 минут, сократите live-часть, а не остальные ключевые идеи.

---

# 31. Критерий переключения на Plan B

На выступлении заранее определите правило.

Например:

> Если через 60–90 секунд после отправки prompt агент не сформировал корректный Task/risk/plan или provider явно нестабилен, переключаемся на checkpoint.

Не принимайте решение импровизационно после нескольких минут ожидания.

Plan B:

```bash
git reset --hard demo/02-create-task
make check
make test
```

или checkout заранее подготовленного checkpoint.

Затем покажите браузер и продолжайте сценарий.

Обязательно проговорите аудитории:

```text
Чтобы не тратить время на latency модели, переключаюсь на заранее сохранённый результат этой же итерации.
```

Это лучше, чем делать вид, что live generation прошла успешно.

---

# 32. Проверка восстановления после неудачной live-попытки

Специально смоделируйте один сбой на репетиции.

Например:

1. начните DEMO-2;
2. остановите агента после частичного изменения;
3. выполните:

```bash
git status
git diff
```

4. покажите, что рабочее состояние можно безопасно отбросить:

```bash
git reset --hard demo/01-read-board
```

5. затем переключиться на:

```bash
git checkout demo/02-create-task
```

Цель — убедиться, что fallback проверен практически, а не только описан в документации.

---

# 33. Проверка браузерного demo

На финальном checkpoint выполните пользовательский smoke test:

## DEMO-1 regression

- список отображается;
- seed data видны.

## DEMO-2 regression

- valid create работает;
- empty title отклоняется;
- long title отклоняется;
- invalid priority отклоняется.

## DEMO-3 regression

- задача сохраняется после restart;
- runtime file не tracked Git.

## DEMO-4

- done работает;
- filters работают;
- counters корректны;
- reload не ломает состояние.

Проверка должна занимать не больше нескольких минут.

---

# 34. Проверка чистоты demo repository

Перед презентацией:

```bash
git status
git ls-files .demo-data
```

Ожидаемо:

```text
working tree clean
```

а `git ls-files .demo-data` ничего не выводит.

Также проверьте отсутствие случайных:

- secrets;
- токенов;
- provider config;
- локальных абсолютных путей;
- персональных данных;
- больших временных файлов.

Запустите:

```bash
./scripts/repo-doctor
```

---

# 35. Проверка независимости от сети

После того как demo repository клонирован и coding agent не нужен, приложение должно работать без внешней сети.

Проверьте хотя бы один раз:

1. отключите ненужный network/VPN либо просто убедитесь, что runtime не обращается наружу;
2. выполните:

```bash
make check
make test
```

3. запустите приложение;
4. откройте локальный browser URL.

Demo runtime не должен требовать:

- `pip install`;
- npm registry;
- внешнюю БД;
- API key;
- облачный сервис.

Сеть нужна только live coding agent, и именно для этого существует checkpoint fallback.

---

# 36. Матрица результатов полного dry-run

После прогона заполните таблицу.

| Проверка | PASS/FAIL | Комментарий |
|---|---|---|
| создание нового repo из template | | |
| repo-doctor сразу после clone | | |
| initial gates fail-closed | | |
| bootstrap project gates | | |
| agent восстанавливает context | | |
| одна Task за цикл | | |
| human gate DEMO-2 | | |
| negative AC DEMO-2 | | |
| restart integration DEMO-3 | | |
| corrupt data behavior | | |
| independent review artifacts | | |
| evidence E2/E3 не завышен | | |
| telemetry append-only | | |
| CI green | | |
| new session after DEMO-4 | | |
| checkpoints восстанавливаются | | |
| Plan B проверен практически | | |
| 15-minute rehearsal укладывается | | |

Не считайте прогон успешным, если критические пункты остаются неизвестными.

---

# 37. Что считать блокирующим дефектом template/demo

Перед выступлением исправьте обязательно:

- project gates дают false-green;
- агент не может определить текущую Task из repository;
- DEMO-2 не останавливается на required human gate;
- corrupted persistence silently теряет данные;
- заявленный E3 не имеет integration test;
- telemetry можно перезаписать без обнаружения CI;
- checkpoint не соответствует ожидаемой итерации;
- demo runtime требует сеть или незадокументированную dependency;
- новая session требует устного пересказа истории проекта;
- Plan B не восстанавливает рабочее состояние.

---

# 38. Что не является блокирующим

Можно осознанно принять до выступления:

- косметические различия UI;
- небольшой P2/P3 review finding с документированным residual risk;
- отсутствие token/cost telemetry, если provider её не предоставляет;
- отсутствие отдельного PR на DEMO-1 при наличии корректного commit/evidence;
- небольшие отклонения от 15 минут, если ключевые блоки остаются понятными.

---

# 39. Рекомендуемый журнал репетиции

Создайте локальный или repository документ, например:

```text
docs/workshop/rehearsal-notes.md
```

Для каждой попытки:

```text
Дата:
Coding agent/model:
Начальный checkpoint:
Полное время:
Время DEMO-2 live:
Был ли fallback:
Что было непонятно аудитории/наблюдателю:
Где потребовалась ручная подсказка агенту:
Что исправить до следующего прогона:
```

Не нужно превращать rehearsal notes в постоянную архитектурную документацию. Это рабочий журнал подготовки выступления.

---

# 40. Минимум два контрольных прогона

Рекомендуется провести:

## Прогон A — инженерный

Без попытки уложиться во время.

Цель:

- найти дефекты процесса;
- проверить Task/AC/evidence;
- получить checkpoints.

## Прогон B — презентационный

С таймером 15 минут.

Цель:

- проверить темп;
- убрать лишние переходы;
- проверить live DEMO-2;
- проверить fallback.

Если есть возможность, проведите ещё один прогон перед человеком, который не видел подготовку.

---

# 41. Финальный preflight за день до выступления

В demo repository:

```bash
git fetch --all --tags
git status
./scripts/repo-doctor
make test-template
make check
make test
make test-integration
make telemetry-check
```

Проверьте tags:

```bash
git tag --list 'demo/*'
```

Проверьте final checkpoint:

```bash
git checkout demo/04-finished
```

Запустите приложение.

Проверьте browser smoke test.

Вернитесь на live start:

```bash
git checkout -B rehearsal/demo-2 demo/01-read-board
```

После этого **не обновляйте зависимости и не меняйте demo без причины**.

---

# 42. Финальный preflight непосредственно перед выступлением

За несколько минут до начала:

```bash
git status
make check
make test
```

Должно быть чисто и зелено.

Запустите server на нужном checkpoint и убедитесь, что browser открывается.

Затем остановите server, если по сценарию его нужно запускать при аудитории.

Откройте заранее:

- repository root;
- `docs/tasks/DEMO-2.md`;
- `docs/reviews/DEMO-3-review.md`;
- terminal с крупным шрифтом;
- browser;
- чистую agent session.

Очистите terminal от лишней истории, которая может отвлекать или содержать секреты.

---

# 43. Критерий «demo готово к презентации»

Demo можно считать готовым, если одновременно выполнено следующее:

1. отдельный repository создан из template;
2. initial fail-closed state подтверждён;
3. bootstrap прошёл через реальные gates;
4. DEMO-1…DEMO-4 реально реализованы отдельными итерациями;
5. human gate DEMO-2 фактически наблюдался;
6. DEMO-2 имеет positive + negative tests;
7. DEMO-3 имеет настоящий restart integration test;
8. independent review artifacts существуют как минимум для DEMO-2/DEMO-3;
9. telemetry проходит validation и append-only checks;
10. final GitHub CI зелёный;
11. новая session восстанавливает состояние без старого чата;
12. все `demo/*` checkpoints проверены checkout'ом;
13. fallback после незавершённой live-попытки реально проверен;
14. финальное приложение запускается без внешних runtime dependencies;
15. timed rehearsal укладывается примерно в 15 минут.

Если пункт 11 не выполняется, это особенно важно исправить: именно repository-as-memory является центральной ценностью подхода.

---

# 44. Короткая последовательность для повторного прогона

После того как полный инженерный dry-run уже выполнен, следующая репетиция сводится к:

```bash
git fetch --all --tags
git checkout -B rehearsal/demo-2 demo/01-read-board
./scripts/repo-doctor
make check
make test
```

Далее:

```text
1. новая agent session
2. короткий prompt
3. DEMO-2 plan
4. human gate
5. live implementation или fallback
6. browser positive/negative scenario
7. новая session → restore context
8. checkout DEMO-3 → restart evidence
9. checkout DEMO-4 → final UI
10. review artifact
11. telemetry summary
12. Git log + финальный тезис
```

Полный сценарий по минутам находится в [`team-demo-scenario.md`](team-demo-scenario.md).

---

# 45. Главный принцип контрольного прогона

Не оптимизируйте первый dry-run под красивую презентацию.

Если агент ошибся, review нашёл проблему, CI упал или telemetry получила `partial/failed` цикл — **сохраните это как реальный инженерный след**.

Первый прогон нужен именно для того, чтобы увидеть слабые места процесса.

Красивые checkpoints для выступления создаются после того, как процесс уже доказал свою воспроизводимость.
