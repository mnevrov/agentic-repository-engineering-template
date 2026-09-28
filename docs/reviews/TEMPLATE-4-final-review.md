# TEMPLATE-4 independent final review

Reviewer: Codex, clean-context review (identity beyond this session is unavailable)

Task: `docs/tasks/TEMPLATE-4.md`

Reviewed exact merge commit: `ae1e4a6b838c4fce518d6285d327c19b923f49b0`

Reviewed diff: `6f26c9b4a537bcf977b28fdb597264ec96d81665..ae1e4a6b838c4fce518d6285d327c19b923f49b0`

## Findings

### P0

None.

### P1

None.

### P2

1. [`scripts/repo-audit:120`](../../scripts/repo-audit) — **The audit follows symlinked build-marker files outside the target repository.** When a Git repository contains a `Makefile` symlink pointing outside the repository, `detect_verification_candidates()` calls `read_text()` on it. The resulting target names are emitted as verification candidates. This lets an audit of an untrusted repository read and disclose derived content from an unrelated local file, contrary to the read-only discovery boundary and the documented claim that the audit does not read secret values. Skip symlinked marker files or require their resolved path to remain inside the repository before parsing. This affects AC: safe read-only discovery without promoting candidates to facts (AC 3).

### P3

1. [`scripts/repo-doctor:749`](../../scripts/repo-doctor) — **Some malformed JSON field types raise an uncaught `TypeError` instead of producing a structured conflict.** For example, a list-valued `stage` reaches set membership and terminates with a traceback; similar membership checks exist for verification/capability statuses and evidence reference types. The command remains nonzero, so this does not create a false `ready` result, but it weakens the promised `ready / not configured / conflict` diagnostics. Validate types before membership checks and report `[CONFLICT]`. Related to AC 12.

## Acceptance criteria

- AC 1–2: satisfied by the reviewed README and brownfield guide/stage documentation.
- AC 3: **partially satisfied**; candidate labeling and read-only writes are handled, but the P2 symlink finding violates the stated safe discovery boundary.
- AC 4–8: satisfied by the repository-local path model, source precedence/conflict mapping, docs, and provider-neutral/native agent instructions.
- AC 9–11: satisfied by the brownfield fixture/regression coverage and exact-head CI evidence supplied for this review.
- AC 12: adoption doctor supports the three documented outcomes without requiring template layout; the P3 malformed-type path produces an unstructured error but still exits nonzero.
- AC 13: satisfied by the existing-task execution contract and source validation.
- AC 14: this review completes the required independent exact-head review. The task file at the reviewed SHA still has this checkbox open, consistent with it being written before this review.

## Invariants

- INV-1: no domain/transport boundary concern identified in this tooling/documentation change.
- INV-2: no authorization surface introduced.
- INV-3: no secret committed in the reviewed diff was identified by static review; `repo-audit` has the P2 disclosure boundary noted above.
- INV-4: no data/schema migration introduced.
- INV-5: no logging/telemetry secret exposure identified in the reviewed diff.

## Verification evidence

Evidence supplied with the review request (not independently rerun):

- GitHub PR-head run `36228392844` passed all steps on exact head `d6d93fabd42c3c0d8b0124b7b40d54736f85fbd8`.
- Post-merge run `36229039503` succeeded on exact merge SHA `ae1e4a6b838c4fce518d6285d327c19b923f49b0`.
- `./scripts/repo-doctor --template` passed locally.
- `make test-template` passed 59 tests.
- Telemetry validator passed.
- CodeRabbit `SUCCESS` was explicitly a skipped review (`Review skipped: manual review required for this OSS repository`) and is not counted as review evidence.

## Verdict

`changes_required`

The B-risk task has no P0/P1 findings. AC 3 remains partially unmet because `repo-audit` can follow and parse symlinked marker files outside the audited repository. The P3 malformed-config diagnostic issue is non-blocking. Re-review the changed symlink handling on the resulting exact commit before closing the task.

Remaining risks: the audit relies on common-path heuristics and candidate verification commands still require human confirmation, as documented. No runtime or network behavior beyond the supplied verification evidence was independently exercised in this review.
