# Справочник команд

Краткий справочник основных команд шаблона. Полное объяснение процесса находится в [`../GETTING_STARTED.md`](../GETTING_STARTED.md).

## Инициализация downstream-проекта

После **Use this template** или локального копирования выполните:

```bash
./scripts/init-project "Название проекта"
```

Опционально задайте bootstrap Task явно:

```bash
./scripts/init-project "Mini Task Board" \
  --bootstrap-id DEMO-BOOTSTRAP \
  --bootstrap-title "Подготовить Mini Task Board к продуктовым итерациям"
```

Initializer очищает source `TEMPLATE-*`/`EXAMPLE-1` Tasks, inherited telemetry и template-only publish artifacts, затем создаёт честный project bootstrap context.

Повторный запуск блокируется. `--force` используйте только для осознанной реинициализации.

## Диагностика репозитория

```bash
./scripts/repo-doctor
```

Проверяет:

- обязательные файлы каркаса;
- согласованность `TODO Ready/In progress/Planned/Done` и `**Статус:**` Task;
- некоторые очевидные secret-like patterns.

Успех:

```text
Repository engineering skeleton looks consistent.
```

## Проверка tooling самого шаблона

```bash
make test-template
```

Запускает только `template_tests/`.

Это **не product tests**. Gate fail-closed при отсутствии `template_tests/` или matching tests.

## Project checks

```bash
make check
```

После bootstrap должен запускать реальные быстрые проверки: lint/static analysis/compile/format verification или эквивалент.

В исходном template и в свежем downstream до настройки намеренно возвращает `NOT CONFIGURED` с ненулевым кодом.

Gate не должен возвращать 0, если входные файлы/проверки отсутствуют.

## Unit/contract tests

```bash
make test
```

После настройки запускает основной набор product tests из `tests/`.

Если используется discovery, добавьте guard на наличие хотя бы одного matching test. Zero-test discovery с exit 0 — false-green.

## Integration/e2e tests

```bash
make test-integration
```

Пока реальных integration/e2e tests нет, оставляйте target `NOT CONFIGURED`.

Не заменяйте placeholder на пустой discovery только ради зелёного результата. Настраивайте target одновременно с появлением настоящего integration scenario.

## Создание Task

```bash
./scripts/new-task TASK-17 "Короткое название"
```

Создаёт `docs/tasks/TASK-17.md` из `.ai/templates/TASK.md`.

После перевода задачи между `Ready / In progress / Planned / Done` синхронно обновляйте поле `**Статус:**`. `repo-doctor` проверяет это автоматически.

## Запись telemetry

Минимум:

```bash
python3 scripts/record-cycle.py \
  --task TASK-17 \
  --started 2026-09-01T10:00:00Z \
  --ended 2026-09-01T10:30:00Z \
  --result passed
```

Практический вариант:

```bash
python3 scripts/record-cycle.py \
  --task TASK-17 \
  --started 2026-09-01T10:00:00Z \
  --ended 2026-09-01T10:30:00Z \
  --result passed \
  --risk B \
  --provider openai \
  --model example-model \
  --review-rounds 2 \
  --review-p0 0 \
  --review-p1 0 \
  --evidence docs/tasks/TASK-17.md
```

Допустимые результаты:

```text
passed
failed
partial
aborted
```

`passed` используйте только когда применимые gates действительно завершены. `NOT CONFIGURED` не является PASS.

Model/provider передавайте только когда они реально известны.

## Проверка telemetry

```bash
make telemetry-check
```

Эквивалент:

```bash
python3 scripts/validate-telemetry.py
```

## Сводка telemetry

```bash
make telemetry-summary
```

Эквивалент:

```bash
python3 scripts/telemetry-summary.py
```

## Проверка append-only telemetry

Обычно запускается CI:

```bash
python3 scripts/check-telemetry-append-only.py --base-ref <git-ref>
```

## Проверка обязательной новой telemetry row

Обычно запускается CI:

```bash
python3 scripts/check-telemetry-required.py --base-ref <git-ref>
```

## Проверка согласованности TODO/Task

Отдельно от `repo-doctor`:

```bash
python3 scripts/check-task-state.py
```

Пример ошибки:

```text
DEMO-1: TODO expects 'ready', task status is 'planned'
```

## Запуск AI-инструмента

Из корня repository:

```bash
opencode
codex
claude
```

Для Claude Code:

```text
/develop
/iterate
```

`/develop` — обычный полный цикл одной bounded Task. `/iterate` — небольшое архитектурное/планировочное изменение.

## Перед commit

После полной настройки проекта:

```bash
./scripts/repo-doctor
make check
make test
make test-template
make telemetry-check
git status
git diff
```

Если integration gate уже реально настроен:

```bash
make test-integration
```

Если он ещё не применим, ожидаемый `NOT CONFIGURED` должен быть явно зафиксирован в Task evidence.

## Типичный Git flow

```bash
git switch -c task/TASK-17
git status
git diff
git add -A
git commit -m "TASK-17 short description"
git push -u origin task/TASK-17
```

Имена веток и commit convention заменяйте на принятые в вашей команде.
