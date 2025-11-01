# Настройка Instagram Cookies

Для скачивания Instagram Reels необходимо настроить cookies.

## Способ 1: Экспорт cookies из браузера

1. Откройте приватное/инкогнито окно браузера
2. Войдите в Instagram аккаунт
3. Экспортируйте cookies для домена `instagram.com`
4. Сохраните в файл `instagram_cookies.txt` в папке `dwnld_bot/`

## Способ 2: Использование расширения браузера

### Chrome/Firefox:
1. Установите расширение "Cookie Editor" или "EditThisCookie"
2. Откройте Instagram в приватном режиме
3. Войдите в аккаунт
4. Экспортируйте cookies в формате Netscape
5. Сохраните как `instagram_cookies.txt`

## Необходимые cookies

Для работы нужны следующие cookies:
- `csrftoken`
- `sessionid` 
- `ds_user_id`

## Формат файла cookies

Файл должен быть в формате Netscape:
```
# Netscape HTTP Cookie File
.instagram.com	TRUE	/	TRUE	1735689600	csrftoken	YOUR_CSRF_TOKEN_HERE
.instagram.com	TRUE	/	TRUE	1735689600	sessionid	YOUR_SESSION_ID_HERE
.instagram.com	TRUE	/	TRUE	1735689600	ds_user_id	YOUR_USER_ID_HERE
```

## Проверка работы

После создания файла cookies перезапустите сервис:
```bash
systemctl restart downloader-bot.service
```

## Важно

- Используйте только приватное окно для экспорта cookies
- Закройте приватное окно после экспорта
- Не используйте основной аккаунт для избежания блокировки
- Cookies нужно обновлять периодически
- Для публичных Reels cookies могут не требоваться 