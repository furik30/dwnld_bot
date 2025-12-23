#!/bin/bash

# Скрипт безопасного обновления Downloader Bot (Docker версия)
set -e

# Определение директорий
# Если скрипт запущен из папки проекта, используем её как BOT_DIR.
# Иначе предполагаем текущую директорию.
BOT_DIR=$(pwd)
TEMP_DIR="/tmp/dwnld_bot-update-$(date +%s)"
REPO_URL="https://github.com/furik30/dwnld_bot.git"
BRANCH=${1:-main}  # По умолчанию ветка main, можно передать аргументом (например, dev)

# Цвета
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}🔄 Запущено обновление Downloader Bot из ветки '$BRANCH'...${NC}"

# Проверка, находимся ли мы в правильной папке (наличие docker-compose.yml)
if [ ! -f "$BOT_DIR/docker-compose.yml" ]; then
    echo -e "${RED}❌ Ошибка: docker-compose.yml не найден. Запускайте скрипт из папки бота.${NC}"
    exit 1
fi

# 1. Клонирование новой версии
echo -e "${YELLOW}🔄 Клонирование ветки '$BRANCH' во временную директорию...${NC}"
git clone --depth 1 --branch "$BRANCH" "$REPO_URL" "$TEMP_DIR"
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Не удалось склонировать репозиторий. Проверьте URL и название ветки.${NC}"
    rm -rf "$TEMP_DIR"
    exit 1
fi

# 2. Остановка текущего бота
echo -e "${YELLOW}⏹️  Остановка контейнеров...${NC}"
./downloader.sh down

# 3. Перенос данных
echo -e "${YELLOW}📦 Перенос данных и конфигурации...${NC}"

# Функция безопасного копирования
safe_copy() {
    local src="$1"
    local dest="$2"
    if [ -e "$src" ]; then
        echo "   Копирование $src..."
        cp -r "$src" "$dest"
    fi
}

# Копируем .env
safe_copy "$BOT_DIR/.env" "$TEMP_DIR/.env"

# Копируем папки с данными (volumes)
# ВАЖНО: Мы переносим данные в temp, чтобы потом заменить папку BOT_DIR целиком.
# Это гарантирует, что старый код будет удален, но данные останутся.
safe_copy "$BOT_DIR/data" "$TEMP_DIR/"
safe_copy "$BOT_DIR/downloads" "$TEMP_DIR/"
safe_copy "$BOT_DIR/logs" "$TEMP_DIR/"

# Копируем cookies
safe_copy "$BOT_DIR/instagram_cookies.txt" "$TEMP_DIR/"
safe_copy "$BOT_DIR/youtube_cookies.txt" "$TEMP_DIR/"

# Опционально: messages.yml, если пользователь его менял и хочет сохранить?
# Обычно конфиг сообщений обновляется из репо. Если нужно сохранять пользовательские правки, раскомментируйте:
# safe_copy "$BOT_DIR/config/messages.yml" "$TEMP_DIR/config/"

# 4. Замена директории
echo -e "${YELLOW}📁 Замена старой версии на новую...${NC}"

# Мы не можем удалить текущую директорию, находясь в ней и выполняя скрипт из нее.
# Поэтому мы поступим хитрее:
# 1. Скрипт должен скопировать себя во временную папку и перезапуститься оттуда? Слишком сложно.
# 2. Просто удалить все файлы КРОМЕ скрипта обновления?
# 3. RSYNC! Лучший способ обновить файлы без удаления папки.

echo -e "${GREEN}Использую rsync для обновления файлов...${NC}"
if ! command -v rsync &> /dev/null; then
    echo -e "${YELLOW}rsync не найден, устанавливаю (требует apt)...${NC}"
    apt-get update && apt-get install -y rsync
fi

# Синхронизируем файлы из TEMP_DIR в BOT_DIR
# --exclude=.git сохраняет git историю текущей папки, если она была (хотя мы клонировали новый репо, там своя история)
# Но мы обновляем "через замену", поэтому лучше сделать как в примере пользователя: полная замена.
# Но проблема: если я удалю папку, скрипт update.sh (который внутри) тоже удалится и выполнение прервется.

# Решение: Копируем файлы из TEMP_DIR поверх текущих.
# Это оставит "мусорные" старые файлы, которых нет в новой версии.
# Чтобы убрать мусор, можно сначала удалить всё, кроме `update.sh`, `install.sh`, `downloader.sh` (чтобы они доработали) и данных.
# Но данные мы уже скопировали в TEMP.

# Давайте сделаем move approach, но аккуратно.
# Мы переместимся на уровень выше.
PARENT_DIR=$(dirname "$BOT_DIR")
BASENAME=$(basename "$BOT_DIR")

# Переходим выше
cd "$PARENT_DIR"

# Переименовываем текущую папку в backup
BACKUP_DIR="${BOT_DIR}_backup_$(date +%s)"
mv "$BOT_DIR" "$BACKUP_DIR"

# Перемещаем TEMP_DIR на место BOT_DIR
mv "$TEMP_DIR" "$BOT_DIR"

# Восстанавливаем права на скрипты
chmod +x "$BOT_DIR/downloader.sh"
chmod +x "$BOT_DIR/install.sh"
chmod +x "$BOT_DIR/update.sh"

echo -e "${GREEN}✅ Файлы обновлены.${NC}"

# 5. Запуск
echo -e "${YELLOW}🚀 Сборка и запуск контейнеров...${NC}"
cd "$BOT_DIR"
./downloader.sh up

# 6. Очистка бэкапа (опционально, пока оставим или удалим?)
echo -e "${YELLOW}🗑 Удаление бэкапа старой версии...${NC}"
rm -rf "$BACKUP_DIR"

echo -e "${GREEN}✅ Обновление завершено успешно!${NC}"
