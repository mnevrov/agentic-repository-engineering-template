# OpenCode v2 — operational contract

Этот template поддерживает **только OpenCode v2**. Сверка формата с официальной документацией: https://dev.opencode.ai/v2/docs/config/ , https://dev.opencode.ai/v2/docs/agents/ , https://dev.opencode.ai/v2/docs/commands/ , https://dev.opencode.ai/v2/docs/skills/ .

## Источники конфигурации

- `AGENTS.md` — правила разработки, Human Gate и доказательства.
- `opencode.json` — V2 permissions. Модель/провайдер **намеренно отсутствуют**; используйте корпоративное окружение, например LiteLLM.
- `.opencode/commands/{develop,iterate,adopt-existing,grill-me}.md` — команды TUI.
- `.opencode/agents/` — read-only discovery, gap-analysis, review.
- `.opencode/skills/` — staged Brownfield adoption и точечные вопросы.

Никакие Claude Code/Codex настройки не поддерживаются. Не переносите `.opencode/` поверх существующего Brownfield проекта автоматически — сначала read-only discovery и согласованный минимальный слой.

## Начало Greenfield

```bash
git clone <new-project-repository>
cd <new-project-repository>
./scripts/init-project "Название проекта"
./scripts/repo-doctor --template
make test-template
opencode
```

Первый шаг в OpenCode: `/develop` для `PROJECT-BOOTSTRAP`. Реальные `make check` и `make test` должны быть настроены до пользовательских задач. `NOT CONFIGURED` означает блокировку, а не успех.

Для CI-проверки парсинга нативной конфигурации используется закреплённый `@opencode/cli@2.2.5`, без model credentials и inference. Этот шаг **не** подтверждает реальную работу модели или Human Gate.

## Локальная проверка без обращения к модели

```bash
make opencode-acceptance
```

Проверяется установленный OpenCode v2, конфигурация и обнаружение subagents без вывода конфигурации провайдера. Не путайте с подключённой приёмкой LiteLLM.

## Production acceptance

1. `opencode --version` подтверждает установленный V2.
2. В новом репозитории `/develop`, `/iterate`, `/adopt-existing`, `/grill-me` обнаруживаются.
3. `reviewer` и discovery subagents действительно доступны и не могут редактировать проект.
4. Глобальный/корпоративный провайдер используется без токенов в Git. Для enterprise допускаются дополнительные управляемые политики.
5. В новом проекте проверены оба сценария: positive flow `PROJECT-BOOTSTRAP` и negative flow с ненастроенными gates; CI проходит на exact SHA.
6. Реальный OpenCode run, independent review, restore-after-new-session и демонстрация фиксируются как отдельные E3/E4 evidence. GitHub CI **не эквивалентен** HOST acceptance.

## Безопасность

V2 permissions отличаются от V1 (`permissions`, `shell`, `subagent`). Порядок правил значим: поздние правила переопределяют ранние. Изменение model/provider и расширение разрешений должны рассматриваться как отдельная Task. Не запускайте `--auto` для high-risk изменений без политик, принудительно запрещающих нежелательные операции.
