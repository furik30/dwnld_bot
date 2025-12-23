#!/bin/bash

# Цветовые коды
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# Настройки репозитория
REPO_URL="https://github.com/furik30/dwnld_bot.git"
BRANCH="dev"
INSTALL_DIR="$HOME/downloader"
BOT_DIR="$INSTALL_DIR/bot"

echo -e "${CYAN}==============================================${NC}"
echo -e "${CYAN}    Telegram Downloader Bot - Установщик      ${NC}"
echo -e "${CYAN}    (Ветка: $BRANCH | Папка: $INSTALL_DIR)    ${NC}"
echo -e "${CYAN}==============================================${NC}"

# 1. Проверки зависимостей
if ! command -v git &> /dev/null; then
    echo -e "${RED}Ошибка: git не установлен.${NC}"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}Docker не найден. Устанавливаю...${NC}"
    curl -fsSL https://get.docker.com | sh
fi

# 2. Умное клонирование (Sparse Checkout)
if [ -d "$INSTALL_DIR/.git" ]; then
    echo -e "${GREEN}Проект уже существует. Обновляем...${NC}"
    cd "$INSTALL_DIR"
    git fetch origin "$BRANCH"
    git checkout "$BRANCH"
    git pull origin "$BRANCH"
else
    echo -e "${YELLOW}Клонирование папки bot из ветки $BRANCH...${NC}"
    # Клонируем без скачивания файлов
    git clone -b "$BRANCH" --no-checkout "$REPO_URL" "$INSTALL_DIR"
    cd "$INSTALL_DIR"
    # Настраиваем получение только папки bot
    git sparse-checkout init --cone
    git sparse-checkout set bot
    git checkout "$BRANCH"
fi

# 3. Настройка .env
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
            if grep -q "^$var=" "$BOT_DIR/.env"; then
                sed -i "s|^$var=.*|$var=$input|" "$BOT_DIR/.env"
            else
                echo "$var=$input" >> "$BOT_DIR/.env"
            fi
        fi
    fi
}

read_val "TELEGRAM_TOKEN" "Введите токен бота (@BotFather)"
read_val "API_ID" "Введите API ID"
read_val "API_HASH" "Введите API HASH"
read_val "OWNER_ID" "Введите ваш Telegram User ID"

# 4. Создание алиаса
echo -e "\n${CYAN}--- Настройка алиаса 'downloader' ---${NC}"
SHELL_RC=""
[ -f "$HOME/.bashrc" ] && SHELL_RC="$HOME/.bashrc"
[ -f "$HOME/.zshrc" ] && SHELL_RC="$HOME/.zshrc"

if [ ! -z "$SHELL_RC" ]; then
    if ! grep -q "alias downloader=" "$SHELL_RC"; then
        echo "alias downloader='bash $BOT_DIR/downloader.sh'" >> "$SHELL_RC"
        echo -e "${GREEN}Алиас добавлен в $SHELL_RC${NC}"
        echo -e "${YELLOW}Для активации выполните: source $SHELL_RC${NC}"
    fi
fi

# 5. Права на запуск
chmod +x "$BOT_DIR/downloader.sh" "$BOT_DIR/update.sh" "$BOT_DIR/uninstall.sh" 2>/dev/null || true

echo -e "\n${GREEN}Установка завершена!${NC}"
echo -e "Запустите бота командой: ${CYAN}downloader up${NC}"