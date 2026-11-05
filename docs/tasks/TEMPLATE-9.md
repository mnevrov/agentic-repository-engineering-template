# TEMPLATE-9 — OpenCode v2-only workflow

**Статус:** blocked
**Риск:** B  
**Human gate:** delegated by owner (2026-11-05)

## Scope
- native OpenCode v2 commands, agents, skills and project policies;
- remove Claude-specific runtime adapters and config;
- update onboarding/workshop/command documentation to OpenCode only;
- preserve Brownfield adoption and explicit review/evidence gates;
- no pinned model/provider.

## Acceptance criteria
- [ ] OpenCode config and command/skill/agent layout pass regression checks.
- [ ] All public docs describe OpenCode as the sole agent runtime.
- [ ] OpenCode runtime smoke in a real machine is executed and recorded (not CI-only).
- [ ] Independent clean-context review and exact PR SHA CI evidence.

## Evidence
Added downstream GitHub CI smoke to verify one-shot bootstrap on a simulated fresh project. This is controlled CI evidence, not OpenCode host acceptance. Pending CI, runtime smoke and independent review. Do not claim live OpenCode acceptance from CI.

## Stabilization evidence update (2026-11-05)

**Технический scope реализован:** source-template exact-main CI [42014455431](https://github.com/mnevrov/agentic-repository-engineering-template/actions/runs/42014455431) — PASS (включая template tests, doctor и pinned OpenCode matrix). Owner reports successful downstream HOST Pilot and post-merge run [42024296100](https://github.com/mnevrov/agentic-template/actions/runs/42024296100) at merge SHA `c23cbbb9c51d2a988a233373882d0b2d512afebf`; этот Pilot недоступен для независимой проверки через коннектор (404). Исторические описания pending — снимок того периода, их не выдавать за текущие события.

**Открытый релизный gate:** независимый review точного финального release SHA, защитные правила main; для TEMPLATE-10 пользовательская проверка QR/meetup остаётся отдельной. Не менять исторические telemetry rows и не объявлять historical independent review, которого не было.
