# Пример первого агентского цикла

Этот пример показывает минимальный практический путь после создания нового проекта из шаблона. Полная инструкция находится в [`../GETTING_STARTED.md`](../GETTING_STARTED.md).

## Исходное состояние

Предположим:

- шаблон уже скопирован в новый Git-репозиторий;
- `repo-doctor` и `make test-template` проходят;
- `make check` и `make test` ещё не настроены;
- первая задача — подключить реальные project gates.

## 1. Создать Task

```bash
./scripts/new-task TASK-1 "Настроить реальные команды проверки проекта"
```

Создан файл:

```text
docs/tasks/TASK-1.md
```

Для этой Task можно указать:

```text
Риск: A
Human gate: delegated
```

если человек заранее разрешил bounded документационно/tooling изменение.

Пример Acceptance Criteria:

```text
AC-1: make check запускает реальные проверки проекта и возвращает 0 только при успехе.
AC-2: make test запускает реальные unit/contract tests.
AC-3: make test-template по-прежнему проходит.
AC-4: README содержит актуальные команды запуска проверок.
```

## 2. Запустить coding agent

Из корня проекта:

```bash
opencode
```

или:

```bash
codex
```

или:

```bash
claude
```

После запуска передайте `START_PROMPT.md` и явно назовите `TASK-1`.

## 3. Проверить план

До реализации агент должен показать:

- выбранную Task;
- scope;
- Acceptance Criteria;
- риск;
- human gate;
- изменяемые файлы;
- способ проверки.

Если `Human gate: required`, подтвердите план явным сообщением.

## 4. Внести минимальные изменения

Для этой Task обычно меняются:

- `Makefile`;
- возможно CI workflow;
- README/engineering docs;
- сама Task с evidence.

Не начинайте одновременно реализовывать product feature.

## 5. Выполнить проверки

Например:

```bash
./scripts/repo-doctor
make check
make test
make test-template
```

Если `make check` или `make test` всё ещё выводят `NOT CONFIGURED`, Acceptance Criteria не выполнены.

## 6. Self-review

Просмотрите diff и убедитесь, что:

- нет product changes вне scope;
- команды действительно запускаются;
- exit code отражает реальный результат;
- тесты не были ослаблены;
- документация совпадает с новым поведением.

## 7. Independent review

Откройте новую чистую сессию другого агента или модели.

Передайте:

- `docs/tasks/TASK-1.md`;
- релевантные invariants;
- diff;
- результаты команд.

Используйте `REVIEW_PROMPT.md`.

Сохраните ответ как:

```text
docs/reviews/TASK-1-review.md
```

Если review недоступен и ответственный человек явно решил временно пропустить gate, не называйте review `approved`: зафиксируйте исключение, а telemetry cycle оставьте `partial`.

## 8. Заполнить evidence

В Task укажите фактически выполненные команды и уровень доказательства.

Если были реальные unit tests, это обычно минимум E2 для соответствующей логики. Не переносите автоматически E2 на внешнюю интеграцию или эксплуатационное поведение.

## 9. Записать telemetry

После завершения попытки:

```bash
python3 scripts/record-cycle.py \
  --task TASK-1 \
  --started 2026-09-01T10:00:00Z \
  --ended 2026-09-01T10:30:00Z \
  --result passed \
  --risk A \
  --provider example-provider \
  --model example-model \
  --review-rounds 1 \
  --review-p0 0 \
  --review-p1 0 \
  --evidence docs/tasks/TASK-1.md
```

Проверить:

```bash
make telemetry-check
make telemetry-summary
```

## 10. Commit / PR

```bash
git status
git diff
git add -A
git commit -m "TASK-1 configure project checks"
```

В PR укажите Task, Acceptance Criteria, реальные проверки, evidence level, review artifact и остаточные риски.

## Что дальше

После TASK-1 можно переходить к первой продуктовой Task. Теперь каждый следующий агентский цикл использует те же project gates и не требует повторной настройки шаблона.
