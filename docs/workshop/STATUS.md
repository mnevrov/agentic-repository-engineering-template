# Workshop / meetup status

Этот файл — единственный источник текущего статуса demo и подготовки к выступлению.

## Текущий статус

**DRY-RUN NOT COMPLETED**

- Template repository опубликован и используется как GitHub Template.
- Brownfield/Greenfield process documentation существует.
- Технический template CI и repository-level tests не заменяют презентационный dry-run.
- Отдельный demo repository/checkpoints не считаются подтверждёнными, пока не пройден полный runbook.
- Meetup tag/release **не создаётся** до успешного тестового прогона.
- Слайды не должны ссылаться на «финальный meetup commit/tag», пока этот статус не изменён.

## Что должно быть проверено

Полный runbook:

[`real-repository-dry-run.md`](real-repository-dry-run.md)

Минимальный readiness gate:

- [ ] demo repository реально создан из template;
- [ ] initial fail-closed state проверен;
- [ ] реальные project gates настроены;
- [ ] DEMO-1…DEMO-4 или утверждённый эквивалент пройдены;
- [ ] Human Gate наблюдался;
- [ ] positive + negative acceptance scenarios проверены;
- [ ] restart/integration evidence проверено;
- [ ] independent review artifacts существуют;
- [ ] telemetry validation + append-only checks проходят;
- [ ] новая agent session восстанавливает context;
- [ ] checkpoints реально checkout'ятся;
- [ ] Plan B после незавершённой live-попытки проверен;
- [ ] browser/user smoke test пройден;
- [ ] timed rehearsal проведена;
- [ ] QR и публичные ссылки проверены с отдельного устройства.

## После успешного dry-run

Только после заполнения evidence:

1. зафиксировать результат прогона;
2. обновить этот файл на **VERIFIED FOR MEETUP**;
3. при необходимости опубликовать demo repository/checkpoints;
4. обновить audience-facing ссылки;
5. создать meetup tag/release;
6. указать exact tag/commit в презентации.

До этого любые workshop checkpoints являются планом/спецификацией, а не подтверждённым результатом.
