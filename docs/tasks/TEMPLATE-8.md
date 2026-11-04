# TEMPLATE-8 — Production bootstrap and template/product test isolation

**Статус:** in progress
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

## Evidence

Pending GitHub Actions and downstream acceptance; do not claim E3 or production readiness prematurely.
