# Телеметрия агентских циклов

## Зачем

Без телеметрии невозможно уверенно ответить:

- стали ли задачи выполняться быстрее;
- сколько времени уходит на review и переработку;
- какая модель выгоднее на разных типах задач;
- где AI экономит время человека, а где создаёт дополнительную работу;
- сколько стоит один завершённый цикл;
- насколько часто дефекты уходят дальше локальной проверки.

## Принцип

Каждая завершённая попытка разработки — успешная, частичная, неуспешная или прерванная — добавляет **одну строку JSON** в `.ai/telemetry/cycles.jsonl`.

Журнал append-only:

- старые строки не редактируются и не переставляются;
- исправление оформляется новой записью с новым `cycle_id`;
- CI проверяет, что существующий префикс файла не изменён;
- если относительно base ref изменился любой содержательный файл, CI требует хотя бы одну новую telemetry row.

Схема: `.ai/schemas/cycle.schema.json`.

## Поля

Обязательный минимум задаётся оператором:

```json
{
  "cycle_id": "2026-08-20T120000Z-TASK-17",
  "task_id": "TASK-17",
  "started_at": "2026-08-20T12:00:00Z",
  "ended_at": "2026-08-20T12:42:00Z",
  "result": "passed"
}
```

`record-cycle.py` автоматически добавляет доступные объективные данные:

- `duration_seconds` — из `started_at`/`ended_at`;
- `git_head` — HEAD на момент записи;
- `git_dirty` — состояние worktree;
- `changed_files` — tracked + untracked файлы на момент записи;
- `diff_lines` — сумма добавленных/удалённых строк tracked diff.

Эти поля не являются доказательством CI или live-среды, но уменьшают объём self-reported telemetry.

По возможности фиксируйте вручную только реально известные значения:

- `model`, `provider`, `agent_role`;
- `risk`;
- `input_tokens`, `output_tokens`;
- `tool_seconds`, `test_seconds`, `ci_seconds`;
- `review_rounds`, `review_p0`, `review_p1`;
- `parallel`;
- `human_minutes`;
- `estimated_cost_usd`;
- `live_validation_result`;
- `defects_found_pre_release`, `escaped_defects`;
- `evidence_ref`.

Не выдумывайте значения: если метрика недоступна, оставьте `null`.

## Какие показатели вычисляются

`scripts/telemetry-summary.py` строит агрегаты, соответствующие метрикам презентации:

- длительность цикла;
- lead time задачи до первого успешного завершения;
- throughput завершённых задач;
- число циклов на задачу и rework rate;
- число раундов review и P0/P1;
- доля параллельных циклов;
- live-validation pass rate;
- input/output tokens;
- оценочная стоимость моделей;
- human steering time;
- tool/test/CI runtime;
- escaped defects и defect escape rate, если зафиксированы данные о дефектах до и после выпуска.

## Запись

```bash
python scripts/record-cycle.py \
  --task TASK-17 \
  --started 2026-08-20T12:00:00Z \
  --ended 2026-08-20T12:42:00Z \
  --result passed \
  --risk B \
  --model example-model \
  --input-tokens 12000 \
  --output-tokens 2400 \
  --review-rounds 2 \
  --ci-seconds 55 \
  --human-minutes 8 \
  --estimated-cost-usd 0.42 \
  --live-validation-result passed \
  --evidence docs/tasks/TASK-17.md
```

Перед записью строка валидируется по `.ai/schemas/cycle.schema.json`.

## Проверка

```bash
python scripts/validate-telemetry.py
python scripts/telemetry-summary.py
```

В CI дополнительно выполняются две проверки относительно базового Git ref:

```bash
python scripts/check-telemetry-append-only.py --base-ref <ref>
python scripts/check-telemetry-required.py --base-ref <ref>
```

Первая запрещает переписывать историю, вторая запрещает содержательному изменению пройти без новой строки telemetry.

## Когда записывать

Запись телеметрии — часть рабочего цикла, а не факультативный отчёт:

1. цикл начался;
2. агент/человек выполняет работу;
3. результат зафиксирован как `passed`, `failed`, `partial` или `aborted`;
4. собраны реально доступные метрики;
5. `record-cycle.py` добавляет строку и автоматические Git/duration evidence;
6. только после этого цикл считается учтённым.

Если задача потребовала несколько попыток, каждая попытка получает собственный `cycle_id`, но сохраняет тот же `task_id`. Именно это позволяет измерять переработку.
