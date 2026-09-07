# Справочник команд

Краткий справочник основных команд шаблона. Полное объяснение процесса находится в [`../GETTING_STARTED.md`](../GETTING_STARTED.md).

## Диагностика репозитория

```bash
./scripts/repo-doctor
```

Проверяет наличие обязательных файлов каркаса и некоторые очевидные secret-like patterns.

Успех:

```text
Repository engineering skeleton looks consistent.
```

## Проверка tooling самого шаблона

```bash
make test-template
```

Запускает тесты служебной механики repository engineering template.

Это **не тесты вашего продукта**.

## Project checks

```bash
make check
```

После настройки проекта должен запускать реальные быстрые проверки: lint/static analysis/compile/format verification или эквивалент.

В исходном шаблоне намеренно возвращает:

```text
NOT CONFIGURED
```

с ненулевым кодом.

## Unit/contract tests

```bash
make test
```

После настройки должен запускать основной набор автоматических тестов проекта.

## Integration/e2e tests

```bash
make test-integration
```

Используйте для integration/e2e, когда они применимы.

## Создание Task

```bash
./scripts/new-task TASK-17 "Короткое название"
```

Создаёт:

```text
docs/tasks/TASK-17.md
```

из `.ai/templates/TASK.md`.

Если файл уже существует, скрипт завершится ошибкой и не перезапишет его.

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

`passed` используйте только когда применимые gates действительно завершены.

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

Показывает агрегированные метрики по записанным cycles.

## Проверка append-only telemetry

Обычно запускается CI. Для диагностики вручную:

```bash
python3 scripts/check-telemetry-append-only.py --base-ref <git-ref>
```

## Проверка обязательной новой telemetry row

Обычно запускается CI:

```bash
python3 scripts/check-telemetry-required.py --base-ref <git-ref>
```

Если между base ref и текущим состоянием есть содержательные изменения, должна появиться новая telemetry row.

## Запуск AI-инструмента

Из корня репозитория, если соответствующий CLI установлен:

```bash
opencode
codex
claude
```

После запуска используйте `START_PROMPT.md`.

Для Claude Code:

```text
/develop
/iterate
```

## Перед commit

Минимальный набор после полной настройки проекта:

```bash
./scripts/repo-doctor
make check
make test
make test-template
make telemetry-check
git status
git diff
```

При необходимости добавьте:

```bash
make test-integration
```

## Типичный Git flow

```bash
git switch -c task/TASK-17
git status
git diff
git add -A
git commit -m "TASK-17 short description"
git push -u origin task/TASK-17
```

Имена веток и формат commit message можно заменить на принятый в вашей команде стандарт.
