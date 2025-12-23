#!/bin/bash

# Цветовые коды
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

REPO_URL="https://github.com/furik30/dwnld_bot.git"
INSTALL_DIR="$HOME/dwnld_bot"
BOT_DIR="$INSTALL_DIR/bot"

echo -e "${CYAN}==============================================${NC}"
echo -e "${CYAN}    Telegram Downloader Bot - Установщик      ${NC}"
echo -e "${CYAN}==============================================${NC}"

# 1. Проверки окружения
if ! command -v git &> /dev/null; then
    echo -e "${RED}Ошибка: git не установлен.${NC}"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}Docker не найден. Устанавливаю...${NC}"
    curl -fsSL https://get.docker.com | sh
fi

# 2. Клонирование или переход в папку
if [ -d "$INSTALL_DIR/.git" ]; then
    echo -e "${GREEN}Проект уже склонирован в $INSTALL_DIR. Обновляем...${NC}"
    cd "$INSTALL_DIR" && git pull
else
    echo -e "${YELLOW}Клонирование репозитория в $INSTALL_DIR...${NC}"
    git clone "$REPO_URL" "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

# 3. Настройка .env внутри папки bot/
echo -e "\n${CYAN}--- Настройка параметров .env ---${NC}"
if [ ! -f "$BOT_DIR/.env" ]; then
    if [ -f "$BOT_DIR/.env.example" ]; then
        cp "$BOT_DIR/.env.example" "$BOT_DIR/.env"
    else
        touch "$BOT_DIR/.env"
    fi
fi

read_val() {
    local var=$1
    local msg=$2
    local current=$(grep "^$var=" "$BOT_DIR/.env" | cut -d'=' -f2-)
    
    if [ -z "$current" ]; then
        echo -n -e "${YELLOW}$msg: ${NC}"
        read input
        if [ ! -z "$input" ]; then
            # Используем | как разделитель в sed, так как токены могут содержать /
            if grep -q "^$var=" "$BOT_DIR/.env"; then
                sed -i "s|^$var=.*|$var=$input|" "$BOT_DIR/.env"
            else
                echo "$var=$input" >> "$BOT_DIR/.env"
            fi
        fi
    fi
}

read_val "TELEGRAM_TOKEN" "Введите токен бота (@BotFather)"
read_val "API_ID" "Введите API ID (my.telegram.org)"
read_val "API_HASH" "Введите API HASH (my.telegram.org)"
read_val "OWNER_ID" "Введите ваш Telegram User ID (для админки)"

# 4. Настройка Alias (теперь путь включает /bot/)
echo -e "\n${CYAN}--- Настройка быстрого доступа (alias) ---${NC}"
SHELL_RC=""
if [ -f "$HOME/.bashrc" ]; then SHELL_RC="$HOME/.bashrc";
elif [ -f "$HOME/.zshrc" ]; then SHELL_RC="$HOME/.zshrc"; fi

if [ ! -z "$SHELL_RC" ]; then
    if ! grep -q "alias downloader=" "$SHELL_RC"; then
        echo "alias downloader='bash $BOT_DIR/downloader.sh'" >> "$SHELL_RC"
        echo -e "${GREEN}Alias 'downloader' добавлен в $SHELL_RC${NC}"
        echo -e "${YELLOW}Чтобы алиас заработал прямо сейчас, выполните: source $SHELL_RC${NC}"
    fi
fi

# 5. Права доступа на скрипты в папке bot/
chmod +x "$BOT_DIR/downloader.sh" "$BOT_DIR/update.sh" "$BOT_DIR/uninstall.sh" 2>/dev/null || true

echo -e "\n${GREEN}Установка завершена!${NC}"
echo -e "Теперь вы можете управлять ботом командой: ${CYAN}downloader up${NC}"