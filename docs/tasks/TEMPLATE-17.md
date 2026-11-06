# TEMPLATE-17 — Owner release approval and gated one-command finalizer

**Статус:** done  
**Риск:** B  
**Human gate:** explicit owner authorization 2026-11-06; review waiver and E4 limitations separately disclosed in `docs/release/OWNER_RELEASE_APPROVAL.md`.

## Scope

- Owner approval and explicit labeling of absent independent exact-SHA review.
- Deterministic guarded release mechanism using local authenticated GitHub CLI and personal registered signing key.
- No unverified tags, no GitHub Action GPG-key generation, no bypass of main protection, no scripted fake integration success.
- Integration tests for pure release-safety checks.

## Acceptance

- [x] Exact-SHA GitHub three required CI jobs checked before publish.
- [x] Admin ruleset created only if missing and active protection verified via branch API and effective rules.
- [x] Tag creation uses local configured signing identity; local signature check and GitHub `verification.verified=true` mandatory.
- [x] Release published only against signed tag, after owner approval and checked CI.
- [x] Dry-run preflight has no remote writes; text logs do not disclose auth tokens.
- [x] Fail-closed tests of required rule types/status-check contexts.
- [ ] Actual admin ruleset and verified tag/Release: waiting for GitHub admin-capable auth + local signing key, unavailable to connected assistant.

## Evidence

Source repo prior SHA `2447c9cee62b39952b55024c10f8fcd72a002250`, [CI PASS 42198948898](https://github.com/mnevrov/agentic-repository-engineering-template/actions/runs/42198948898).
Final code SHA will change upon merging this task; **must recheck current SHA's CI before release**.

**Scope is release automation, not a completed GitHub release.** Readiness remains blocked until platform operations actually succeed.
