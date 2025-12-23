# Telegram Downloader Bot

Мощный Telegram-бот для скачивания музыки и видео с YouTube, Instagram (Reels), TikTok и SoundCloud.
Рефакторинг с использованием Pyrogram (для скорости), модульной структуры и Docker.

## Возможности

- 🎵 **Музыка**: Поиск и скачивание с YouTube (MP3).
- 📹 **Видео**: Скачивание с YouTube, TikTok, Instagram Reels.
- 📦 **Плейлисты**: Поддержка плейлистов YouTube и SoundCloud.
- 🚀 **Быстрый**: Построен на Pyrogram (MTProto).
- 🐳 **Docker**: Легкое развертывание через Docker Compose.
- 🛠 **CLI**: Скрипт `downloader.sh` для управления.
- 🍪 **Cookies**: Поддержка cookies для Instagram и YouTube (обход ограничений).
- 🔐 **Админ-панель**: Просмотр логов и статуса прямо в Telegram.
- 🔗 **Deep Links**: Ссылки для быстрого скачивания видео.

## Требования

- Docker и Docker Compose
- Токен Telegram бота (@BotFather)
- Telegram API ID и Hash (https://my.telegram.org)

## Установка

1.  **Клонирование репозитория:**
    ```bash
    git clone https://github.com/yourusername/dwnld_bot.git
    cd dwnld_bot
    ```

2.  **Настройка:**
    -   Скопируйте `.env.example` в `.env` (или скрипт сделает это за вас).
    -   Отредактируйте `.env`, указав ваши данные.
    ```bash
    ./downloader.sh edit-env
    ```

3.  **Cookies (Опционально, но рекомендуется):**
    -   **Instagram**: Экспортируйте cookies в формате Netscape (используя расширения типа "Get cookies.txt LOCALLY") и сохраните как `instagram_cookies.txt` в корневой папке.
    -   **YouTube**: Аналогично сохраните `youtube_cookies.txt` в корневой папке для обхода возрастных ограничений.

4.  **Запуск бота:**
    ```bash
    ./downloader.sh up
    ```

## Использование

- **/start**: Запустить бота.
- **Поиск**: Отправьте любой текст для поиска песни.
- **Ссылки**: Отправьте ссылку с поддерживаемой платформы (YouTube, Instagram, TikTok, SoundCloud).
- **Inline**: Напишите `@UsernameБота запрос` в любом чате.

### Команды администратора

- **/admin** или **/logs**: Открыть админ-панель (только для `OWNER_ID`).
    -   **Логи**: Показать последние 20 строк логов.
    -   **Статус**: Показать использование памяти и активные потоки.
    -   **Ошибки**: Показать только логи с ошибками.

## CLI Команды (`./downloader.sh`)

- `up`: Запустить бота в фоновом режиме.
- `down`: Остановить бота.
- `logs [n]`: Просмотр логов (по умолчанию 100 строк).
- `restart`: Перезагрузить бота.
- `update`: Получить обновления из git и пересобрать.
- `status`: Проверить статус контейнера.

## Структура проекта

- `main.py`: Точка входа.
- `modules/`: Обработчики бота (youtube, instagram, admin).
- `utils/`: Вспомогательные функции (logger, storage, messages).
- `config/`: Конфигурационные файлы (messages.yml).
- `data/`: Постоянные данные (deep links, сессии).
- `downloads/`: Папка для временных загрузок.

## Лицензия

MIT
