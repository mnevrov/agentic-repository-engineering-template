# TEMPLATE-2 — Подробный русскоязычный onboarding

**Статус:** in review  
**Риск:** A  
**Human gate:** delegated  
**Владелец:** repository owner  
**Связанный эпик/этап:** template usability  
**Requirements / ADR:** n/a

## Зачем

Текущая документация описывает отдельные механизмы шаблона, но новому разработчику недостаточно ясно, в каком порядке подготовить новый проект и пройти первый полный агентский цикл.

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
- integration: `repo-doctor`, `make test-template`, documentation link/content review;
- e2e/live: ручная проверка onboarding последовательности;
- ожидаемый evidence level: E1/E2 для структуры шаблона, manual documentation validation для содержимого.

## Доказательства

- команды: CI/template checks после публикации ветки;
- результаты: pending CI;
- артефакты: `README.md`, `docs/GETTING_STARTED.md`, `docs/reference/commands.md`;
- фактический evidence level: pending;
- что не проверено: independent review будет явно waived для этой документационной итерации по решению владельца.

## Review

- self-review: структура и непротиворечивость проверены автором;
- independent review artifact: waived by repository owner for this documentation iteration;
- остаточные замечания: проверить CI после PR.

## Traceability

- requirement/ADR → task: запрос владельца на подробную русскоязычную документацию → TEMPLATE-2;
- task → evidence: этот файл + onboarding/reference docs;
- task → commit/PR: будет заполнено после публикации.
