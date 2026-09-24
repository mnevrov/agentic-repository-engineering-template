# Трассируемость изменений

## Цель

Сделать историю агентской разработки проверяемой без навязывания тяжёлой иерархии Epic → Feature → Story каждому проекту.

## Минимальный уровень — обязателен

Для любой задачи в зрелом/full-profile процессе должна восстанавливаться цепочка:

```text
task source → execution contract / acceptance criteria → evidence → review → commit/PR
```

Task source может быть local Markdown, GitHub Issue, Jira, GitLab Issue или внутренний ID. Brownfield local contract фиксирует execution semantics и не обязан дублировать весь tracker item. На ранней adoption stage deferred review отмечается явно; Stage 3 восстанавливает полный independent-review link.

## Расширенный уровень — по необходимости

Для крупных, регулируемых или архитектурно насыщенных проектов используйте:

```text
requirement → ADR/design → task → code/test → evidence → review → commit/PR
```

Epic/Feature/Story остаются optional: добавляйте их только если они реально помогают планированию.

## Правила

- Существенное архитектурное решение должно ссылаться на ADR.
- Если ADR/requirement неприменимы, укажите `n/a`, а не придумывайте связь.
- Review artifact или project-native equivalent должен ссылаться на проверенный diff/SHA и Task ID/execution contract.
- Evidence должен быть воспроизводимым и соответствовать `evidence-ladder.md`.
- Исправление после review остаётся в той же Task, пока scope не изменился; новый scope становится новой Task.
