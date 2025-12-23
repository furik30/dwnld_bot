#!/bin/bash

BOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${RED}⚠️ ВНИМАНИЕ: Это полностью удалит бота, все настройки и скачанные файлы!${NC}"
echo -n "Вы уверены? (y/n): "
read confirm

if [ "$confirm" != "y" ]; then
    echo "Удаление отменено."
    exit 0
fi

cd "$BOT_DIR"

echo -e "${YELLOW}Остановка и удаление контейнеров...${NC}"
docker compose down --rmi all --volumes 2>/dev/null

# Удаление alias
SHELL_RC=""
if [ -f "$HOME/.bashrc" ]; then SHELL_RC="$HOME/.bashrc";
elif [ -f "$HOME/.zshrc" ]; then SHELL_RC="$HOME/.zshrc"; fi

if [ ! -z "$SHELL_RC" ]; then
    sed -i '/alias downloader=/d' "$SHELL_RC"
    echo "Alias удален из $SHELL_RC"
fi

echo -e "${YELLOW}Удаление файлов проекта...${NC}"
rm -rf "$BOT_DIR"

echo -e "${RED}Бот успешно удален.${NC}"