# TEMPLATE-9 — OpenCode v2-only workflow

**Статус:** in progress  
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
