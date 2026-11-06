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

## Round 3 — VERDICT: CHANGES_REQUIRED (1 P0, 1 P1, 1 P2, doc drift)

Fresh-context reviewer at commit `f6ac04b`; PoCs built under `/tmp/opencode/adv3/`, all independently reproduced by the author before implementing:

| # | Sev | Finding (CONFIRMED) | Remediation + regression |
|---|-----|----------------------|--------------------------|
| R3-1 | P0 | The blanket `source_only` exemption in `history_monotonic` made the interior check inert for the template's OWN repository: a `result:"failed"` TEMPLATE-* row added in one PR commit and deleted in the next, with the base prefix restored byte-exactly, passed validate/append-only/required with the verbatim CI invocation | Two-regime rule: only a cutover-shaped final ledger (zero TEMPLATE-* rows, all valid) exempts intermediate source-only ledgers; any other final ledger is checked with no exemption; ledger-file deletion inside the range always fails. Regressions: `test_source_template_cannot_delete_template_row_with_prefix_restored`, `test_ledger_deleted_midrange_fails_closed` |
| R3-2 | P1 | `lower()` executed before `unquote()`: `%41gentic-…` decodes to `Agentic-…` after case folding and evaded the source/mirror deny and the init guard (`git ls-remote` shows the server resolves it to the source HEAD) | Decode host and path before case folding in `repository_identity` and `source_url_matches`; regressions for `%41`, `…templat%45`, `%67ithub.com`, with downstream names unaffected |
| R3-3 | P2 | A **directory** at `.ai/project-initialized`: `ls-tree -r` reported children's modes (regular blobs), and `git show` of a tree prints child names that satisfied `_valid_marker_content` → cutover unlocked | Non-recursive `ls-tree` with a single-entry requirement; regression `test_directory_marker_refuses_cutover` |
| R3-4 | P2 | Doc/code drift: telemetry.md/docstring/ADR claimed an unconditional subsequence rule while the code had the source_only exemption | All three texts now state the two-regime rule and decode-before-lower ordering explicitly |

Reviewer's own closure confirmations (round-2 items): R2-3, R2-4, R2-5, R2-6, R2-7, R2-8 CLOSED with their own PoCs; R2-1/R2-2 partially closed → superseded by the R3-1/R3-2 fixes above.

**Post-round-3 verification (author):** 131 template tests OK; round-3 PoC trio blocked (prefix-restored deletion rc=1 both gates; `%41` identity now matches source; directory marker kind='special', text=None); full round-1/round-2 batteries re-run all blocked (9/9 + 4/4); downstream CI smoke PASS; real Pilot boundary replay PASS (3/3 rc=0 + tamper rejected); validate-telemetry/doctor/check-task-state PASS.

## Round 4 — resubmission

Round 4 re-reviews the fixed code with fresh context; verdict appended below.

### Round 4 — VERDICT: REVISE (no P0; 1 P1, four mediums recorded below as P2, F5 as P3)

Fresh-context reviewer at commit `dd4b157`; every finding independently reproduced by the author first (`/tmp/opencode/audit-repro2/round4-verify.sh`, `round4b-f1.sh`, `f5-repro.sh`) before implementing:

| # | Sev | Finding (CONFIRMED) | Remediation + regression |
|---|-----|----------------------|--------------------------|
| R4-1 | P1 | `history_monotonic` granted the cutover exemption from the final ledger's SHAPE alone. Base an ancestor from before the ledger existed — e.g. the template's own root `20b3cf3…`, which has no ledger — and the endpoint prefix check became vacuous: a 40-row TEMPLATE-* wipe to one fabricated project row passed BOTH gates with a hosted-looking origin | The exemption requires `verified_cutover=True`, which callers set only from a successful `bootstrap_cutover` verdict; shape alone never grants it. Regressions `test_pre_ledger_base_cannot_wipe_inherited_template_rows` (root WITHOUT a ledger — the shape earlier tests lacked) + `test_pre_ledger_root_honest_project_ledger_still_passes` (no over-refusal) |
| R4-2 | P2 | Multi-valued `remote.origin.url`: transport fetches the FIRST value, `git config --get` reports the LAST — a deny-listed template URL first with a friendly URL second gave the gate a usable identity | `--get-all`, more than one value → no identity; regression `test_multiple_origin_urls_refuse_identity` |
| R4-3 | P2 | insteadOf check over-refused: a common personal `url.git@github.com:.insteadOf https://github.com/` (typically global, and repo-local `git config --list` cannot distinguish scope) blocked legitimate first-bootstrap forever | `_origin_rewritten` asks Git itself for the effective target (`ls-remote --get-url`) and refuses only when the rewrite changes host/owner/repo identity; regressions for the tolerated alias (cutover still PASSes) and an identity-changing alias (refused) |
| R4-4 | P2 | Shallow/replace-refs integrity was checked only inside `bootstrap_cutover`; the standalone `history_monotonic` scan (the required-gate's second pass) ran over grafted/shallow ranges too, and legacy `.git/info/grafts` was never inspected | Checks hoisted into `history_monotonic` (both gates inherit them) + `.git/info/grafts` presence treated as fabricated lineage; ADR overclaim about which layer enforces what corrected; regression `test_grafts_file_refuses_cutover` |
| R4-5 | P3 | A tree at the ledger path made `git show` print a child listing (`['tree …','','inner.txt']`) and the worktree read crashed with an unhandled `IsADirectoryError` traceback | Mode-checked non-recursive ledger reads (`_ledger_kind_at`): tree/symlink/gitlink → explicit 'not a regular file' error from both gates; regression `test_directory_ledger_path_fails_closed` |

**Post-round-4 verification (author):** 138 template tests OK; F1 faithful wipe (round4b) and pre-ledger-root variant blocked rc=1 both gates; F2 identity None; F3 alias tolerated rc=0 and retargeting alias blocked; F5 clean structural error; full round-1/2/3 batteries re-run all blocked; downstream CI smoke PASS; real Pilot boundary replay PASS; validate-telemetry/repo-doctor/check-task-state/opencode-acceptance PASS; repo's own gates vs `2043f6d` PASS.

## Round 5 — VERDICT: REVISE (2 P1, 1 P2, 2 P3)

Fresh-context reviewer at commit `79dfd0c` (PoCs under `/tmp/opencode/adv5/`); closures R4-1/R4-3/R4-5 confirmed CLOSED by the reviewer; R4-2 CLOSED for the gates but its fix regressed the init guard; R4-4 partially closed. All five new findings independently reproduced by the author before implementing (`round5-verify.sh`, plus the reviewer's own PoCs re-run):

| # | Sev | Finding (CONFIRMED) | Remediation + regression |
|---|-----|----------------------|--------------------------|
| R5-F1 | P1 | `.git/info/grafts` was located via `rev-parse --git-dir`, which in a LINKED worktree points at `.git/worktrees/<name>` — git honors the COMMON dir file. Both gates silently skipped the lineage check in the worktree workflows this repo's own tooling teaches; a committed `failed` row deleted mid-range passed both gates with a common-dir graft planted | Path resolved with `rev-parse --git-path info/grafts`; regression `test_grafts_file_in_common_dir_refuses_from_linked_worktree` + realistic replay (grafted linked worktree now rc=1 both gates) |
| R5-F2 | P1 | `source_url_matches` did not canonicalize `.`/`//` segments: `git clone .` inside the template records `/abs/…-template/.` verbatim and the destructive init guard opened — init destroyed a full template clone (tasks, reviews, 41 ledger rows wiped, marker committed) | Separator/dot-segment canonicalization (with `..` clamping) before the name check; regressions for `/.`, `/./`, `//.`, `../`, `file://…/.` variants in both `source_url_matches` and bootstrap-safety |
| R5-F3 | P2 | R4-2's `origin_url -> None` on ambiguity was consumed by init as `or ""` — the destructive guard collapsed 'unverifiable' into 'definitely not the source' and initialized a template clone holding the source URL as one of several values | New `origin_urls()`; the guard checks EVERY configured value; regression `test_refuses_multi_valued_origin_when_any_value_is_source` |
| R5-F4 | P3 | An unreadable (chmod 000) grafts file escaped as an unhandled `PermissionError` traceback; append-gate `main()` caught nothing | `OSError` inside `_has_replace_refs` → treated as fabricated lineage; both mains report structural errors as plain messages; regression `test_unreadable_grafts_file_refuses_without_traceback` |
| R5-F5 | P3 | `…/repo/.git` normalized to an identity with an EMPTY trailing segment (deny compared against `""`); dead `_absent_at` (with an incorrect stderr heuristic) and `_insteadof_bases` left in place inviting reuse | Empty segment dropped after `.git` strip (`host/owner/repo` correct — deny works at that layer too); dead helpers deleted; regression `test_repository_identity_canonicalizes_repo_git_tail` |

**Post-round-5 verification (author):** 144 template tests OK; reviewer's poc1/poc2/poc3 re-run against the fixed tree: F1 attack rc=1 both gates (linked worktree + common-dir graft), F2 init rc=1 with 15 tasks/41 rows intact, F3 init rc=1 data intact; realistic grafted-worktree replay on this repo rc=1 both gates; unreadable grafts plain-message rc=1; `…/repo/.git` identity full and deny-true.

## Round 6 — compressed (owner instruction: time-boxed, no long external review round)

Per the owner's explicit instruction the full fresh-context round-6 review cycle was skipped; instead the attack surfaces a round-6 reviewer would probe first (named in the prepared brief) were pre-checked by the author against `d055579` and hardened pre-emptively:

| Probe | Result | Action |
|---|---|---|
| Case-insensitive `.git` tail in `repository_identity`: `…template.GIT` → `host/owner/template.git` (tail NOT stripped pre-lowercase), so `source_identity_matches` deny saw a different repo name; GitHub serves `repo.GIT` case-insensitively | CONFIRMED (deny evasion at the identity layer; `source_url_matches` still refused, so no end-to-end gate bypass was demonstrated) | Tail strip made case-insensitive before lowering; `.GIT`/`.Git` now normalize identically; chain `…/.git/.git` fails closed; regressions extended |
| Colon tokenizer in `source_url_matches` (`[/ :]+`): scp-style, port forms, `C:/`, `%2e`-encoded dot | Colon-collapse produces e.g. `github.com/8443:mnevrov/…` for the malformed `host:port:owner/repo` — the SOURCE name still lands in the tail and is refused; no downstream over-refusal found | No change (refuse-biased already; malformed-form matching the source errs safe) |
| `%32e`/`%2e` tricks, `repo/.git` with case variants in `source_url_matches` | Resolved consistently after unquote-before-split | Covered by extended tests |
| Grafts as directory / unreadable directory listing | `is_file()` False → not flagged; git itself warns and ignores a grafts directory | Accepted as-is (git semantics), OSError path already covered |

**Post-round-6 verification (author):** 144 template tests OK; round-1 battery 9/9 blocked; F1 round-4b wipe blocked; round-5 probe set unchanged (F2 refuses, F4 rc=1); `.GIT` identity deny True; CI smoke PASS; real Pilot replay PASS; validate-telemetry 43 rows valid; repo's own gates vs `2043f6d` PASS.

**Residual process risk (disclosed):** rounds 1-5 were external fresh-context reviews; the round-6 pass is author-executed pre-checks on predicted attack surfaces, not an independent clean-context review. The PR therefore remains a Human-Gate artifact; merging still requires the owner.

