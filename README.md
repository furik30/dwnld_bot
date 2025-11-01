[EN](READMEs/README_en.md)

# Telegram Downloader Bot

Это Telegram-бот, который позволяет загружать музыку и видео с различных платформ, таких как YouTube, TikTok, Instagram Reels и SoundCloud.

## Функции

- Поиск и загрузка музыки с YouTube.
- Загрузка видео с TikTok, Instagram Reels и YouTube.
- Загрузка плейлистов с YouTube и SoundCloud.
- Инлайновый режим для быстрого поиска и загрузки.

## Установка

1.  **Клонируйте репозиторий:**
    ```bash
    git clone https://github.com/furik30/dwnld_bot
    ```

2.  **Запустите установщик:**
    Это создаст виртуальное окружение, установит зависимости и создаст файл `.env` для вас.
    ```bash
    bash install.sh
    ```

3.  **Конфигурация:**
    -   Откройте вновь созданный файл `.env`.
    -   Заполните ваш `TELEGRAM_TOKEN` от BotFather.
    -   При желании установите `OWNER_USERNAME` и `INSTAGRAM_USERNAME`.

4.  **Запуск бота:**
    ```bash
    source venv/bin/activate
    python dwnld_bot/dwnld_bot.py
    ```

## Файлы куки

-   `youtube_cookies.txt`: Используется `yt-dlp` для обхода возрастных ограничений и других ограничений на YouTube.
-   `instagram_cookies.txt`: Требуется для загрузки Instagram Reels. Подробности см. в [READMEs/README_INSTAGRAM.md](READMEs/README_INSTAGRAM.md).
## Лицензия

Этот проект распространяется под лицензией MIT [LICENSE](LICENSE).
