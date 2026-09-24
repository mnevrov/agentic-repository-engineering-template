---
name: Adopt Existing Repository
description: Use to introduce repository engineering into an existing/brownfield project. Orchestrates specialized read-only subagents, uses grill-me for unresolved human decisions, proposes the minimum adoption plan, and stops at a Human Gate before any repository modification.
allowed-tools: Read, Grep, Glob, Bash
---

# Adopt Existing Repository

This is orchestration, not one giant prompt.

1. Run/consume `repo-audit`; treat it as evidence, not authority.
2. Delegate independent read-only workstreams to `repository-discovery`, `verification-discovery`, and `context-truth`; parallelize when possible.
3. Invoke `gap-analysis` on evidence summaries, then `adoption-orchestrator`.
4. For every blocking decision not resolvable from repository evidence, invoke `/grill-me`. Leave non-blocking unknowns explicit.
5. Final plan may include only source mapping, confirmed verification semantics, local execution-contract location tied to the existing tracker, relevant context for one pilot Task, and exact necessary file changes.
6. Do not require template layout, new Makefile/CI/tracker, retrospective ADR migration or rewritten AI instructions.
7. **STOP before editing and wait for explicit Human Gate.** After approval, make only agreed minimal changes and use one existing bounded Task.

Read `docs/ADOPT_EXISTING_REPOSITORY.md`.
