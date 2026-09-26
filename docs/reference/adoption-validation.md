# Brownfield adoption — validation reference

Этот документ содержит низкоуровневые правила validation contract для `repo-doctor --adoption` и `new-task --contract`.

Он дополняет основной onboarding: [`../ADOPT_EXISTING_REPOSITORY.md`](../ADOPT_EXISTING_REPOSITORY.md).

## Evidence и task references

Typed `url` evidence must be a syntactically valid absolute HTTP(S) URL with a valid host/port and without whitespace, control characters or embedded credentials. A `path` evidence reference and local task source must resolve to an **existing repository-local regular file**; a directory is not evidence. `new-task --contract --source` accepts only a strict URL, compact external ID such as `JIRA-1842`, or an existing repository-local file reference such as `BACKLOG.md#LEGACY-17`.


Strict HTTP(S) evidence/task URLs additionally require every literal `%` to begin a complete two-hex-digit percent escape. Malformed forms such as `%ZZ`, `%` or `%0G` are invalid; normal escapes such as `%20`, `%2F` and `%25` remain valid. Compact external task IDs may contain `/` (for example `owner/repo#123`); `new-task` treats explicit/existing file references as local instead of using slash alone to infer a filesystem path.


Для неоднозначных task references `new-task` поддерживает `--source-kind external|local` (default `auto`). Например, `owner/repo#123` остаётся compact external ID даже если похожий local directory существует; extensionless local source можно зафиксировать явно через `--source-kind local --source tasks/current#TASK-1`.


`new-task` сохраняет resolved source namespace в execution contract отдельным полем `Тип источника: local|external`. В `auto` распространённые file-like suffixes (Markdown/text/YAML/JSON/TOML/INI/CFG/CSV/TSV/XML) трактуются как local и поэтому отсутствующий файл fail-closed. Если project-native external ID намеренно выглядит как file path, используйте `--source-kind external`; для нестандартного/extensionless local source — `--source-kind local`.


## Когда читать этот документ

Используйте его, если:

- `repo-doctor --adoption` возвращает invalid/conflict;
- нужно выбрать `path | url | external_id | command` для capability evidence;
- task reference неоднозначен между local и external;
- нужен `--source-kind local|external`;
- вы меняете validation tooling и обязаны сохранить fail-closed semantics.

Для первого знакомства с подходом этот уровень деталей не требуется.
