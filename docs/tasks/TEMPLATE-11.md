# TEMPLATE-11 — Diagnose OpenCode project agent discovery on HOST

**Статус:** in progress  
**Риск:** A  
**Human gate:** delegated by owner (2026-11-05)

## User evidence

- `make test-template`: 80 tests PASS on `release/v0.1.0-rc.1`.
- `make opencode-acceptance`: missing `reviewer`, `repository-discovery`, `adoption-orchestrator`.
- Host OpenCode version and actual config sources not yet observed.

## Scope

- Improve error diagnostics for project configuration not loaded vs missing agents.
- Identify `OPENCODE_DISABLE_PROJECT_CONFIG` service environment failure mode.
- Do not log resolved OpenCode config or provider secrets.
- Add tests for global-only config sources and no secret leak.
- Preserve release candidate `v0.1.0-rc.1`; no retrospective tag or release mutation.

## Acceptance

- [ ] Existing and new tests PASS.
- [ ] Exact-head GitHub CI PASS.
- [ ] Independent review completed.
- [ ] Real HOST OpenCode subagents discovered (separate local acceptance).

## Evidence

User-provided HOST failure confirmed; remaining checks pending.
