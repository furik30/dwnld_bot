#!/bin/bash

# Цветовые коды
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# Настройки
REPO_URL="https://github.com/furik30/dwnld_bot.git"
BRANCH="dev"
INSTALL_DIR="$HOME/downloader"

echo -e "${CYAN}==============================================${NC}"
echo -e "${CYAN}    Telegram Downloader Bot - Установщик      ${NC}"
echo -e "${CYAN}    (Ветка: $BRANCH | Папка: $INSTALL_DIR)    ${NC}"
echo -e "${CYAN}==============================================${NC}"

# Определяем необходимость sudo
if [ "$EUID" -ne 0 ]; then
  SUDO="sudo"
else
  SUDO=""
fi

# 1. Проверки зависимостей
echo -e "${YELLOW}Проверка зависимостей...${NC}"

if ! command -v git &> /dev/null; then
    echo -e "${RED}Ошибка: git не установлен.${NC}"
    echo -e "Установите git вручную и повторите попытку."
    exit 1
fi

if ! command -v rsync &> /dev/null; then
    echo -e "${YELLOW}rsync не найден. Пробую установить...${NC}"
    if command -v apt-get &> /dev/null; then
        $SUDO apt-get update && $SUDO apt-get install -y rsync
    elif command -v apk &> /dev/null; then
        $SUDO apk add rsync
    elif command -v yum &> /dev/null; then
        $SUDO yum install -y rsync
    else
        echo -e "${RED}Не удалось установить rsync автоматически. Пожалуйста, установите его вручную.${NC}"
        exit 1
    fi
fi

if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}Docker не найден. Устанавливаю...${NC}"
    curl -fsSL https://get.docker.com | sh
fi

# 2. Подготовка временной папки и клонирование
TEMP_DIR=$(mktemp -d)
echo -e "${YELLOW}Клонирование репозитория во временную папку...${NC}"
if git clone -b "$BRANCH" --depth 1 "$REPO_URL" "$TEMP_DIR"; then
    echo -e "${GREEN}Репозиторий клонирован.${NC}"
else
    echo -e "${RED}Ошибка клонирования!${NC}"
    rm -rf "$TEMP_DIR"
    exit 1
fi

# 3. Копирование файлов в целевую директорию
echo -e "${YELLOW}Установка файлов в $INSTALL_DIR...${NC}"
mkdir -p "$INSTALL_DIR"

# Используем rsync для копирования содержимого bot/ в корень установки
rsync -av \
    --exclude='.env' \
    --exclude='data/' \
    --exclude='downloads/' \
    --exclude='session/' \
    --exclude='instagram_cookies.txt' \
    "$TEMP_DIR/bot/" "$INSTALL_DIR/"

# Проверяем старую структуру
if [ -d "$INSTALL_DIR/bot" ]; then
    echo -e "${YELLOW}Внимание: Обнаружена папка 'bot' внутри установочной директории.${NC}"
    echo -e "${YELLOW}Если это остатки старой установки, вы можете удалить её вручную: rm -rf $INSTALL_DIR/bot${NC}"
fi

# 4. Настройка .env
echo -e "\n${CYAN}--- Настройка параметров .env ---${NC}"
cd "$INSTALL_DIR"

if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp ".env.example" ".env"
    else
        touch ".env"
    fi
fi

# Функция для интерактивного ввода
read_val() {
    local var=$1
    local msg=$2
    local current=$(grep "^$var=" ".env" | cut -d'=' -f2-)
    
    if [ -z "$current" ]; then
        echo -n -e "${YELLOW}$msg: ${NC}"
        read input
        if [ ! -z "$input" ]; then
            if grep -q "^$var=" ".env"; then
                sed -i "s|^$var=.*|$var=$input|" ".env"
            else
                echo "$var=$input" >> ".env"
            fi
        fi
    fi
}

read_val "TELEGRAM_TOKEN" "Введите токен бота (@BotFather)"
read_val "API_ID" "Введите API ID"
read_val "API_HASH" "Введите API HASH"
read_val "OWNER_ID" "Введите ваш Telegram User ID"

# 5. Настройка алиаса
echo -e "\n${CYAN}--- Настройка алиаса 'downloader' ---${NC}"
SHELL_RC=""
[ -f "$HOME/.bashrc" ] && SHELL_RC="$HOME/.bashrc"
[ -f "$HOME/.zshrc" ] && SHELL_RC="$HOME/.zshrc"

if [ ! -z "$SHELL_RC" ]; then
    if grep -q "alias downloader=" "$SHELL_RC"; then
        # Проверяем, не ведет ли алиас на старый путь (содержащий /bot/)
        if grep -q "/bot/downloader.sh" "$SHELL_RC"; then
            echo -e "${YELLOW}Обнаружен устаревший алиас. Обновляем...${NC}"
            sed -i "s|alias downloader=.*|alias downloader='bash $INSTALL_DIR/downloader.sh'|" "$SHELL_RC"
            echo -e "${GREEN}Алиас обновлен в $SHELL_RC${NC}"
            echo -e "${YELLOW}Для активации выполните: source $SHELL_RC${NC}"
        else
            echo -e "${GREEN}Алиас уже настроен корректно.${NC}"
        fi
    else
        echo "alias downloader='bash $INSTALL_DIR/downloader.sh'" >> "$SHELL_RC"
        echo -e "${GREEN}Алиас добавлен в $SHELL_RC${NC}"
        echo -e "${YELLOW}Для активации выполните: source $SHELL_RC${NC}"
    fi
fi

# 6. Права на запуск
chmod +x "$INSTALL_DIR/downloader.sh" "$INSTALL_DIR/update.sh" "$INSTALL_DIR/uninstall.sh" 2>/dev/null || true

# 7. Очистка
rm -rf "$TEMP_DIR"
echo -e "${GREEN}Временные файлы удалены.${NC}"

echo -e "\n${GREEN}Установка завершена!${NC}"
echo -e "Запустите бота командой: ${CYAN}downloader up${NC}"
