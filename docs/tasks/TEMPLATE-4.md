# TEMPLATE-4 — Brownfield adoption path

**Статус:** merged; symlink finding исправлен и локально независимо перепроверен; exact-head CI ожидает нового commit
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

- [x] README явно предлагает greenfield и existing-project onboarding.
- [x] Есть полноценный brownfield guide и staged adoption model.
- [x] `repo-audit` выполняет безопасный read-only discovery и не выдаёт candidates за authoritative facts. Finding о symlink escape исправлен и подтверждён в TEMPLATE-6; exact-head CI остаётся отдельным evidence gate ниже.
- [x] Existing repository не обязан повторять layout template.
- [x] Existing build/test/CI и tracker можно переиспользовать.
- [x] Existing AI instructions не перезаписываются tooling.
- [x] Есть explicit source-of-truth precedence и unresolved-conflict semantics.
- [x] Есть agent/subagent orchestration и `grill-me` skill; fallback prompt не является основным механизмом.
- [x] Есть brownfield fixture с source/tests/docs/CI/existing task.
- [x] Есть regression tests критической adoption mechanics.
- [x] Greenfield/full template regression подтверждался GitHub CI на implementation HEADs; final review-fix HEAD требует обычного повторного CI.
- [x] `repo-doctor --adoption` различает ready / not configured / conflict без требования template skeleton.
- [x] Existing task может получить локальный execution contract без миграции backlog.
- [ ] Independent clean-context re-review нового exact final HEAD после round-8 fix без открытого AC-blocking finding.

## План проверки

- focused adoption tests через `make test-template`;
- full regression: `make test-template`;
- greenfield doctor: `./scripts/repo-doctor --template`;
- fail-closed gates: существующие template contract tests;
- GitHub CI exact HEAD;
- independent CodeRabbit clean-context full review / re-review exact HEAD.

## Доказательства

- до первого независимого review: GitHub Actions `Repository Doctor` run `36005074403` PASS на `3bff1620cfe5ce64c59ae017f91efd85b479dd70`;
- independent review round 1: CodeRabbit, exact `3bff1620cfe5ce64c59ae017f91efd85b479dd70`, 4 Major findings;
- findings verified by author and fixed with targeted regression tests in the following commit;
- final exact-HEAD CI/re-review: сохраняется в PR #5 после публикации этого commit.

## Review

- self-review: найдено и до independent review исправлено несколько edge cases (secret scan, path escape, untracked context, stage wording);
- independent review artifact: `docs/reviews/TEMPLATE-4-review.md`;
- independent round 1: 4 Major findings, fixed in `917fc172...`;
- independent round 2 on `917fc172...`: 8 P1 findings, all accepted and addressed by the next review-fix commit;
- independent round 3 on `f95abce0...`: 3 P1 + 2 P2 findings accepted; remediation prepared with typed evidence refs, stricter placeholders/local-source containment, fd-based creation, and doc alignment;
- independent round 4 on `25c80df2...`: 2 P1 + 2 P2 findings accepted; remediation prepared for strict URL/regular-file evidence and identifiable new-task sources;
- independent round 5 on `4ebf4214...`: 2 P1 + 1 P3 findings accepted; remediation prepared for terminal HTTP(S) parsing, Unicode/IDNA strictness, and canonical task-source persistence;
- independent round 6 on `9d38d9b1...`: 1 P1 + 1 P2 findings accepted; remediation prepared for strict percent-encoding and slash-ID/source-kind consistency;
- independent round 7 on `f426dfbc...`: no P0/P1, one acceptance-blocking P2 accepted; remediation prepared for fail-closed file-like auto classification and persistent source namespace;
- independent round 8 on `91910713...`: no P0/P1, one acceptance-blocking P2 accepted; remediation prepared to reserve HTTP(S) namespace before file-like auto classification;
- closure: TEMPLATE-6 clean-context review confirms the symlink finding is fixed; new exact-HEAD CI and broader exact-HEAD review remain required;
- residual risk: provider-specific adapters remain thin adapters; generic process is defined in provider-neutral docs.

## Post-merge status (2026-09-28)

- Merged commit: `ae1e4a6b838c4fce518d6285d327c19b923f49b0`.
- Локальная проверка этого merge-коммита: `./scripts/repo-doctor --template` — exit 0; `make test-template` — 59 tests, OK; `python3 scripts/validate-telemetry.py` — 21 cycles valid.
- PR-head GitHub Actions run [`36228392844`](https://github.com/mnevrov/agentic-repository-engineering-template/actions/runs/36228392844) завершился с conclusion `success` на exact HEAD `d6d93fabd42c3c0d8b0124b7b40d54736f85fbd8`.
- Post-merge GitHub Actions run [`36229039503`](https://github.com/mnevrov/agentic-repository-engineering-template/actions/runs/36229039503) проверил exact merge SHA `ae1e4a6b838c4fce518d6285d327c19b923f49b0`; conclusion success.
- CodeRabbit status `SUCCESS` на PR head означает `Review skipped: manual review required for this OSS repository`; это не независимый review.
- Independent clean-context review точного merge SHA сохранён в `docs/reviews/TEMPLATE-4-final-review.md`; verdict `changes_required`, P0/P1 нет, P2 по чтению symlinked `Makefile` оставляет AC-3 частично невыполненным. Следующая задача TEMPLATE-6 исправляет этот finding и добавляет regression coverage.
- TEMPLATE-6 исправляет symlink finding; 61 template tests и `repo-doctor --template` прошли локально, independent review `docs/reviews/TEMPLATE-6-review.md` одобрил текущий scoped diff. GitHub CI на новом commit ещё не запускался.
- Review также отметил P3: некоторые malformed list-valued поля `repo-doctor` дают traceback вместо structured conflict. Он не блокирует TEMPLATE-4 и не входит в TEMPLATE-6.

## Traceability

- owner requirement → TEMPLATE-4;
- TEMPLATE-4 → brownfield guide/tooling/agents/tests;
- Task → PR: #5 `feat(adoption): add brownfield repository engineering path`.
