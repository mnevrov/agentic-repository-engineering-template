# TEMPLATE-10 — OpenCode-only public onboarding

**Статус:** in progress  
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
