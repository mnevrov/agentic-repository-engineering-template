# TEMPLATE-11 — Diagnose OpenCode project agent discovery on HOST

**Статус:** blocked
**Риск:** A  
**Human gate:** delegated by owner (2026-11-05)

## User evidence

- `make test-template`: 80 tests PASS on `release/v0.1.0-rc.1`.
- `make opencode-acceptance`: missing `reviewer`, `repository-discovery`, `adoption-orchestrator`.
- HOST (2026-11-05): OpenCode **v2.1.2**; neither `OPENCODE_DISABLE_PROJECT_CONFIG` nor `OPENCODE_CONFIG_PROJECT_DISABLE` is set; Git tracks `.opencode/agents/repository-discovery.md`.
- HOST: `opencode debug config` confirms project `opencode.json` and `.opencode` sources are loaded.
- HOST: `opencode debug agents | python3 -c 'json.load(...)'` fails at line 7359, char 196405; upstream known large-output pipe truncation.
- CI: OpenCode **2.1.2** fails all three exact agent IDs even when captured into a regular file; OpenCode **2.2.5** passes. This is a genuine version-compatibility issue distinct from pipe truncation.

## Scope

- Improve error diagnostics for project configuration not loaded vs missing agents.
- Identify `OPENCODE_DISABLE_PROJECT_CONFIG` service environment failure mode.
- Do not log resolved OpenCode config or provider secrets.
- Add tests for global-only config sources and no secret leak.
- Preserve release candidate `v0.1.0-rc.1`; no retrospective tag or release mutation.

## Acceptance

- [ ] Existing and new tests PASS (including fake pipe-truncation reproduction and old-version rejection).
- [ ] Exact-head GitHub CI PASS.
- [ ] Independent review completed.
- [ ] Real HOST OpenCode subagents discovered (separate local acceptance).

## Evidence

User-provided HOST JSON parse failure confirmed; exact OpenCode CLI source v2.1.2 uses `process.stdout.write(JSON.stringify(...))`; upstream https://github.com/anomalyco/opencode/issues/29330 documents pipe truncation and file-redirect workaround. Real user rerun on patched `main` remains required.

## Version policy

OpenCode **2.2.5** is the minimum verified version; 2.1.2 explicitly rejected by acceptance. Do not duplicate Markdown agent definitions into global provider config to work around legacy discovery. Final real HOST verification still pending.

## Stabilization evidence update (2026-11-05)

**Технический scope реализован:** source-template exact-main CI [42014455431](https://github.com/mnevrov/agentic-repository-engineering-template/actions/runs/42014455431) — PASS (включая template tests, doctor и pinned OpenCode matrix). Owner reports successful downstream HOST Pilot and post-merge run [42024296100](https://github.com/mnevrov/agentic-template/actions/runs/42024296100) at merge SHA `c23cbbb9c51d2a988a233373882d0b2d512afebf`; этот Pilot недоступен для независимой проверки через коннектор (404). Исторические описания pending — снимок того периода, их не выдавать за текущие события.

**Открытый релизный gate:** независимый review точного финального release SHA, защитные правила main; для TEMPLATE-10 пользовательская проверка QR/meetup остаётся отдельной. Не менять исторические telemetry rows и не объявлять historical independent review, которого не было.
