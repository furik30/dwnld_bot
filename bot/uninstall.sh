#!/bin/bash

# Скрипт полного удаления
# Определяем директорию установки (теперь это и есть корень бота)
INSTALL_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${RED}⚠️  ВНИМАНИЕ: Это удалит папку $INSTALL_DIR и все данные!${NC}"
echo -n "Вы уверены? (y/n): "
read confirm

if [ "$confirm" != "y" ]; then
    echo "Отмена."
    exit 0
fi

# 1. Остановка и удаление контейнеров
cd "$INSTALL_DIR"
echo -e "${YELLOW}Удаление контейнеров...${NC}"
# Проверяем наличие docker compose перед вызовом
if command -v docker &> /dev/null; then
    docker compose down --rmi all --volumes 2>/dev/null
fi

# 2. Удаление алиаса
SHELL_RC=""
[ -f "$HOME/.bashrc" ] && SHELL_RC="$HOME/.bashrc"
[ -f "$HOME/.zshrc" ] && SHELL_RC="$HOME/.zshrc"

if [ ! -z "$SHELL_RC" ]; then
    if grep -q "alias downloader=" "$SHELL_RC"; then
        sed -i '/alias downloader=/d' "$SHELL_RC"
        echo "Алиас удален из $SHELL_RC"
    fi
fi

# 3. Удаление файлов
# Важно: переходим на уровень выше, чтобы удалить папку
cd ..
echo -e "${YELLOW}Удаление файлов проекта ($INSTALL_DIR)...${NC}"
rm -rf "$INSTALL_DIR"

echo -e "${RED}Удаление завершено.${NC}"
