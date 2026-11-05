# OpenCode v2 — operational contract

Этот template поддерживает **только OpenCode v2**. Минимальная проверенная версия: **OpenCode v2.2.5**. Версия v2.1.2 не загружает проектных агентов на чистом CI, хотя проектные источники конфигурации обнаружены; приёмка намеренно завершается ошибкой до обновления. Сверка формата с официальной документацией: https://dev.opencode.ai/v2/docs/config/ , https://dev.opencode.ai/v2/docs/agents/ , https://dev.opencode.ai/v2/docs/commands/ , https://dev.opencode.ai/v2/docs/skills/ .

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

Для CI используется матрица: `@opencode/cli@2.1.2` как **ожидаемое отклонение** несовместимой версии и `@opencode/cli@2.2.5` как поддерживаемый успешный проход, без model credentials и inference. Этот шаг **не** подтверждает реальную работу модели или Human Gate.

## Локальная проверка без обращения к модели

```bash
make opencode-acceptance
```

Проверяется установленный OpenCode v2, конфигурация и точные **ID** subagents без вывода конфигурации провайдера. CLI вывод перенаправляется во временные regular files, так как OpenCode/Bun может обрезать большие JSON-потоки при pipe; они удаляются при завершении проверки. Не путайте с подключённой приёмкой LiteLLM.


## Если `make opencode-acceptance` не видит subagents

Если тесты шаблона проходят, а `reviewer`, `repository-discovery` и другие проектные агенты отсутствуют в выводе `opencode debug agents`, сначала проверьте **загрузку проектной конфигурации**. Путь `.opencode/agents/` корректен для V2; не переносите файлы в глобальную конфигурацию без необходимости.

Из корня репозитория:

```bash
opencode --version
printenv OPENCODE_DISABLE_PROJECT_CONFIG
opencode debug agents
```

Если `OPENCODE_DISABLE_PROJECT_CONFIG=1`, удалите настройку из shell startup / launcher и выполните `unset OPENCODE_DISABLE_PROJECT_CONFIG`. **Важно:** фоновый сервис наследует переменные среды при старте, поэтому очистки текущей shell может быть недостаточно. Завершите активные сессии OpenCode перед перезапуском:

```bash
opencode service stop
opencode service start
make opencode-acceptance
```

Если переменная не установлена, проблема всё равно может быть в окружении уже запущенного сервиса или в глобальных переопределениях. Просмотрите пути источников в `opencode debug config` **локально**, не пересылайте его полный вывод: там может оказаться конфигурация с секретами. Проверьте отсутствие `OPENCODE_DISABLE_PROJECT_CONFIG` в systemd/launcher/editor окружении; после исправления перезапустите сервис. Сопоставимый подтверждённый случай: https://github.com/anomalyco/opencode/issues/53839 .

**Не считать PASS** до появления всех ожидаемых project agents. При отсутствии реальной проверки в корпоративном HOST не повышать evidence до E3/E4.

## Production acceptance

1. `opencode --version` подтверждает установленный V2.
2. В новом репозитории `/develop`, `/iterate`, `/adopt-existing`, `/grill-me` обнаруживаются.
3. `reviewer` и discovery subagents действительно доступны и не могут редактировать проект.
4. Глобальный/корпоративный провайдер используется без токенов в Git. Для enterprise допускаются дополнительные управляемые политики.
5. В новом проекте проверены оба сценария: positive flow `PROJECT-BOOTSTRAP` и negative flow с ненастроенными gates; CI проходит на exact SHA.
6. Реальный OpenCode run, independent review, restore-after-new-session и демонстрация фиксируются как отдельные E3/E4 evidence. GitHub CI **не эквивалентен** HOST acceptance.

## Безопасность

V2 permissions отличаются от V1 (`permissions`, `shell`, `subagent`). Порядок правил значим: поздние правила переопределяют ранние. Изменение model/provider и расширение разрешений должны рассматриваться как отдельная Task. Не запускайте `--auto` для high-risk изменений без политик, принудительно запрещающих нежелательные операции.

## Версия 2.1.2: обнаружение агентов не проходит

На GitHub Actions (2026-11-05) проверка из этого репозитория нашла: с OpenCode 2.1.2 все три требуемых project agent ID отсутствуют; с 2.2.5 они присутствуют. Это воспроизведено с прямым перенаправлением полного CLI JSON в файл, без проблем pipe truncation. Поэтому версия **2.1.2 не поддерживается** для production acceptance. Обновите CLI до проверенной версии:

```bash
opencode upgrade 2.2.5
opencode --version
opencode service stop
opencode service start
make opencode-acceptance
```

Проверяйте фактически установленную версию после обновления; при управляемой корпоративной установке согласуйте обновление с администратором.

## Большой JSON в `opencode debug agents`

Если `opencode debug agents | python3 -c '...json.load(...)'` или `| jq` даёт `JSONDecodeError` приблизительно на 64/128/192 КиБ, это может быть известная upstream проблема асинхронной записи stdout в pipe: https://github.com/anomalyco/opencode/issues/29330 . Подтверждайте без передачи prompt/credentials:

```bash
make opencode-acceptance
```

Скрипт использует временный regular file, парсит JSON целиком и проверяет `id` агентов, а не вхождение имени в описания. Не сохраняйте и не публикуйте сырой JSON: в нём может быть содержимое системных инструкций.
