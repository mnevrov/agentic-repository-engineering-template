# v0.1.0 — owner release decision

**OWNER APPROVED** — 2026-11-06. The repository owner explicitly instructed to complete the release sprint, after receiving the remaining release-gate status and the limitations of the connected GitHub integration.

## Boundary of the owner's decision

- **independent review: waived** for the additional final release-review round, following completed TEMPLATE-15 adversarial rounds 1–5, the owner-directed shortened round 6, and confirmation of the outstanding findings. This records *owner acceptance of the absence of another independent review*, not a claim that a new reviewer approved the final SHA.
- **E4: owner-reported**, not independently reproduced in this release sprint. The prior HOST/Pilot cycle was reported successful by the owner; the CI-only CLI/Git/telemetry integration added in Pilot PR #2 establishes E3 component integration, not model/LiteLLM or OpenCode HOST E4. There is no stored claim of a fresh model run.
- Platform rules (active protection of `main`) and GitHub's verification of a personally signed immutable tag **must still be satisfied technically**. These conditions are NOT waived because they can be verified deterministically and are necessary before publication.
- Approval applies to the project as of the final release-candidate SHA *after* exact-SHA CI passes, without additional changes after the release tag.
- `v0.1.0` is not considered released merely by recording this approval. A successful signed tag and a published GitHub Release remain necessary.

## Relevant evidence

- TEMPLATE-15 closure: `docs/tasks/TEMPLATE-15.md` and ADR-0001.
- Source main before finalizer: `2447c9cee62b39952b55024c10f8fcd72a002250`, [CI 42198948898](https://github.com/mnevrov/agentic-repository-engineering-template/actions/runs/42198948898) PASS.
- Pilot main: `d2fdf020be2a465549f31896c84e6be02132eb36`, [CI 42198531178](https://github.com/mnevrov/agentic-template/actions/runs/42198531178) PASS, including 2 E3 component tests.
- GitHub release gate issue: [#9](https://github.com/mnevrov/agentic-repository-engineering-template/issues/9).
