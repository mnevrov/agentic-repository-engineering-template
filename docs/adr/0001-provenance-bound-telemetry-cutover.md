# ADR-0001 — Provenance-bound telemetry cutover

**Статус:** accepted  
**Дата:** 2026-11-05

## Контекст

Одноразовый cutover telemetry (замена source-only `TEMPLATE-*` реестра на первый проектный реестр) в baseline `2043f6d` открывался самим фактом наличия `.ai/project-initialized` в HEAD при отсутствии маркера в base ref. Independent release audit воспроизвёл PoC: клон исходного шаблона, поддельный маркер и замена 38 строк на одну выдуманную — оба telemetry-gate PASS. Условие было «навсегда взведено» против самого шаблона, потому что его история — это ровно «TEMPLATE-* без маркера в base».

## Варианты

### A — Проверяемая provenance-связка (выбран)

Исключение открывается только когда одновременно и fail-closed:

- **Identity:** `remote.origin.url` присутствует (ровно одно значение: multi-valued url даёт разъезд между transport (первое) и `git config --get` (последнее) и не является достоверной identity) и парсится в hosted `host/owner/repo`; отсутствие или непарсимость (локальный путь, `file://`, host без точки) запрещают исключение; identity не равна identity исходного репозитория (`github.com/mnevrov/agentic-repository-engineering-template`).
- **Lineage:** base ref — предок HEAD; маркер закоммичен в HEAD и читается только из HEAD-blob (worktree недоверенный); маркер отсутствует и в base ref, и в корневом коммите истории HEAD; единственность корня обязательна.
- **Baseline shape:** telemetry корневого коммита (если есть) source-only; base реестр source-only; новый реестр без `TEMPLATE-*`.

Плюсы: PoC закрыт без сети; корректный downstream bootstrap работает без изменений; правила симметричны guard'у `init-project`.
Минусы: downstream-репозиторий без origin обязан настроить origin до первого commit (явная, документируемая цена; CI smoke настраивает).

### B — Сетевая верификация lineage через GitHub API

Сильнее против форков, но вводит сеть, токены и недоступность в критический CI-gate. Не выбрано: remote сам по себе не доверенное удостоверение, и офлайн fail-closed важнее.

### C — Оставить маркер-only

Отклонено PoC аудита.

## Решение

Вариант A в `scripts/telemetry_cutover.py` (общий нормализатор URL используется `init-project`). После независимого adversarial-review контракт усилен: identity сравнивается по имени репозитория (зеркала на других хостях с тем же именем тоже запрещены), dot-segment псевдонимы URL отклоняются, `url.*.insteadOf`-переписывание, меняющее identity, запрещает исключение (identity-сохраняющие алиасы — см. round 4), multi-valued `remote.origin.url` не даёт identity, shallow-клон запрещает исключение, маркер обязан быть regular-file blob в HEAD, `base_ref` не может начинаться с `-`, и `history_monotonic` проверяет весь диапазон `base..HEAD` (а не только концы) — удалённая/переписанная в середине строка не прячется устаревшей base-веткой PR.

- Identity hardening (rounds 2-3): percent-путь декодируется ДО приведения к нижнему регистру (и `%61…`, и `%41…` псевдонимы больше не обходят deny; сервер case-insensitive); хвост `/.git` в URL раскрывает имя родительского репозитория (защита `clone /path/…/.git`). Маркер ищется НЕ-рекурсивным ls-tree: каталог на месте маркера не считается regular-file blob.
- Range integrity (rounds 2-4): `history_monotonic` сканирует диапазон по `--full-history --reverse`; два режима — исключение для промежуточных `TEMPLATE-*` предоставляется только при VERIFIED cutover-вердикте (`verified_cutover` из `bootstrap_cutover`), никогда на основании одной формы финального журнала (round 4: base-анцестор до появления журнала иначе лицензировал стирание TEMPLATE-* строк, например на root самого шаблона, где журнала нет); любой другой финальный журнал проверяется без исключений (удаление TEMPLATE-* строки с восстановлением base-префикса в PR самого шаблона блокируется); удаление файла журнала внутри диапазона запрещено всегда; оба gate читают журнал из HEAD-blob и отказывают при diverged worktree; каталог/симлинк на пути журнала — явная structural-ошибка, не строки; `refs/replace` и legacy `.git/info/grafts` запрещают исключение и сам range-scan (проверки целостности истории подняты в `history_monotonic`, оба gate наследуют их); `validate-telemetry.py` требует уникальные `cycle_id`.
- Git remote — необходимое, но не достаточное условие: это эвристика происхождения, а не криптографическое удостоверение. Остаточные риски: origin, вручную указывающий на посторонний hosted-репозиторий (PR с такой настройкой CI обходит identity-слой — но тот же автор может просто удалить проверки; gate защищает от маркер-only подмены и халатности); `GIT_CONFIG_*`/hook-манипуляции на машине, выполняющей gate; локальные чтения gate теперь берут HEAD, а не worktree. Это зафиксировано как принятый предел дизайна без сети.

## Последствия

- `bootstrap_cutover` больше никогда не открывает исключение для checkout'а source template или одноимённого зеркала (identity совпадает), для репозитория без достоверной hosted identity, для shallow-клона и при insteadOf-переписывании, меняющем host/owner/repo. Identity-сохраняющий алиас (например личный `url.git@github.com:.insteadOf https://github.com/`) исключение не ломает: gate спрашивает Git об эффективной цели (`ls-remote --get-url`) и сверяет identity до и после переписывания.
- Оба gate (`append-only`, `required`) проверяют монотонность журнала по всему диапазону `base..HEAD`, а не только на концах.
- CI downstream smoke обязано выставлять свой hosted origin.
- Downstream-проект обязан иметь собственное имя репозитория и настроенный `origin` до первого проверяемого коммита (GETTING_STARTED).
- Негативные Git-backed регрессии повторяют PoC аудита и все подтверждённые атаки adversarial-review (полный перечень раундов — `docs/reviews/TEMPLATE-15-review.md`; негативы и merge-позитивы — `template_tests/test_telemetry_cutover.py`).
