# Release playbook — v0.1.0

**Status:** PREPARED / BLOCKED. Не исполнять выпуск до выполнения всех hard gate ниже. Исходный код TEMPLATE-15 закрыт, новые adversarial-раунды не планируются.

## 1. Факты на 6 ноября 2026

- Source repository: `mnevrov/agentic-repository-engineering-template`, `main` без защиты (`protected=false`), rulesets `[]` при проверке.
- Latest *verified before this release-prep PR* source main CI: SHA `59e432167dd3d223c96d0bf966d2977949f84bd4`, [run 42196905872](https://github.com/mnevrov/agentic-repository-engineering-template/actions/runs/42196905872), PASS: doctor, OpenCode v2.1.2 negative, v2.2.5 positive.
- Pilot: SHA `d2fdf020be2a465549f31896c84e6be02132eb36`, [run 42198531178](https://github.com/mnevrov/agentic-template/actions/runs/42198531178), PASS: 7 unit tests, 2 isolated Git-backed integration tests, 96 template tests (записано в Actions log). Это E3 компоненты, не HOST/LLM acceptance.
- Release tag `v0.1.0` и GitHub Release отсутствуют; `release/v0.1.0-rc.1` не менять.
- GitHub connector, доступный в этом workflow, не поддерживает POST rulesets, создание signed tag или GitHub Release. **Загруженный JSON сам по себе ничего не защищает.**
- Final independent *release* review exact SHA остаётся отдельным gate. Принятое TEMPLATE-15 adversarial review не выдавать за него.

## 2. Защитить main (нужны администраторские права репозитория)

Рекомендуемый способ — `docs/release/MAIN_RULESET.json`, проверенный по GitHub REST Create Repository Ruleset. Он требует PR, проверок `doctor`, `OpenCode v2.1.2 configuration` и `OpenCode v2.2.5 configuration`, запрета удаления/force-push и закрытия обсуждений. Состояние `required_approving_review_count=0` выбрано для single-maintainer; формальное независимое release-review остаётся ручным gate. **При появлении второго reviewer установить значение 1**.

GitHub UI: `Settings → Rules → Rulesets → New ruleset → New branch ruleset`. Если план GitHub для приватного репозитория не поддерживает Rulesets, используйте `Settings → Branches → Add classic branch protection rule` с эквивалентными ограничениями. См. актуальную [инструкцию GitHub](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/creating-rulesets-for-a-repository).

Для администратора с заранее авторизованным `gh` (никаких токенов в командной строке/файлах):

```bash
gh api --method POST \
  repos/mnevrov/agentic-repository-engineering-template/rulesets \
  --input docs/release/MAIN_RULESET.json
gh api repos/mnevrov/agentic-repository-engineering-template/rulesets
gh api repos/mnevrov/agentic-repository-engineering-template/rules/branches/main
```

Требуется реальное API-подтверждение действующих правил, не наличие JSON-файла. Если правило уже создано, **не выполнять POST повторно**, сначала проверить текущую конфигурацию.

## 3. Release evidence и решение

- [x] TEMPLATE-15 remediation закрыта, 144 теста в историческом отчёте, source exact-code CI PASS.
- [x] Pilot CLI/Git/telemetry component integration E3 PASS (отдельный GitHub Actions run).
- [ ] Проверено, что ruleset/branch protection реально **active** для `main`, запрет удаления/force-push, PR и три required checks.
- [ ] Есть отдельный независимый финальный release verdict именно по **новому** final SHA (можно документировать risk waiver, но нельзя скрыто превращать self-review в independent review). Если владелец явно принимает waiver — указать в issue #9 вместе с риском и SHA.
- [ ] HOST/LLM acceptance согласно issue #9 либо отдельная обоснованная owner risk acceptance с перечнем НЕ проверенных сценариев. Не переименовывать CI в HOST PASS.
- [ ] На финальном SHA прошли все три CI jobs, включая `doctor` и обе версии OpenCode.
- [ ] Issue #9 обновлён фактическими ссылками и явным решением о релизе.

## 4. Создание подписанного тега и GitHub Release — только после checklist

На доверенной машине с локально настроенным Git signing key:

```bash
git fetch --prune origin
git switch main
git pull --ff-only origin main
FINAL_SHA="$(git rev-parse HEAD)"
# Сравните FINAL_SHA с одобренным exact SHA из issue #9.
# Не продолжать при несовпадении.
git tag -s v0.1.0 -m "Agentic Repository Engineering Template v0.1.0" "$FINAL_SHA"
git tag -v v0.1.0  # обязательна проверка подписи
git push origin refs/tags/v0.1.0
gh release create v0.1.0 --verify-tag \
  --title "Agentic Repository Engineering Template v0.1.0" \
  --notes-file docs/releases/v0.1.0-DRAFT.md
gh release view v0.1.0
```

**Важно:** подписанный тег — отдельный Git-объект. GitHub Release, созданный на голом имени тега без проверки подписи, не заменяет этот gate. `gh release create --verify-tag` требует существования удалённого тега, а не создаёт signed tag.

После успешного выпуска обновить `docs/RELEASE_READINESS.md` новым PR и теговыми ссылками; не переписывать уже выпущенный тег. Сохранить исторический `release/v0.1.0-rc.1` без изменений.
