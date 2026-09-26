# Внедрение в существующий repository

Этот путь предназначен для brownfield-проектов: код, Git-история, структура, build/test/lint, CI, backlog и инженерные правила уже существуют. **Не создавайте новый repository из template и не копируйте его дерево поверх проекта.** Template адаптируется к проекту, а не наоборот.

> Не нужно описывать весь существующий проект до первой AI-задачи. Нужно создать минимально достаточный проверяемый контекст для безопасной следующей задачи и улучшать repository memory итеративно.

## Когда использовать

Используйте brownfield adoption, если проект уже имеет production code, Git history, CI, build/test commands, issue tracker, CONTRIBUTING/README, architecture/design/RFC/ADR или AI instructions. Для нового проекта используйте [`GETTING_STARTED.md`](GETTING_STARTED.md).

## Сначала discovery — никаких изменений

```bash
git clone --depth 1 https://github.com/mnevrov/agentic-repository-engineering-template.git /tmp/agentic-repository-template
cd existing-project
python3 /tmp/agentic-repository-template/scripts/repo-audit --repo . > /tmp/agentic-repository-audit.md
```

`repo-audit` только читает repository. Он обнаруживает common build files, test-related paths, CI, instructions, docs, ADR/RFC/design paths, backlog-like files и candidate verification commands. Candidate не становится authoritative автоматически. Security-sensitive detection path-based и не печатает возможные secret values.

## Agent orchestration вместо большого prompt

Предпочтительный workflow:

1. **Repository Discovery** — topology, languages/build markers, tests, CI, docs.
2. **Verification Discovery** — existing check/test/integration gates и evidence.
3. **Context & Truth** — AI/contributor instructions, architecture/RFC/ADR, task sources, source-of-truth ambiguity.
4. **Gap Analysis** — `EXISTS / EXISTING_EQUIVALENT / PARTIAL / MISSING / NOT_APPLICABLE / CONFLICT`.
5. **Adoption Orchestrator** — минимальный plan и Human Gate.

Claude Code adapter находится в `.claude/agents/`, orchestration skill — `/adopt-existing`, questioning skill — `/grill-me`. [`ADOPT_EXISTING_PROMPT.md`](../ADOPT_EXISTING_PROMPT.md) — только fallback для runtimes без subagents.

## Когда спрашивать человека

Сначала исчерпайте repository evidence. `grill-me` нужен только для blocking decision, влияющего на scope, safety, verification или source-of-truth. Типичные случаи: несколько несовместимых instruction sources; CI и docs расходятся в merge gate; authoritative external tracker неизвестен; project-native risk model требует mapping.

Non-blocking unknown оставляйте unknown, а не превращайте adoption в интервью.

## Gap analysis

Используйте [`adoption/GAP_CHECKLIST.md`](adoption/GAP_CHECKLIST.md). Автоматический audit выдаёт осторожные `DETECTED / CANDIDATE / NOT_DETECTED / NEEDS_CONFIRMATION`; окончательный gap status появляется только после проверки.

## Минимальный permanent layer

После Human Gate добавьте только нужное. Базовый mapping — `.agentic-repository.json`; пример: `.ai/templates/ADOPTION_CONFIG.json`.

Mapping не дублирует docs, а указывает их location и verification semantics. Он фиксирует explicit source-of-truth precedence, existing instructions/architecture/decision/task/CI sources, check/test/integration commands, unresolved conflicts и blocking open questions.

Не добавляйте новый Makefile только ради uniformity. Existing `cmake --build`, `ctest`, `ninja`, `pytest`, `npm test`, `cargo test` или project scripts можно использовать напрямую, если они подтверждены как authoritative.

Проверка mapping:

```bash
/tmp/agentic-repository-template/scripts/repo-doctor --adoption --repo .
```

Exit: `0` consistent; `2` context ещё не настроен/неполон, repository не broken; `1` invalid mapping/conflict.

## Existing CI, docs и AI instructions

Не копируйте template CI поверх существующего. Не перезаписывайте `AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING.md`, Copilot/Cursor rules. Если существующие mechanisms выполняют нужную функцию, mapping ссылается на них.

## Existing architecture / ADR / RFC

Не реконструируйте всю историю. Ретроспективно фиксируйте только факты и invariants, необходимые для текущей bounded Task. Если проект использует RFC/design docs — продолжайте их использовать. Если formal decision log отсутствует, ADR можно начать с новых существенных решений. Наблюдаемое legacy-поведение не объявляется architectural invariant без подтверждения.

## Existing backlog

Jira, GitHub/GitLab Issues, Markdown backlog и внутренние IDs остаются task-management source of truth. Для local task-source kinds (`markdown-backlog`, `local-file`) reference трактуется как repository-local path с optional `#fragment` и проходит containment validation. Для external kinds reference должен быть конкретным URL/ID. Для agentic cycle нужен лишь local execution contract:

```bash
/tmp/agentic-repository-template/scripts/new-task \
  --repo . --contract \
  --source JIRA-1842 \
  JIRA-1842 "Короткое название"
```

По умолчанию создаётся `.agentic/tasks/JIRA-1842.md`: scope, out-of-scope, AC, risk/human gate, relevant sources, verification/evidence и traceability.

## Первая пилотная Task

Выберите существующую небольшую задачу с наблюдаемым acceptance signal, ограниченной областью и применимыми existing checks. Не начинайте с destructive/security migration и не делайте «описать весь legacy» первой Task.

До кода agent показывает external task reference, local contract, scope/out-of-scope, AC, relevant constraints, authoritative verification, risk и plan; затем выполняется Human Gate текущей стадии/project policy.

## Первый controlled cycle

```text
existing task → local contract → mapped repository context
→ human gate → small implementation → existing checks/tests
→ applicable review/evidence → commit/PR
```

Не заявляйте full-profile compliance, если соответствующие gates ещё не включены.

## Стадии adoption

**Stage 1 — Minimum context:** source map, реальные verification semantics, одна bounded Task.

**Stage 2 — Repeatable workflow:** стабильный Task contract, AC, evidence и DoD.

**Stage 3 — Independent verification:** clean-context review/project equivalent, exact SHA/diff evidence, CI/PR linkage.

**Stage 4 — Risk-aware enforcement:** A/B/C либо existing risk model, stronger high-risk gates, adversarial review и technical enforcement.

`repo-doctor --adoption` проверяет stage fail-closed. Для Stage 2 mapping должен явно подтвердить repeatable-workflow capabilities (Task contract, AC, evidence, DoD); Stage 3 дополнительно — review mechanism, exact SHA/diff evidence и CI/PR linkage; Stage 4 — risk model, high-risk gates, adversarial review и technical enforcement. Простая смена значения `stage` без этих capabilities даёт `NOT_CONFIGURED`, а не false green.

Configured capability использует **typed evidence reference**, а не описательную строку:

```json
{
  "status": "configured",
  "reference": {"type": "path", "value": "GOVERNANCE.md#independent-review"}
}
```

Допустимые reference types:

- `path` — существующий repository-local path, допускается `#fragment`; absolute/`..`/symlink escape запрещены;
- `url` — абсолютный `http(s)` URL без embedded credentials;
- `external_id` — компактный внешний identifier, например `JIRA-1842` или `POLICY:RISK-1`;
- `command` — exact command, уже присутствующий среди configured verification commands.

Значения вроде `"yes"`, `"project risk policy"` или `"TODO later"` не являются evidence.

Telemetry обязательна в greenfield/full profile, но не prerequisite Stage 1 brownfield adoption.

## Что не автоматизируется

Tooling не должен сам менять production layout, выбирать authoritative command по convention, переписывать CI/Git flow/backlog/AI instructions, объявлять inferred architecture фактом, массово создавать retrospective ADR или разрешать source-of-truth conflicts.


## Детали validation contract

Основной onboarding выше описывает процесс adoption. Низкоуровневые правила typed evidence, strict URL validation, repository-local paths и `new-task --source-kind` вынесены в справочник:

[`reference/adoption-validation.md`](reference/adoption-validation.md)

Они нужны при настройке mapping/tooling и при разборе ошибок `repo-doctor`, но не являются prerequisite для понимания первого Brownfield cycle.
