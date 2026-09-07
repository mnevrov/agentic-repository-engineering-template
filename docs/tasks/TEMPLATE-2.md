# TEMPLATE-2 — Подробный русскоязычный onboarding

**Статус:** done (review waived)  
**Риск:** A  
**Human gate:** delegated  
**Владелец:** repository owner  
**Связанный эпик/этап:** template usability  
**Requirements / ADR:** n/a

## Зачем

Текущая документация описывала отдельные механизмы шаблона, но новому разработчику было недостаточно ясно, в каком порядке подготовить новый проект и пройти первый полный агентский цикл.

## Объём

### Входит

- единая подробная инструкция начала работы на русском языке;
- ясный quick start в README;
- настройка fail-closed project gates;
- подготовка project memory;
- создание Task и Acceptance Criteria;
- запуск OpenCode/Codex CLI/Claude Code;
- объяснение human gate, review, evidence, telemetry, commit/PR;
- справочник команд;
- актуализация примера первого цикла;
- документирование явного исключения из independent-review gate.

### Не входит

- изменение runtime/tooling поведения шаблона;
- интеграция новых AI-провайдеров;
- продуктовые детали конкретного downstream проекта.

## Критерии приёмки

- [x] AC-1: новый пользователь может начать с README и перейти к одному каноническому onboarding документу.
- [x] AC-2: onboarding покрывает путь от создания репозитория до commit/PR первой Task.
- [x] AC-3: явно объяснено исходное состояние `NOT CONFIGURED` и порядок настройки `Makefile`.
- [x] AC-4: описаны OpenCode, Codex CLI и Claude Code без привязки общего процесса к одному агенту.
- [x] AC-5: human gate, risk A/B/C, clean-context review, evidence E0–E5 и telemetry объяснены практическими шагами.
- [x] AC-6: есть отдельный справочник основных команд.
- [x] AC-7: документация описывает review waiver как исключение, а не как фиктивный approved review.

## Архитектурные ограничения

- документация остаётся provider-neutral;
- основной долговременный контекст хранится в Git;
- фактические и примерные команды должны быть явно различимы.

## План проверки

- unit: n/a;
- integration: `repo-doctor`, `make test-template`, telemetry validation/enforcement в CI;
- e2e/live: ручная проверка последовательности onboarding и ссылок между документами;
- ожидаемый evidence level: E1/E2 для структуры/tooling шаблона, manual validation для содержимого документации.

## Доказательства

- команды: GitHub Actions `Repository Doctor`, run `34165835482`;
- результаты: PASS — repository skeleton, telemetry validation/enforcement, template tests и project-gate contract;
- артефакты: `README.md`, `docs/GETTING_STARTED.md`, `docs/reference/commands.md`, `docs/examples/first-agent-cycle.md`;
- фактический evidence level: E2 для template tooling; содержимое документации прошло self-review на непротиворечивость;
- что не проверено: independent review явно waived владельцем репозитория для этой документационной итерации.

## Review

- self-review: структура, последовательность onboarding и согласованность с текущими guardrails проверены;
- independent review artifact: waived by repository owner for this documentation iteration;
- остаточный риск: возможны редакционные улучшения после реального использования onboarding новым разработчиком.

## Traceability

- requirement/ADR → task: запрос владельца на подробную русскоязычную документацию → TEMPLATE-2;
- task → evidence: этот файл + onboarding/reference docs + CI run `34165835482`;
- task → commit/PR: PR #2, branch `docs/getting-started`.
