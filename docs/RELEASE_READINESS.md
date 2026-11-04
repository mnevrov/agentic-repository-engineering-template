# Release readiness — OpenCode v2

**Статус: RELEASE CANDIDATE; выпуск в production не подтверждён.**

Этот репозиторий — шаблон инженерного процесса, а не автономный оркестратор. Поддерживается только OpenCode v2, а модель/провайдер задаются доверенным окружением пользователя.

## Технические проверки

| Критерий | Способ проверки | Статус |
|---|---|---|
| Fail-closed project gates и template tests | GitHub Actions Repository Doctor | Автоматизировано |
| Отдельный bootstrap и защита от повторного запуска | Downstream greenfield smoke | Автоматизировано |
| Нативная OpenCode v2 конфигурация и discovery | Pinned CLI GitHub Actions | Автоматизировано |
| OpenCode CLI на целевом хосте | make opencode-acceptance | Не проверено на HOST |
| Реальный полный цикл с внутренней моделью LiteLLM | Одна bounded Task, new-session recovery | Не проверено на HOST |
| Независимый review exact final PR HEAD | Сохранённый review artifact | Ожидается |
| Обязательные CI/review для main | GitHub branch rules | Не настроено через текущий доступ |
| Версионированный production release | GitHub tag/release после всех gate | Не создан |

## Граница доказательств

CI подтверждает работу bootstrap и парсинг OpenCode CLI без запроса к модели. Это не E4, не доказательство доступа к корпоративному LiteLLM и не подтверждение фактического Human Gate в OpenCode.

## Ручной HOST acceptance

1. Создать отдельный новый GitHub repository из шаблона.
2. Выполнить scripts/init-project один раз и убедиться, что повтор заблокирован.
3. Выполнить make opencode-acceptance без логирования токенов.
4. Настроить real make check и make test (no zero-test green).
5. Провести через OpenCode /develop для bootstrap Task с внутренней моделью.
6. Проверить независимый reviewer, AC/evidence/telemetry, начало новой сессии и восстановление Git-контекста.
7. Получить зелёный exact-head CI и review, затем зафиксировать проверенный release tag.

Неизвестное остаётся неизвестным: отсутствие данных по токенам или стоимости не равно нулю.
