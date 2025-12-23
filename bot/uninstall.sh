#!/bin/bash

# Скрипт полного удаления
BOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$BOT_DIR")"

RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${RED}⚠️  ВНИМАНИЕ: Это удалит папку $PROJECT_ROOT и все данные!${NC}"
echo -n "Вы уверены? (y/n): "
read confirm

if [ "$confirm" != "y" ]; then
    echo "Отмена."
    exit 0
fi

# 1. Docker clean
cd "$BOT_DIR"
echo -e "${YELLOW}Удаление контейнеров...${NC}"
docker compose down --rmi all --volumes 2>/dev/null

# 2. Удаление алиаса
SHELL_RC=""
[ -f "$HOME/.bashrc" ] && SHELL_RC="$HOME/.bashrc"
[ -f "$HOME/.zshrc" ] && SHELL_RC="$HOME/.zshrc"

if [ ! -z "$SHELL_RC" ]; then
    sed -i '/alias downloader=/d' "$SHELL_RC"
    echo "Алиас удален из $SHELL_RC"
fi

# 3. Удаление файлов
echo -e "${YELLOW}Удаление файлов проекта...${NC}"
rm -rf "$PROJECT_ROOT"

echo -e "${RED}Удаление завершено.${NC}"