# Telegram Downloader Bot

Мощный Telegram-бот для скачивания музыки и видео с YouTube, Instagram (Reels), TikTok и SoundCloud.
Рефакторинг с использованием Pyrogram (для скорости), модульной структуры и Docker.

## Возможности

- 🎵 **Музыка**: Поиск и скачивание с YouTube (MP3).
- 📹 **Видео**: Скачивание с YouTube, TikTok, Instagram Reels.
- 📦 **Плейлисты**: Поддержка плейлистов YouTube и SoundCloud.
- 🚀 **Быстрый**: Построен на Pyrogram (MTProto).
- 🐳 **Docker**: Легкое развертывание через Docker Compose.
- 🛠 **Управление**: Скрипты `install.sh`, `update.sh`, `downloader.sh`.
- 🍪 **Cookies**: Поддержка cookies для Instagram и YouTube (обход ограничений).
- 🔐 **Админ-панель**: Просмотр логов и статуса прямо в Telegram.
- 🔗 **Deep Links**: Ссылки для быстрого скачивания видео.

## Требования

- Docker и Docker Compose
- Git
- Токен Telegram бота (@BotFather)
- Telegram API ID и Hash (https://my.telegram.org)

## Установка (Автоматическая)

1.  **Скачайте и запустите установщик:**

    Если репозиторий еще не склонирован:
    ```bash
    git clone https://github.com/yourusername/dwnld_bot.git
    cd dwnld_bot
    bash install.sh
    ```

    Скрипт проверит наличие Docker, создаст `.env` файл (запросит у вас данные) и запустит бота.

2.  **Cookies (Опционально):**
    Для работы с Instagram и контентом 18+ на YouTube:
    -   Положите файл `instagram_cookies.txt` (формат Netscape) в папку бота.
    -   Положите файл `youtube_cookies.txt` в папку бота.
    -   Перезапустите бота: `./downloader.sh restart`.

## Обновление

Для обновления бота до последней версии используйте скрипт `update.sh`:

```bash
sudo ./update.sh [имя_ветки]
```
По умолчанию обновляется из ветки `main`. Для dev-версии: `sudo ./update.sh dev`.
Скрипт безопасно перенесет ваши данные (`.env`, базу данных, скачанные файлы) в новую версию.

## Управление ботом (`./downloader.sh`)

- `./downloader.sh up` - Запустить
- `./downloader.sh down` - Остановить
- `./downloader.sh restart` - Перезапустить
- `./downloader.sh logs` - Смотреть логи
- `./downloader.sh status` - Статус
- `./downloader.sh edit-env` - Изменить настройки

## Структура проекта

- `main.py`: Точка входа.
- `modules/`: Обработчики бота.
- `utils/`: Утилиты.
- `config/`: Конфиги.
- `data/`: Постоянные данные.
- `downloads/`: Загрузки.

## Лицензия

MIT
