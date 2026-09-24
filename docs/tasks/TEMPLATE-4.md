# TEMPLATE-4 — Brownfield adoption path

**Статус:** in progress  
**Риск:** B  
**Human gate:** required — подтверждён владельцем repository 2026-09-24  
**Владелец:** repository owner  
**Связанный эпик/этап:** template adoption  
**Requirements / ADR:** brownfield/existing-project onboarding; ADR n/a

## Зачем

Сделать existing repositories равноправным режимом использования template без пересоздания проекта и копирования демонстрационного layout.

## Объём

### Входит

- отдельный brownfield onboarding;
- read-only repository audit;
- staged adoption doctor;
- provider-neutral agent/subagent role contracts и Claude Code native subagents;
- `grill-me` skill для blocking ambiguities;
- source-of-truth mapping;
- existing build/test/CI reuse;
- external tracker + local execution contract;
- existing architecture/RFC/ADR semantics;
- brownfield fixture и regression tests;
- greenfield backward compatibility.

### Не входит

- универсальный parser всех build systems;
- автоматическое переписывание CI/docs/AI instructions;
- migration production layout;
- привязка общего процесса к одному AI provider или issue tracker.

## Критерии приёмки

- [ ] README явно предлагает greenfield и existing-project onboarding.
- [x] Есть полноценный brownfield guide и staged adoption model.
- [x] `repo-audit` выполняет безопасный read-only discovery и не выдаёт candidates за authoritative facts.
- [x] Existing repository не обязан повторять layout template.
- [x] Existing build/test/CI и tracker можно переиспользовать.
- [x] Existing AI instructions не перезаписываются tooling.
- [x] Есть explicit source-of-truth precedence и unresolved-conflict semantics.
- [x] Есть agent/subagent orchestration и `grill-me` skill; fallback prompt не является основным механизмом.
- [x] Есть brownfield fixture с source/tests/docs/CI/existing task.
- [x] Есть regression tests критической adoption mechanics.
- [ ] Greenfield/full template regression подтверждён CI.
- [x] `repo-doctor --adoption` различает ready / not configured / conflict без требования template skeleton.
- [x] Existing task может получить локальный execution contract без миграции backlog.
- [ ] Independent clean-context review exact final HEAD завершён, findings закрыты.

## План проверки

- new mechanics: `python3 -m unittest -v tests/test_brownfield_adoption.py`;
- full regression: `make test-template`;
- greenfield doctor: `./scripts/repo-doctor --template`;
- fail-closed gates: существующие template contract tests;
- GitHub CI exact HEAD;
- independent clean-context review exact final HEAD.

## Доказательства

- локально до публикации: 5/5 brownfield tests PASS в изолированной рабочей копии новых scripts/fixture/tests;
- GitHub CI: pending;
- greenfield regression: pending;
- exact-HEAD review: pending.

## Review

- self-review: pending final diff;
- independent review artifact: `docs/reviews/TEMPLATE-4-review.md` — pending;
- residual risk: provider-specific adapters требуют честной документации fallback semantics.

## Traceability

- owner requirement → TEMPLATE-4;
- TEMPLATE-4 → brownfield guide/tooling/agents/tests;
- Task → PR: pending.
