# Публикация и эксплуатационный статус GitHub Template

Шаблон уже опубликован: https://github.com/mnevrov/agentic-repository-engineering-template

GitHub repository имеет `is_template=true`, поддерживается только OpenCode v2. Сценарий создания нового исходного repository больше не актуален и не должен использоваться.

## Создание downstream-проекта

1. Нажмите **Use this template** в GitHub.
2. Создайте новый repository и склонируйте его.
3. Выполните из корня `./scripts/init-project "Название проекта"` ровно один раз.
4. Выполните `./scripts/repo-doctor --template` и `make test-template`.
5. Настройте настоящие `make check` / `make test` и запустите `opencode`.

Не используйте `git init` и `gh repo create` внутри уже опубликованного исходного репозитория.

## Release gate

Release candidate — не production release. Сверяйтесь с [docs/RELEASE_READINESS.md](docs/RELEASE_READINESS.md), [issue #9](https://github.com/mnevrov/agentic-repository-engineering-template/issues/9) и [docs/workshop/STATUS.md](docs/workshop/STATUS.md). До завершения HOST acceptance, независимого review и branch protection новый production tag не выпускайте.

Для митапа: [docs/MEETUP.md](docs/MEETUP.md).
