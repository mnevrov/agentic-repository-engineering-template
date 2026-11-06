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

## Round 2 — pending

Round 2 resubmits the fixed code to a fresh adversarial pass; verdict and any P0/P1 disposition are appended below when complete.
