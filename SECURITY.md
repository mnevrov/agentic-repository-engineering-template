# Security

## Для разработчиков и AI-агентов

- Не коммитьте ключи, токены, пароли, cookies и реальные credential-файлы.
- Не вставляйте production secrets в prompts и telemetry.
- Любые изменения authentication/authorization относятся к риску C.
- Destructive operations должны требовать явного подтверждения и иметь безопасный режим проверки.
- Security finding не скрывается ради завершения задачи; он фиксируется в review/TODO.

## Сообщение об уязвимости

Не публикуйте credential, exploit details или другие чувствительные данные в обычном GitHub Issue.

Если на странице repository доступен **Security → Report a vulnerability**, используйте private vulnerability report / GitHub Security Advisory. Если private reporting недоступен, сначала свяжитесь с владельцем repository через его GitHub profile и согласуйте приватный канал передачи деталей.

Обычные несекретные вопросы по security contract можно обсуждать через GitHub Issues.
