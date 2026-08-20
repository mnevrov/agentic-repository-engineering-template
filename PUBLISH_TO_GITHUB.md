# Публикация как GitHub Template Repository

Целевой публичный адрес для раздачи слушателям:

```text
https://github.com/mnevrov/agentic-repository-engineering-template
```

## Вариант 1 — через GitHub CLI

Требуется установленный и авторизованный `gh`:

```bash
gh auth status
```

Из корня этого каталога:

```bash
git init
git add -A
git commit -m "initial template"

gh repo create mnevrov/agentic-repository-engineering-template \
  --public \
  --description "Template repository for controlled AI-agent development cycles" \
  --source . \
  --remote origin \
  --push

gh api -X PATCH repos/mnevrov/agentic-repository-engineering-template \
  -f is_template=true \
  -f has_issues=true \
  -f has_projects=false \
  -f has_wiki=false

gh repo edit mnevrov/agentic-repository-engineering-template \
  --add-topic ai-agents \
  --add-topic repository-template \
  --add-topic engineering-process \
  --add-topic adr \
  --add-topic tdd
```

После этого на странице репозитория появится кнопка **Use this template**.

## Вариант 2 — через интерфейс GitHub

1. Создайте новый публичный репозиторий `agentic-repository-engineering-template`.
2. Загрузите содержимое этого каталога в `main`.
3. Откройте **Settings → General → Template repository**.
4. Включите флаг **Template repository**.
5. Отключите Wiki/Projects, если они не нужны.
6. Добавьте topics: `ai-agents`, `repository-template`, `engineering-process`, `adr`, `tdd`.

## Проверка перед публикацией

```bash
./scripts/repo-doctor
make check
make test
python scripts/record-cycle.py \
  --task EXAMPLE-1 \
  --started 2026-08-20T12:00:00Z \
  --ended 2026-08-20T12:20:00Z \
  --result passed \
  --risk A \
  --model dry-run \
  --review-rounds 1 \
  --evidence docs/tasks/EXAMPLE-1.md
python scripts/telemetry-summary.py
```

Если не хотите публиковать демонстрационную запись телеметрии, удалите `.ai/telemetry/cycles.jsonl` перед коммитом.

## QR-код

Файл `docs/workshop/github-template-qr.png` указывает на будущий публичный URL:

```text
https://github.com/mnevrov/agentic-repository-engineering-template
```
