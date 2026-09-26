# TEMPLATE-5 — Подготовить документацию template к митапу

**Статус:** in progress  
**Риск:** A  
**Human gate:** delegated  
**Источник:** подготовка публичного template к митапу

## Зачем

После PR #5 инженерный contract Greenfield/Brownfield актуален, но публичная навигация и workshop-документация всё ещё могли создавать ложное впечатление, что demo уже прогнан и meetup-version можно фиксировать.

## Scope

- сделать явный выбор Greenfield/Brownfield на публичных entry points;
- добавить короткий audience-facing meetup landing;
- сделать HANDOUT самодостаточным;
- привести publication guide к фактическому public/template состоянию;
- отделить presenter runbooks от audience onboarding;
- ввести единый фактический статус dry-run/rehearsal;
- явно запретить meetup tag/release до успешного тестового прогона;
- пометить ROADMAP/TODO как placeholders нового проекта.

## Out of scope

- создавать meetup tag/release;
- утверждать demo/checkpoints как проверенные;
- проводить сам тестовый прогон;
- менять process semantics или tooling;
- создавать/публиковать demo repository без фактического dry-run.

## Acceptance Criteria

- [x] README не отправляет всех новых читателей только в Greenfield.
- [x] `docs/MEETUP.md` даёт короткий маршрут Greenfield/Brownfield.
- [x] HANDOUT содержит public URL и практические next steps.
- [x] `docs/workshop/STATUS.md` явно говорит `DRY-RUN NOT COMPLETED`.
- [x] publication guide не предлагает удалять append-only telemetry и корректно описывает fail-closed template gates.
- [x] presenter runbooks явно отделены от подтверждённого результата.
- [x] ROADMAP/TODO помечены как template placeholders.
- [ ] Полный demo dry-run выполнен.
- [ ] Timed rehearsal выполнена.
- [ ] STATUS обновлён на verified.
- [ ] Meetup tag/release создан только после этих gates.

## Verification

До dry-run эта Task не может иметь `passed`: документационный этап должен оставаться `partial`.

Проверки текущего docs-only change:

- template CI на exact HEAD;
- проверка ссылок/команд по diff;
- независимый review документации перед merge либо явное исключение;
- после merge — реальный runbook `docs/workshop/real-repository-dry-run.md`.

## Evidence

Текущий evidence level: documentation/static review only. Реальный demo evidence появится только после dry-run.
