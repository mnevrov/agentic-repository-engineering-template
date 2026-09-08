# Быстрая 10-минутная демонстрация шаблона

Этот сценарий подходит, когда нужно быстро объяснить **механику template repository**, но нет времени показывать несколько продуктовых итераций.

Для полноценной командной презентации с небольшим работающим проектом используйте:

- [`team-demo-scenario.md`](team-demo-scenario.md) — рекомендуемый 15-минутный сценарий выступления;
- [`demo-project.md`](demo-project.md) — спецификация Mini Task Board и четырёх демонстрационных итераций.

---

## 0:00–2:00 — Репозиторий как память

Покажите:

- `AGENTS.md`;
- `docs/INDEX.md`;
- архитектуру и инварианты;
- ROADMAP/TODO.

Ключевой тезис: новый агент восстанавливает контекст из репозитория, а не из старой беседы.

---

## 2:00–4:00 — Одна Task

Откройте один файл из `docs/tasks/` и покажите:

- ID и scope;
- Acceptance Criteria;
- risk A/B/C;
- human gate;
- способ проверки;
- evidence.

Ключевой тезис: агент не получает расплывчатое «сделай фичу», а ограниченную проверяемую инженерную задачу.

---

## 4:00–6:00 — Рабочий цикл

Покажите `docs/process/development-cycle.md` или `.claude/commands/develop.md`.

Сфокусируйтесь только на цепочке:

```text
контекст → одна Task → план → human gate
→ реализация → реальные проверки
→ self-review → independent review
→ evidence → telemetry → commit/PR
```

---

## 6:00–8:00 — Review и доказательства

Покажите:

- `docs/process/code-review.md`;
- `.ai/templates/REVIEW.md`;
- `docs/process/evidence-ladder.md`.

Объясните один пример:

```text
unit test               → E2
integration/restart flow → E3
```

Главный тезис: сообщение модели «готово» не повышает уровень доказательств.

---

## 8:00–10:00 — Измеримость

Покажите существующую telemetry:

```bash
make telemetry-check
make telemetry-summary
tail -3 .ai/telemetry/cycles.jsonl
```

Обратите внимание на task ID, result, duration, review/evidence reference.

Финальный тезис:

> Template не заменяет coding agent. Он превращает работу агента в повторяемый инженерный процесс, состояние которого хранится и проверяется в Git.

Если после этого есть ещё 10–15 минут, переходите к Mini Task Board из `team-demo-scenario.md`: он показывает тот же процесс уже на нескольких видимых продуктовых итерациях.
