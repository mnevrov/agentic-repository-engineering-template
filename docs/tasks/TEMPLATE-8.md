# TEMPLATE-8 — Production bootstrap and template/product test isolation

**Статус:** blocked
**Риск:** B
**Human gate:** delegated by repository owner (2026-11-05)
**Источник:** production readiness for OpenCode-only usage

## Scope

- isolate reusable tooling tests under `template_tests/`;
- add guarded, one-shot downstream initializer;
- preserve project-owned `tests/` and fail-closed real check/test gates;
- verify consistency of Markdown TODO vs task status;
- add regression coverage and CI verification.

## Acceptance criteria

- [ ] `make test-template` runs tooling tests without product tests.
- [ ] New project initializer removes source tasks/reviews and resets telemetry.
- [ ] Repeat and symlinked-directory initialization fail without mutation.
- [ ] Post-bootstrap product check/test can be configured without false red template tests.
- [ ] GitHub CI passes on exact PR SHA; independent clean-context review recorded.

## Review findings remediation

Addressed CodeRabbit findings (origin matching, output/symlink preflight, atomic initialization lock, safe checker location), and added regression tests. Lock intentionally stays after partial failure to force manual inspection. `template_tests/` symlinks explicitly fail closed (no external directory traversal).

## Evidence

Pending GitHub Actions and downstream acceptance; do not claim E3 or production readiness prematurely.

## Stabilization evidence update (2026-11-05)

**Технический scope реализован:** source-template exact-main CI [42014455431](https://github.com/mnevrov/agentic-repository-engineering-template/actions/runs/42014455431) — PASS (включая template tests, doctor и pinned OpenCode matrix). Owner reports successful downstream HOST Pilot and post-merge run [42024296100](https://github.com/mnevrov/agentic-template/actions/runs/42024296100) at merge SHA `c23cbbb9c51d2a988a233373882d0b2d512afebf`; этот Pilot недоступен для независимой проверки через коннектор (404). Исторические описания pending — снимок того периода, их не выдавать за текущие события.

**Открытый релизный gate:** независимый review точного финального release SHA, защитные правила main; для TEMPLATE-10 пользовательская проверка QR/meetup остаётся отдельной. Не менять исторические telemetry rows и не объявлять historical independent review, которого не было.
