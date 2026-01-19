# Telegram Downloader Bot 🚀
Мощный Telegram-бот на базе Pyrogram для скачивания медиаконтента с YouTube, Instagram, TikTok и SoundCloud. Полностью автоматизирован через Docker.
## ⚡ Быстрая установка
Просто вставьте эту команду в терминал вашего сервера:
```
curl -sSL https://raw.githubusercontent.com/furik30/dwnld_bot/dev/install.sh | bash
```
## 🛠 Управление (CLI)
После установки вам доступна команда `downloader` из любой директории:
- `downloader up` — запустить бота в фоне.
- `downloader down` — остановить бота.
- `downloader restart` — перезагрузить.
- `downloader logs` — просмотр логов в реальном времени.
- `downloader update` — обновить бота до последней версии.
- `downloader edit` — быстрое редактирование настроек `.env`.
- `downloader uninstall` — полное удаление бота и всех данных.
## 📋 Требования
- **Docker** и **Docker Compose** (скрипт проверит наличие).
- **Telegram API ID/Hash**: получите на [my.telegram.org](https://my.telegram.org).
- **Bot Token**: получите у [@BotFather](https://t.me/BotFather).
## 🍪 Cookies (Опционально)
Для обхода ограничений YouTube (18+) и скачивания из Instagram:
1. Положите файлы `youtube_cookies.txt`, `instagram_cookies.txt` и `tiktok_cookies.txt` в формате Netscape в папку /downloader/bot/cookies/.
2. Выполните `downloader restart`.

Разработано для удобного деплоя на VPS.