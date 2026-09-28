# Independent final review — TEMPLATE-4

**Reviewer:** Codex code-reviewer (GPT-6), clean-context review; identity beyond this session is unavailable\
**Task:** `docs/tasks/TEMPLATE-4.md`\
**Risk:** B\
**Base:** `ae1e4a6b838c4fce518d6285d327c19b923f49b0`\
**Exact reviewed HEAD:** `8061409d7dda2127604acc050aebffdf080fae0f`\
**Diff:** `ae1e4a6b838c4fce518d6285d327c19b923f49b0..8061409d7dda2127604acc050aebffdf080fae0f`

## Verdict

**blocked** — no code changes are required by this review, and the previous symlink finding is fixed in the reviewed diff. TEMPLATE-4's exact-HEAD CI evidence gate remains open. The requested local-only scope excluded GitHub access, so this review cannot establish that gate. The code diff is acceptable subject to that evidence gate being completed separately.

## Findings

### P0

None.

### P1

None.

### P2

None.

### P3

None.

## Acceptance criteria

- **Brownfield functionality, documentation, and regression coverage:** The reviewed changes preserve the TEMPLATE-4 adoption materials and add a regression that rejects candidates from an external `Makefile` symlink while retaining candidates from a repository-local regular `Makefile`.
- **Safe read-only discovery (AC-3):** The implementation now checks `Makefile.is_symlink()` before reading. Both external-target and regular-file behaviors have regression coverage. The supplied exact-HEAD `make test-template` result passed 61 tests. No P0–P3 issue remains in the reviewed change for this finding.
- **Independent exact-HEAD review:** Completed by this artifact.
- **Exact-HEAD CI:** Not established. The task states that the final review-fix HEAD requires a new CI run. The supplied local checks do not satisfy that remote CI gate.
- **Other TEMPLATE-4 criteria:** This diff does not regress the reviewed task documentation or adoption implementation. No new acceptance-blocking code finding was identified.

## Evidence status

The following exact-HEAD results were supplied with the review request and are recorded as supplied evidence, not independently rerun here:

- `make test-template` — passed, 61 tests.
- `./scripts/repo-doctor --template` — passed.
- `python3 scripts/validate-telemetry.py` — passed, 25 cycles valid.
- `git diff HEAD^..HEAD --check` — passed.
- `make check`, `make test`, and `make test-integration` — each exited 2 with documented `NOT CONFIGURED`; none counts as PASS.
- Exact-HEAD GitHub CI — not run in this review, per the local-only review scope.

## Residual risk

The `is_symlink()` check and subsequent `read_text()` are separate filesystem operations, so a concurrent replacement could theoretically race the check. The existing TEMPLATE-6 independent review assessed this as non-blocking for this local read-only discovery tool. The change fails closed for a stable symlink and the new tests cover that behavior. Exact-HEAD CI remains the outstanding acceptance evidence.
