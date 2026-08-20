# Телеметрия агентских циклов

## Зачем

Без телеметрии невозможно уверенно ответить:

- стали ли задачи выполняться быстрее;
- сколько времени уходит на review и переработку;
- какая модель выгоднее на разных типах задач;
- где AI экономит время человека, а где создаёт дополнительную работу.

## Формат

Каждая завершённая попытка добавляет **одну строку JSON** в `.ai/telemetry/cycles.jsonl`.
Не редактируйте старые строки — добавляйте корректирующую запись новым cycle_id.

Схема: `.ai/schemas/cycle.schema.json`.

## Минимальные поля

```json
{
  "cycle_id": "2026-08-20T120000Z-TASK-17",
  "task_id": "TASK-17",
  "started_at": "2026-08-20T12:00:00Z",
  "ended_at": "2026-08-20T12:42:00Z",
  "result": "passed"
}
```

## Полезные метрики

- lead time по задаче;
- throughput задач за неделю;
- число повторных циклов;
- review rounds и P0/P1;
- tool/test/CI runtime;
- live-validation pass rate;
- input/output tokens и стоимость;
- human steering time;
- defect escape rate;
- доля параллельных циклов.

## Запись

```bash
python scripts/record-cycle.py \
  --task TASK-17 \
  --started 2026-08-20T12:00:00Z \
  --ended 2026-08-20T12:42:00Z \
  --result passed \
  --risk B \
  --model example-model \
  --review-rounds 2 \
  --evidence docs/tasks/TASK-17.md
```
