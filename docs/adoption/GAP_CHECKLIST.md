# Brownfield adoption gap checklist

Заполняйте после read-only audit и проверки repository evidence. Не превращайте `NOT_DETECTED` в `MISSING`, пока не проверены external/project-specific mechanisms.

Допустимые состояния: `EXISTS`, `EXISTING_EQUIVALENT`, `PARTIAL`, `MISSING`, `NOT_APPLICABLE`, `CONFLICT`.

| Область | Статус | Existing source/evidence | Минимальное действие | Human decision |
|---|---|---|---|---|
| Repository instructions |  |  |  |  |
| Instruction precedence |  |  |  |  |
| Build command |  |  |  |  |
| Fast check/lint/static analysis |  |  |  |  |
| Unit/contract tests |  |  |  |  |
| Integration/e2e |  |  |  |  |
| CI/merge gates |  |  |  |  |
| Architecture/design source |  |  |  |  |
| Decision record (ADR/RFC/etc.) |  |  |  |  |
| Security/trust boundaries relevant to pilot |  |  |  |  |
| Backlog / issue tracker |  |  |  |  |
| Local execution contract |  |  |  |  |
| Review mechanism |  |  |  |  |
| Risk model |  |  |  |  |
| Evidence/traceability |  |  |  |  |
| Telemetry/metrics |  |  |  |  |

Перед первой bounded Task должны быть известны: repository instructions, relevant precedence, authoritative verification или честный blocker, existing task source, local contract, relevant architecture/security constraints и Human Gate policy.

Не требуется до первой Task: полный architecture rewrite, retrospective ADR catalogue, новый CI, новый Makefile, новый tracker или полная telemetry platform.
