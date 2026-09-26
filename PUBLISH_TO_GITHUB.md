# Публичный template и подготовка версии для митапа

Публичный repository:

https://github.com/mnevrov/agentic-repository-engineering-template

Репозиторий уже используется как GitHub Template Repository. Этот документ больше не описывает первоначальное создание repository; он фиксирует **проверки публичной упаковки и правила подготовки meetup-версии**.

## Проверить публичную конфигурацию

Через GitHub UI убедитесь, что:

- repository public;
- включён **Template repository**;
- доступна кнопка **Use this template**;
- Wiki/Projects не используются без необходимости;
- README первым экраном показывает выбор Greenfield/Brownfield;
- [`docs/MEETUP.md`](docs/MEETUP.md) доступен слушателю без дополнительных пояснений.

При наличии GitHub CLI:

```bash
gh repo view mnevrov/agentic-repository-engineering-template
gh api repos/mnevrov/agentic-repository-engineering-template --jq '{is_template,visibility,default_branch,topics}'
```

## QR-код

Файл:

`docs/workshop/github-template-qr.png`

должен вести на:

https://github.com/mnevrov/agentic-repository-engineering-template

Перед выступлением QR проверяется с отдельного телефона/браузера, не только с машины ведущего.

## Что проверять в самом template repository

```bash
./scripts/repo-doctor --template
make test-template
make telemetry-check
```

Важно: в **самом reusable template** project gates `make check` / `make test` намеренно остаются `NOT CONFIGURED` и возвращают ненулевой код. Это fail-closed contract, а не ошибка публикации.

Зелёными `make check` / `make test` они должны стать уже в конкретном demo/product repository после настройки реальных project gates.

## Telemetry

Не удаляйте существующий `.ai/telemetry/cycles.jsonl` ради «чистой» публикации или презентации. Для full-profile template telemetry является append-only engineering evidence.

Если конкретный demo создаётся из template, его telemetry должна отражать реальные попытки, включая `partial` / `failed`, если они фактически были.

## Когда можно фиксировать meetup-версию

**Не создавайте meetup tag/release до полного тестового прогона.**

Источник текущего статуса:

[`docs/workshop/STATUS.md`](docs/workshop/STATUS.md)

Минимальный gate перед фиксацией:

1. отдельный demo repository реально создан из template;
2. bootstrap и project gates проверены;
3. DEMO-1…DEMO-4 пройдены либо эквивалентный утверждённый сценарий выполнен;
4. checkpoints реально checkout'ятся;
5. новая agent session восстанавливает context из repository;
6. Human Gate наблюдался на live-кандидате;
7. review/evidence/telemetry проверены;
8. Plan B реально восстановлен;
9. презентационная репетиция проведена с таймером;
10. QR и публичные ссылки проверены с внешнего устройства.

Только после этого можно:

- обновить `docs/workshop/STATUS.md` на verified;
- при необходимости опубликовать demo repository/checkpoints;
- создать meetup tag/release;
- зафиксировать точный commit/tag в слайдах.

До этого `main` остаётся рабочей веткой подготовки, а не обещанием неизменной meetup-версии.
