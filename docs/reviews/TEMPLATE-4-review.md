# Независимая проверка — TEMPLATE-4

**Дата:** 2026-09-24  
**Проверяющий:** CodeRabbit external reviewer  
**Контекст:** independent / clean PR review  
**Риск задачи:** B  
**Проверенный diff:** `6f26c9b4a537bcf977b28fdb597264ec96d81665..3bff1620cfe5ce64c59ae017f91efd85b479dd70`  
**PR:** #5

## Итог первого независимого раунда

**Verdict:** changes_required

CodeRabbit выполнил full review всех 48 изменённых файлов и опубликовал четыре actionable Major findings. Для внутренней severity model TEMPLATE-4 они классифицированы как P1, потому что каждый мог нарушить заявленный adoption contract или дать false-green/неверный target repository.

| Severity | Область | Finding | Closure |
|---|---|---|---|
| P1 | `docs/process/telemetry.md` | Stage 1 разрешал deferred telemetry, но дальнейший текст всё ещё объявлял recording/CI enforcement обязательными всегда. | Правила recording/CI явно ограничены профилями с включённой telemetry policy. |
| P1 | `scripts/repo-audit`, `scripts/repo-doctor`, tests | Унаследованные `GIT_DIR`/`GIT_WORK_TREE` и связанные overrides могли заставить Git-команды работать не с target `cwd`. | Добавлена очистка repository-location Git env + regression tests. |
| P1 | `scripts/repo-doctor` | Task source мог считаться configured без идентифицируемого `reference`. | Reference теперь обязателен для configured task source; пустой/TODO → `NOT_CONFIGURED`. |
| P1 | `scripts/repo-doctor` | Отсутствующие `verification.check/test` могли пройти как OPTIONAL и дать exit 0. | Omitted `check/test` теперь `NOT_CONFIGURED` + exit 2; integration остаётся optional только при явной семантике. |

## Дополнительный сигнал reviewer

CodeRabbit показал warning по docstring coverage. Он не является функциональным finding и в repository нет принятого docstring threshold; поэтому он не используется как merge blocker для этой Task.

## Verification closure

После исправления выполняются новые regression scenarios:

- audit/doctor игнорируют inherited Git repository-location overrides;
- external task source без reference остаётся incomplete;
- отсутствующие check/test gates остаются fail-closed;
- существующие brownfield regression tests сохраняются.

Точный final HEAD после этого closure commit должен снова пройти GitHub CI и independent external re-review. Результат final-HEAD re-review хранится в PR #5, а не дописывается в этот файл после review, чтобы не сдвигать уже проверенный HEAD.
