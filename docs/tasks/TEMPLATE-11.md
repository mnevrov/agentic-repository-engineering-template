# TEMPLATE-11 — Diagnose OpenCode project agent discovery on HOST

**Статус:** in progress  
**Риск:** A  
**Human gate:** delegated by owner (2026-11-05)

## User evidence

- `make test-template`: 80 tests PASS on `release/v0.1.0-rc.1`.
- `make opencode-acceptance`: missing `reviewer`, `repository-discovery`, `adoption-orchestrator`.
- HOST (2026-11-05): OpenCode **v2.1.2**; neither `OPENCODE_DISABLE_PROJECT_CONFIG` nor `OPENCODE_CONFIG_PROJECT_DISABLE` is set; Git tracks `.opencode/agents/repository-discovery.md`.
- HOST: `opencode debug config` confirms project `opencode.json` and `.opencode` sources are loaded.
- HOST: `opencode debug agents | python3 -c 'json.load(...)'` fails at line 7359, char 196405; probable known large-output pipe truncation in OpenCode CLI. This is not proof the agent is absent.

## Scope

- Improve error diagnostics for project configuration not loaded vs missing agents.
- Identify `OPENCODE_DISABLE_PROJECT_CONFIG` service environment failure mode.
- Do not log resolved OpenCode config or provider secrets.
- Add tests for global-only config sources and no secret leak.
- Preserve release candidate `v0.1.0-rc.1`; no retrospective tag or release mutation.

## Acceptance

- [ ] Existing and new tests PASS (including fake pipe-truncation reproduction).
- [ ] Exact-head GitHub CI PASS.
- [ ] Independent review completed.
- [ ] Real HOST OpenCode subagents discovered (separate local acceptance).

## Evidence

User-provided HOST JSON parse failure confirmed; exact OpenCode CLI source v2.1.2 uses `process.stdout.write(JSON.stringify(...))`; upstream https://github.com/anomalyco/opencode/issues/29330 documents pipe truncation and file-redirect workaround. Real user rerun on patched `main` remains required.
