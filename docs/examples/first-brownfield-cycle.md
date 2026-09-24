# Первый brownfield cycle

Existing fixture имеет layout `legacy_app/`, tests в `qa/`, existing `CONTRIBUTING.md`/`CLAUDE.md`, свой GitHub Actions workflow и `LEGACY-17` в `BACKLOG.md`.

1. `/path/to/template/scripts/repo-audit --repo . --output /tmp/audit.md` — repository не меняется.
2. `/adopt-existing` или equivalent multi-agent workflow — discovery/verification/context subagents исследуют repo независимо; unresolved blocking conflict идёт в `grill-me`.
3. После Human Gate добавляется минимальный `.agentic-repository.json`.
4. `repo-doctor --adoption --repo .` проверяет mapping без требования `src/tests/Makefile/docs/tasks`.
5. Existing task получает execution contract:

```bash
/path/to/template/scripts/new-task --repo . --contract \
  --source 'BACKLOG.md#LEGACY-17' \
  LEGACY-17 'Collapse repeated internal whitespace'
```

6. После required Human Gate меняется только task-specific code/tests и запускаются existing `./scripts/check.sh` и `./scripts/test.sh`.

Existing layout, README, CLAUDE.md и CI не переписываются ради template. Repository memory усиливается только там, где следующий cycle реально нуждается в контексте.
