# Independent adversarial review — TEMPLATE-15 (release-audit remediation)

**Reviewer:** independent OpenCode subagent (fresh clean context, adversarial stance), 2026-11-05/06.
**Reviewed:** commits on `fix/release-audit-p1-telemetry-provenance-v2` over baseline `2043f6d1c2262342f81edb296f5d5584a50c5107`.

## Round 1 — VERDICT: CHANGES_REQUIRED

The named audit PoC was closed and the happy path worked, but the reviewer confirmed working bypasses (PoCs in `/tmp/opencode/adv-review/`, independently reproduced by the author in `/tmp/opencode/audit-repro2/` before implementing):

| # | Sev | Finding (CONFIRMED by PoC) | Remediation |
|---|-----|-----------------------------|-------------|
| 1 | P0 | Cutover re-opened by presenting any pre-marker ancestor (stale branch/tag, `event.before`) as `base_ref`: project rows deleted mid-lifecycle passed both gates | Marker required in **every** commit of `base..HEAD`; `history_monotonic` verifies every ledger committed in the range is an order-preserving subsequence of the final ledger; enforced in BOTH gates |
| 2 | P0 | Source-template identity bypassed by URL aliases that really resolve to the source (`.git/.`, `x/../name`, port form, trailing-dot host) | Canonical segments: `..` rejected → identity None; `/.` and `.git/.` normalize to the true identity → source match; ports/trailing-dot hosts normalized; full last-segment comparison |
| 3 | P0 | Same-name GitLab mirror of the template (`gitlab.t8.ru/sensor/other/agentic-repository-engineering-template`) cut its inherited ledger over; init-project also initialized it | Identity deny: any identity whose repo-name segment equals the template name; `source_url_matches` likewise for raw URLs (incl. mirrors and local paths) |
| 4 | P1 | `init-project` destroyed a local-path clone of the template (origin without `mnevrov/` prefix) | Name-segment guard in `source_url_matches`; regression `test_refuses_local_path_clone_named_after_template` |
| 5 | P2 | Symlink marker (blob content = link target text) unlocked cutover | `ls-tree` mode check: only `100644/100755` regular blobs qualify |
| 6 | P2 | `check-telemetry-required.py` failed **open** on dash-leading `--base-ref` (`--all` → "no substantive change", rc=0) | `UNSAFE_REF` gate in both scripts and in `bootstrap_cutover`/`history_monotonic`; regression test |
| 7 | P2 | Shallow clone boundary masqueraded as root commit | `rev-parse --is-shallow-repository` must be exactly `false` |
| 8 | P2 | Job-level `permissions:` escalation hidden by YAML-quoted key defeated the regex test | Test rewritten to parse the YAML structurally (`jobs.*.permissions` absence asserted) |
| 9 | P3 | `url.<base>.insteadOf` hid the real fetch target | Any insteadOf rewrite covering the origin URL → identity unverifiable → refuse |
| 10 | P3 | `docs/process/telemetry.md` documented the old contract incl. a false irrepeatability claim | Rewritten to the provenance contract; GETTING_STARTED documents hosted-origin-before-first-commit and unique repo name |
| 11 | P3 | `PUBLISH_TO_GITHUB.md` still said "Release candidate" | Aligned to STABILIZATION/BLOCKED |
| 12 | P3 | INDEX stripping was substring-based (deleted unrelated lines); RELEASE_READINESS kept a dead link | Link-target/inline-code resolution relative to document and root; both files processed; regression in init test |

Reviewer-verified positives (round 1): original audit PoC refused; legitimate downstream flow worked; crash paths exit nonzero (fail-closed).

## Fixes verification (author, before round 2)

- `make test-template`: 122 tests OK (includes 31 cutover tests: provenance negatives per-attack + merge-with-parallel-rows positive).
- Full attack battery re-run: all previous bypasses blocked; legitimate bootstrap/append still pass.
- Real downstream `mnevrov/agentic-template` replay at actual boundary commits: cutover PASS, post-cutover append PASS, tamper FAIL (rejected).
- Downstream CI smoke equivalent (local): PASS incl. destructive-repeat guard and no-origin fail-closed.

## Round 2 — VERDICT: CHANGES_REQUIRED (9 new confirmed findings)

Fresh-context reviewer at commit `9cb62d1`; all PoCs rebuilt from scratch. 8 of 12 round-1 findings verified CLOSED by the reviewer; the mechanism introduced to close finding 1 (`history_monotonic`) was itself defeated, plus a new identity alias class. Independently reproduced by the author before implementing (all CONFIRMED):

| # | Sev | Finding (CONFIRMED by PoC, reproduced by author) | Remediation + regression |
|---|-----|--------------------------------------------------|--------------------------|
| R2-1 | P0 | `git rev-list base..HEAD -- path` applies default history simplification: an `-s ours` "evil merge" whose tree equals the first parent is pruned — a committed `result:"failed"` row deleted via merge resolution passed BOTH gates in the exact CI invocation (`--base-ref origin/main`); the same blind spot re-opened the cutover from a stale root base | `--full-history` in `history_monotonic`; regressions `test_evil_merge_cannot_drop_committed_row`, existing merge positive test proves no false positive |
| R2-2 | P1 | Percent-encoded remote path (`%61gentic-…`) resolves to the real source repo (`git ls-remote` verified) but bypassed `source_identity_matches`, the mirror deny, and `init-project`'s destructive guard | Single `unquote()` pass before canonicalization (double-encoding stays literal); regressions in `test_telemetry_cutover` + PoC battery |
| R2-3 | P2 | `git clone /path/…/.git` clone: tail segment `.git` defeated the name-based init guard while carrying full template history | `/.git` tail resolves to the parent name before comparison; PoC `round2c.sh` PASS |
| R2-4 | P2 | `git replace --graft` fabricated a template-signature root, defeating root/marker lineage | Any non-empty `refs/replace` namespace → lineage unverifiable → refuse; regression `test_replace_refs_refuse_cutover` |
| R2-5 | P2 | Byte-identical duplicated `cycle_id` row satisfied the required-gate without a real cycle | `validate-telemetry.py` rejects duplicate `cycle_id` (CI step 'Validate telemetry' runs before the gates) |
| R2-6 | P2 | required-check read the worktree ledger while diffing `base..HEAD`: uncommitted local row masked a missing committed row ('passes locally') | Both gates read the ledger from the HEAD blob and fail closed on a diverged worktree copy; regression `test_worktree_ledger_diverged_from_head_fails_closed` |
| R2-7 | P2 | Structural permissions test skipped silently when PyYAML missing | Always-on text guard (quoted keys, job indentation) + structural YAML test as defense in depth |
| R2-8 | P2 | INDEX stripping dropped prose lines naming a removed file in backticks | Only list lines whose EVERY markdown link resolves to a removed file are dropped; prose/backticks survive (init test extended) |
| R2-9 | P3 | Docstrings/ADR/telemetry.md claimed 'prefix' and repeated the falsified irrepeatability claim | Reworded to the implemented order-preserving-subsequence over `--full-history`; replace-refs/percent/HEAD-read residual notes in ADR-0001 |

Reviewer's verified fix direction (`--full-history`) was applied exactly as recommended; the reviewer had validated it against the suite and all legitimate flows in their own patched copy.

**Post-round-2 verification (author):** 127 template tests OK; full round-1 battery re-run 9/9 blocked; round-2 PoC battery (evil merge, pct aliases ×{gates, init}, .git-tail init, replace-graft, duplicate cycle_id, worktree divergence) all blocked; downstream CI smoke PASS; real Pilot boundary replay PASS; validate-telemetry/doctor/check-task-state/opencode-acceptance PASS.

## Round 3 — resubmission

Round 3 re-reviews commit `0599c4b` with fresh context: verify R2-1…R2-9 closed and hunt for new bypasses. Verdict appended below.
