# Fallback: existing repository adoption

Используйте этот файл только если runtime не умеет запускать специализированные subagents. Иначе используйте `docs/process/agent-orchestration.md` и native agents.

До Human Gate работай read-only. Изучи deterministic audit, instructions, build/test/lint, CI, docs, architecture/RFC/ADR и task sources. Различай fact, candidate и unknown; не требуй template layout; не создавай architecture rules из assumptions.

Построй gap analysis. Blocking uncertainty, которое нельзя закрыть repository evidence, эскалируй через доступный `grill-me`/structured-questioning skill. Не спрашивай человека то, что можешь доказать самостоятельно.

Предложи minimum Stage-1 plan: source mapping, confirmed verification semantics и одну existing bounded Task. Перечисли exact proposed file changes и остановись на Human Gate.

До подтверждения не создавай, не редактируй, не удаляй, не переименовывай и не commit'ь файлы target repository.
