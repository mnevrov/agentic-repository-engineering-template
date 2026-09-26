# Agent orchestration for repository adoption

Brownfield discovery не должен выполняться одним длинным prompt, если runtime поддерживает isolated subagents.

## Роли

**Repository Discovery** — read-only topology/build/test/CI/docs map.

**Verification Discovery** — read-only поиск existing check/test/integration commands; candidate не равен authoritative.

**Context & Truth** — read-only instructions, architecture/RFC/ADR, task sources, precedence ambiguity; documented fact отделяется от implementation observation/inference/unknown.

**Gap Analysis** — синтез evidence в `EXISTS / EXISTING_EQUIVALENT / PARTIAL / MISSING / NOT_APPLICABLE / CONFLICT`.

**Adoption Orchestrator** — получает evidence summaries, оставляет non-blocking unknowns, использует structured questioning только для blocking decisions, формирует minimum plan и останавливается на Human Gate.

## Grill-me

Если blocking question нельзя закрыть repository evidence, orchestrator использует `grill-me`: показать evidence, сформулировать exact decision, предложить варианты, объяснить impact и не спрашивать discoverable facts.

## Когда subagents не нужны

Не делегируйте один exact-file lookup или маленькую последовательную проверку. Subagents нужны для независимых workstreams, isolated context и independent verification.

## Provider neutrality

`.claude/agents/` и `.claude/skills/` — native adapter для Claude Code. Другие harnesses должны реализовать те же role boundaries своими agent primitives. `ADOPT_EXISTING_PROMPT.md` — fallback, когда subagents отсутствуют.
