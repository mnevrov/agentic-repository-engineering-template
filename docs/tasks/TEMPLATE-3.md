# TEMPLATE-3 — Сценарий командной демонстрации

**Статус:** in review  
**Риск:** A  
**Human gate:** delegated  
**Владелец:** repository owner  
**Связанный эпик/этап:** template adoption / team presentation  
**Requirements / ADR:** n/a

## Зачем

Шаблон планируется презентовать команде. Нужен короткий, воспроизводимый и наглядный сценарий, который показывает не только документы template, но и результат нескольких последовательных агентских итераций на маленьком работающем проекте.

## Объём

### Входит

- рекомендуемый 15-минутный сценарий выступления;
- небольшой визуальный demo project;
- 3–4 последовательные Task;
- рекомендация, какую итерацию проводить live;
- checkpoints для надёжного выступления;
- демонстрация новой сессии агента с восстановлением контекста из Git;
- human gate, tests, review/evidence, telemetry;
- plan B на случай проблем с provider/network;
- подробный runbook полного контрольного прогона на отдельном реальном репозитории;
- критерии готовности demo к презентации и timed rehearsal;
- сокращённый 10-минутный вариант.

### Не входит

- реализация самого отдельного demo repository в этой Task;
- выбор корпоративного coding-agent provider;
- подготовка слайдов;
- измерение реальной производительности моделей.

## Критерии приёмки

- [x] AC-1: есть сценарий, укладывающийся примерно в 15 минут.
- [x] AC-2: demo состоит из нескольких маленьких итераций с видимым пользовательским результатом.
- [x] AC-3: определено, что показывать live, а что через заранее подготовленные checkpoints.
- [x] AC-4: одна итерация демонстрирует обязательный human gate и негативный acceptance scenario.
- [x] AC-5: отдельный момент показывает восстановление контекста в новой сессии агента.
- [x] AC-6: есть пример задачи с более сильным evidence level, чем unit tests.
- [x] AC-7: предусмотрен plan B без имитации live-разработки.
- [x] AC-8: сценарий не требует внешних runtime dependencies для demo application.
- [x] AC-9: есть подробная инструкция полного dry-run на новом реальном repository, включая bootstrap, DEMO-1…4, CI, review, evidence, telemetry, checkpoints, fallback и критерий готовности к выступлению.

## Архитектурные ограничения

- template остаётся provider-neutral;
- demo должен показывать ценность repository workflow, а не benchmark конкретной модели;
- live часть должна быть короткой и восстанавливаемой;
- пример не должен требовать доступа к корпоративной инфраструктуре.

## План проверки

- unit: n/a;
- integration: `repo-doctor`, template tests и CI после публикации;
- manual: проверить последовательность сценария и runbook; фактический полный rehearsal выполняется уже на отдельном demo repository;
- ожидаемый evidence level: E1 для сценария/runbook + E2 для структуры template/CI.

## Доказательства

- команды: GitHub Actions после публикации PR и последующих обновлений;
- результаты: CI на исходной версии PR прошёл; после добавления dry-run runbook требуется повторный CI на текущем SHA;
- артефакты:
  - `docs/workshop/team-demo-scenario.md`;
  - `docs/workshop/demo-project.md`;
  - `docs/workshop/real-repository-dry-run.md`;
  - `docs/workshop/10-minute-demo.md`;
- фактический evidence level: E1 для содержимого документации, E2 после зелёного template CI;
- что не проверено: фактический полный прогон отдельного demo repository и timed rehearsal.

## Review

- self-review: сценарий и runbook проверены на последовательность, timing, fallback и соответствие process docs;
- independent review artifact: внешняя CodeRabbit review в этом repository не запускается автоматически из-за ограничения текущей конфигурации/репозитория; отдельное исключение пока не зафиксировано;
- остаточные замечания: следующей Task собрать фактический demo repository и выполнить runbook, записав реальные отклонения.

## Traceability

- запрос владельца на сценарий командной презентации и подробный тестовый прогон → TEMPLATE-3;
- TEMPLATE-3 → workshop docs;
- Task → PR: `#3 docs: add reproducible team demo scenario`;
