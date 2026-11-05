# TEMPLATE-10 — OpenCode-only public onboarding

**Статус:** blocked
**Риск:** A  
**Human gate:** delegated by owner (2026-11-05)

## Scope

- Update public meetup/handout/docs for OpenCode v2 exclusively.
- Ensure downstream initializer removes source-only meetup status and handout.
- Preserve release-candidate vs production acceptance distinction.

## Acceptance criteria

- [ ] Public docs link correctly and don't advertise Claude/Codex as supported runtimes.
- [ ] Source-only files are absent after downstream initialization.
- [ ] GitHub CI pass on exact SHA and independent clean-context review is captured.

## Evidence

Pending CI; user-device link/QR verification and HOST demo remain separate gates.

## Stabilization evidence update (2026-11-05)

**Технический scope реализован:** source-template exact-main CI [42014455431](https://github.com/mnevrov/agentic-repository-engineering-template/actions/runs/42014455431) — PASS (включая template tests, doctor и pinned OpenCode matrix). Owner reports successful downstream HOST Pilot and post-merge run [42024296100](https://github.com/mnevrov/agentic-template/actions/runs/42024296100) at merge SHA `c23cbbb9c51d2a988a233373882d0b2d512afebf`; этот Pilot недоступен для независимой проверки через коннектор (404). Исторические описания pending — снимок того периода, их не выдавать за текущие события.

**Открытый релизный gate:** независимый review точного финального release SHA, защитные правила main; для TEMPLATE-10 пользовательская проверка QR/meetup остаётся отдельной. Не менять исторические telemetry rows и не объявлять historical independent review, которого не было.
