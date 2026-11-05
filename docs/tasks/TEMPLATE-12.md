# TEMPLATE-12 — Initial downstream telemetry cutover without hiding data loss

**Статус:** blocked
**Риск:** B  
**Human gate:** delegated, approved project stabilization.

## Trigger
Owner reports Pilot `PROJECT-BOOTSTRAP` at `aadec1f` with 7 unit tests, 9/9 AC, E2 review and telemetry. Initial downstream Git baseline copied from template still contains 35 source-only `TEMPLATE-*` rows, but one-time `init-project` rightly clears them. CI currently rejects the first project commit as a non-append-only rewrite.

## Scope
- Permit reset ONLY across the committed first `.ai/project-initialized` marker, from an old ledger containing exclusively `TEMPLATE-*` to an entirely project-owned ledger.
- Continue requiring >=1 project telemetry row for substantive first-commit changes.
- Refuse missing/invalid marker, mixed old ledger, retained source entries, invalid base ref, and any subsequent history rewrite.
- Run Git-backed negative tests and downstream first-commit CI smoke.
- Preserve frozen RC branch; do not publish Pilot or claim E3/E4.

## Acceptance
- [ ] First new-project bootstrap commit passes BOTH telemetry gates.
- [ ] Source-only reset cannot bypass missing project-cycle row.
- [ ] Subsequent history remains strictly append-only.
- [ ] GitHub CI exact-head PASS and review findings resolved.
- [ ] Pilot HOST final CI and new-session restore remain pending.

## Evidence
Awaiting CI and independent review.

## Stabilization evidence update (2026-11-05)

**Технический scope реализован:** source-template exact-main CI [42014455431](https://github.com/mnevrov/agentic-repository-engineering-template/actions/runs/42014455431) — PASS (включая template tests, doctor и pinned OpenCode matrix). Owner reports successful downstream HOST Pilot and post-merge run [42024296100](https://github.com/mnevrov/agentic-template/actions/runs/42024296100) at merge SHA `c23cbbb9c51d2a988a233373882d0b2d512afebf`; этот Pilot недоступен для независимой проверки через коннектор (404). Исторические описания pending — снимок того периода, их не выдавать за текущие события.

**Открытый релизный gate:** независимый review точного финального release SHA, защитные правила main; для TEMPLATE-10 пользовательская проверка QR/meetup остаётся отдельной. Не менять исторические telemetry rows и не объявлять historical independent review, которого не было.
