# Участие в разработке

Этот репозиторий использует один и тот же процесс для человека и AI-агента.

Если вы впервые работаете с проектом, сначала прочитайте [`docs/GETTING_STARTED.md`](docs/GETTING_STARTED.md).

## Перед началом работы

1. Прочитайте `AGENTS.md`.
2. Откройте `docs/INDEX.md`.
3. Проверьте текущие ROADMAP/TODO.
4. Прочитайте релевантную архитектуру и ADR.
5. Выберите одну Task или создайте её через `scripts/new-task`.
6. Убедитесь, что scope и Acceptance Criteria измеримы.
7. Определите риск A/B/C и human gate.

## Во время разработки

Следуйте [`docs/process/development-cycle.md`](docs/process/development-cycle.md).

Основные ограничения:

- одна небольшая Task за цикл;
- несвязанные изменения не смешиваются;
- архитектурные решения не принимаются молча;
- тесты не ослабляются ради зелёного результата;
- непроведённая проверка не описывается как PASS;
- значимые найденные соседние проблемы выносятся в TODO.

## Перед Pull Request

Запустите применимые проверки, например:

```bash
./scripts/repo-doctor
make check
make test
make test-template
make telemetry-check
```

и `make test-integration`, если он нужен для изменения.

Проведите self-review, затем independent clean-context review. Сохраните результат в `docs/reviews/<TASK-ID>-review.md`.

Если review-gate явно пропущен ответственным человеком как исключение, это должно быть записано в PR/Task; такой review нельзя помечать `approved`, а cycle остаётся `partial`.

## Требования к Pull Request

PR должен отвечать на вопросы:

- какую Task он решает;
- что входит и не входит в scope;
- какие Acceptance Criteria выполнены;
- что фактически изменилось;
- какие команды проверки реально запускались;
- какой evidence level достигнут;
- где independent review artifact или зафиксированное исключение;
- какие ограничения и остаточные риски остаются.

Перед merge проверьте [`docs/process/definition-of-done.md`](docs/process/definition-of-done.md).
