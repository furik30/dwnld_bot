#!/bin/bash

# Цвета
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# Настройки
REPO_URL="https://github.com/furik30/dwnld_bot.git"
BRANCH="dev"
INSTALL_DIR="$HOME/downloader"
BOT_DIR="$INSTALL_DIR/bot"

echo -e "${CYAN}=== Telegram Downloader Bot Installer ===${NC}"

# 1. Проверка зависимостей
echo -e "${YELLOW}Проверка зависимостей...${NC}"
if ! command -v git &> /dev/null; then
    echo -e "${RED}Git не найден. Установите git.${NC}"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}Docker не найден. Устанавливаю...${NC}"
    curl -fsSL https://get.docker.com | sh
fi

# 2. Скачивание (Sparse checkout)
if [ -d "$INSTALL_DIR/.git" ]; then
    echo -e "${GREEN}Обновление репозитория...${NC}"
    cd "$INSTALL_DIR"
    git fetch origin "$BRANCH"
    git checkout "$BRANCH"
    git pull origin "$BRANCH"
else
    echo -e "${GREEN}Клонирование репозитория...${NC}"
    git clone -b "$BRANCH" --no-checkout "$REPO_URL" "$INSTALL_DIR"
    cd "$INSTALL_DIR"
    git sparse-checkout init --cone
    git sparse-checkout set bot
    git checkout "$BRANCH"
fi

# 3. Права на исполнение
chmod +x "$BOT_DIR/downloader.sh" "$BOT_DIR/update.sh" "$BOT_DIR/uninstall.sh" 2>/dev/null

# 4. Настройка алиаса
SHELL_RC=""
[ -f "$HOME/.bashrc" ] && SHELL_RC="$HOME/.bashrc"
[ -f "$HOME/.zshrc" ] && SHELL_RC="$HOME/.zshrc"

if [ ! -z "$SHELL_RC" ]; then
    if ! grep -q "alias downloader=" "$SHELL_RC"; then
        echo "" >> "$SHELL_RC"
        echo "# Alias for Downloader Bot" >> "$SHELL_RC"
        echo "alias downloader='bash $BOT_DIR/downloader.sh'" >> "$SHELL_RC"
        echo -e "${GREEN}Алиас 'downloader' добавлен в $SHELL_RC${NC}"
    fi
fi

echo -e "\n${GREEN}✅ Установка завершена!${NC}"
echo -e "Для настройки и запуска выполните следующие команды:"
echo -e "  1. ${CYAN}source $SHELL_RC${NC} (или перезайдите в терминал)"
echo -e "  2. ${CYAN}downloader setup${NC} (для настройки токенов)"
echo -e "  3. ${CYAN}downloader up${NC}    (для запуска)"