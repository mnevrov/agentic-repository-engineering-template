# TEMPLATE-14 — Minimal CI and release review gate hardening

**Статус:** in progress
**Риск:** A
**Human gate:** delegated by owner, 2026-11-05.

## Scope

- Repository Doctor workflow uses read-only GITHUB_TOKEN and explicit timeout.
- Independent release-review evidence may be published externally with exact reviewed SHA; mirroring it in Git changes HEAD and requires fresh verification.
- Add regression coverage; do not touch OpenCode runtime, frozen RC, releases or branch rules.

## Acceptance

- [ ] CI permissions explicitly contents: read and doctor job bounded.
- [ ] New regression and exact-head CI PASS.
- [ ] External review artifact must identify exact SHA without creating a new head.
- [ ] Independent final approval and main branch protection remain open gates.

## Evidence

Pending exact-head CI. Telemetry stays partial while final independent approval is missing.
