#!/bin/bash

# Описание: Скрипт обновления (стратегия temp-swap)
# Запускается из папки установки (например, ~/downloader)

# Определяем текущую директорию
INSTALL_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_URL="https://github.com/furik30/dwnld_bot.git"
BRANCH="main"

# Цвета
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${CYAN}==============================================${NC}"
echo -e "${CYAN}    Telegram Downloader Bot - Обновление      ${NC}"
echo -e "${CYAN}    (Ветка: $BRANCH | Папка: $INSTALL_DIR)    ${NC}"
echo -e "${CYAN}==============================================${NC}"

# 1. Создание временной директории
TEMP_DIR=$(mktemp -d)
echo -e "${YELLOW}Создана временная директория: $TEMP_DIR${NC}"

# 2. Клонирование репозитория
echo -e "${YELLOW}Клонирование репозитория...${NC}"
if git clone -b "$BRANCH" --depth 1 "$REPO_URL" "$TEMP_DIR"; then
    echo -e "${GREEN}Репозиторий успешно клонирован.${NC}"
else
    echo -e "${RED}Ошибка клонирования репозитория!${NC}"
    rm -rf "$TEMP_DIR"
    exit 1
fi

# 3. Синхронизация файлов
echo -e "${YELLOW}Обновление файлов...${NC}"

# Проверка наличия rsync
if ! command -v rsync &> /dev/null; then
    echo -e "${YELLOW}rsync не найден, используем cp (менее надежно)...${NC}"
    # Копируем все, но стараемся не затереть .env если он вдруг есть в репо (маловероятно)
    # Здесь просто копируем с перезаписью
    cp -rf "$TEMP_DIR/bot/"* "$INSTALL_DIR/"
else
    # Используем rsync для копирования
    # -a: архивный режим (сохраняет права, время и т.д.)
    # -v: подробно
    # Исключаем файлы, которые не хотим случайно перезаписать, если они есть в репо
    rsync -av \
        --exclude='.env' \
        --exclude='data/' \
        --exclude='downloads/' \
        --exclude='session/' \
        --exclude='instagram_cookies.txt' \
        "$TEMP_DIR/bot/" "$INSTALL_DIR/"
fi

# 4. Очистка
rm -rf "$TEMP_DIR"
echo -e "${GREEN}Временные файлы удалены.${NC}"

# 5. Пересборка контейнеров
echo -e "${YELLOW}Пересборка и перезапуск контейнеров...${NC}"
cd "$INSTALL_DIR"
# Проверяем, запущен ли docker (на всякий случай)
if docker compose version &> /dev/null; then
    docker compose up -d --build
else
    echo -e "${RED}Ошибка: docker compose не найден или не работает.${NC}"
fi

echo -e "${GREEN}✅ Обновление успешно завершено!${NC}"
