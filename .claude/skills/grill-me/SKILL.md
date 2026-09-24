---
name: Grill Me
description: Use when a workflow has a blocking ambiguity that cannot be resolved from repository evidence. Ask the minimum high-value questions needed for source-of-truth, scope, verification, safety, or policy decisions; never ask for discoverable facts.
allowed-tools: Read, Grep, Glob
---

# Grill Me

Use only after repository evidence is exhausted.

For each blocking ambiguity: show relevant evidence/paths; state the exact unresolved decision; offer 2–5 concrete options plus other when useful; give an evidence-based recommendation only when justified and label it recommendation; explain why the answer changes scope/safety/truth/verification; ask independent questions in a small batch; sequence dependent questions.

Do not ask the user to repeat repository facts. If an unknown is not needed for the current bounded Task, record it as non-blocking instead of asking. Return a concise decision record to the orchestrator. Do not edit files before the parent Human Gate.
