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

## Независимый clean-context review — round 2

Exact reviewed HEAD: `917fc172cc658d414409ac95a965fa31ba25626a`.

Verdict: `CHANGES_REQUIRED`.

Reviewer reported `P0/P1/P2/P3 = 0/8/0/0`. Blocking areas:

1. full-profile secret scan excluded tracked build/vendor/large content;
2. `repo-audit --output` could overwrite target-repository files;
3. adoption doctor was not stage-aware;
4. mapped repository-local paths could escape through absolute/`..`/symlink paths;
5. placeholders and malformed nested config remained fail-open;
6. `new-task --contract` allowed missing source/non-Git targets/dangling-symlink writes;
7. telemetry wording remained unconditional in README/reference;
8. PR CI metadata referenced the HEAD SHA while checkout actually tested GitHub's generated merge commit.

All eight findings were accepted as valid and addressed in the subsequent review-fix commit with targeted regression coverage. A new clean-context review is required on the new exact HEAD.

## Author self-review after round-2 fixes

Focused self-review found one remaining edge inside finding #5 before external re-review: malformed scalar types in instruction/task fields were fail-closed but could be classified as incomplete instead of invalid, and optional lower-stage capability sections were not fully schema-checked. The doctor now treats those malformed values as `CONFLICT` and validates every present known capability section even when the current stage does not require it.

## Независимый clean-context review — round 3

Exact reviewed HEAD: `f95abce0f008c9d14f6b6f8f978ecc8689697832`.

Verdict: `CHANGES_REQUIRED`.

Reviewer reported `P0/P1/P2/P3 = 0/3/2/0`.

Accepted findings:

1. Stage 2–4 capability references were structurally configured but not evidence-bearing;
2. natural-language placeholder variants such as `TODO later` could bypass fail-closed guards;
3. the adoption config itself could be an external symlink and local task references were not containment-validated;
4. audit/new-task retained ancestor TOCTOU surface (P2);
5. workshop documentation still described merge-ref verification after CI moved to exact PR HEAD (P2).

The subsequent fix changes capability references to typed evidence references, broadens sentinel detection without rejecting IDs like `TODO-123`, rejects external config symlinks and local task-source escapes, makes repo-audit stdout-only, uses descriptor-relative no-follow creation in new-task, and aligns the workshop with exact-HEAD CI.

## Author fix after round-3 remediation CI

The first remediation commit failed strict template CI before tests because a generated regex/constants block in `scripts/repo-doctor` was syntactically malformed. The same inspection also caught over-escaped whitespace regexes. Both scripts were corrected before the next independent review; this failed CI attempt is retained as evidence rather than hidden.
