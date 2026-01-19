#!/bin/bash

BOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$BOT_DIR"

# Цвета
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

ENV_FILE=".env"
EXAMPLE_FILE=".env.example"

# Данные для Docker
export USER_ID=$(id -u)
export GROUP_ID=$(id -g)

# --- Функции помощники ---

# Функция проверки и исправления файлов cookies
ensure_cookie_files() {
    local cookie_dir="cookies"
    
    local files=("youtube_cookies.txt" "instagram_cookies.txt" "tiktok_cookies.txt")
    
    for file_name in "${files[@]}"; do
        local file_path="$cookie_dir/$file_name"
        
        if [ -d "$file_path" ]; then
            echo -e "${YELLOW}⚠️  Обнаружена ошибка: '$file_path' является папкой. Исправляем...${NC}"
            rm -rf "$file_path"
            touch "$file_path"
            echo -e "${GREEN}   -> Папка удалена, создан пустой файл '$file_path'.${NC}"
        elif [ ! -f "$file_path" ]; then
            echo -e "${YELLOW}ℹ️  Файл '$file_path' не найден. Создаю пустой...${NC}"
            touch "$file_path"
        fi
    done
}

# Функция для безопасного обновления переменных в .env
set_env_var() {
    local key="$1"
    local value="$2"
    
    if grep -q "^$key=" "$ENV_FILE"; then
        sed "s|^$key=.*|$key=$value|" "$ENV_FILE" > "${ENV_FILE}.tmp" && mv "${ENV_FILE}.tmp" "$ENV_FILE"
    else
        echo "$key=$value" >> "$ENV_FILE"
    fi
}

# Функция интерактивной настройки
setup_env() {
    echo -e "${CYAN}🛠  Настройка конфигурации (.env)${NC}"
    
    if [ ! -f "$ENV_FILE" ]; then
        if [ -f "$EXAMPLE_FILE" ]; then
            cp "$EXAMPLE_FILE" "$ENV_FILE"
            echo -e "${GREEN}Создан чистый файл .env${NC}"
        else
            echo -e "${RED}Ошибка: Не найден .env.example${NC}"
            touch "$ENV_FILE"
        fi
    else
        echo -e "${YELLOW}Файл .env уже существует.${NC}"
        echo -n "Хотите сбросить настройки и начать заново? (y/N): "
        read reset_conf
        if [[ "$reset_conf" =~ ^[Yy]$ ]]; then
            cp "$EXAMPLE_FILE" "$ENV_FILE"
            echo -e "${GREEN}Конфигурация сброшена.${NC}"
        fi
    fi

    source "$ENV_FILE" 2>/dev/null
    echo -e "\nВведите данные (нажмите Enter, чтобы оставить текущее значение):"

    current_token="${TELEGRAM_TOKEN:-}"
    echo -n "Telegram Bot Token [${current_token:0:10}...]: "
    read input_token
    [ ! -z "$input_token" ] && set_env_var "TELEGRAM_TOKEN" "$input_token"

    current_api_id="${API_ID:-}"
    echo -n "API ID (my.telegram.org) [$current_api_id]: "
    read input_api_id
    [ ! -z "$input_api_id" ] && set_env_var "API_ID" "$input_api_id"

    current_api_hash="${API_HASH:-}"
    echo -n "API HASH [$current_api_hash]: "
    read input_api_hash
    [ ! -z "$input_api_hash" ] && set_env_var "API_HASH" "$input_api_hash"

    current_owner="${OWNER_ID:-}"
    echo -n "Ваш Telegram User ID [$current_owner]: "
    read input_owner
    [ ! -z "$input_owner" ] && set_env_var "OWNER_ID" "$input_owner"

    echo -e "${GREEN}✅ Настройка завершена!${NC}"
}

check_env() {
    if [ ! -f "$ENV_FILE" ]; then
        echo -e "${RED}Файл .env не найден!${NC}"
        echo -e "Запустите: ${CYAN}downloader setup${NC}"
        exit 1
    fi
    if grep -q "TELEGRAM_TOKEN=$" "$ENV_FILE" || grep -q "API_ID=$" "$ENV_FILE"; then
        echo -e "${YELLOW}Внимание: Некоторые переменные в .env не заполнены.${NC}"
        echo -n "Продолжить запуск? (y/n): "
        read cont
        if [ "$cont" != "y" ]; then exit 1; fi
    fi
}

usage() {
    echo -e "${CYAN}Downloader CLI. Использование: downloader [команда]${NC}"
    echo "  setup     - Интерактивная настройка (.env)"
    echo "  up        - Собрать и запустить бота"
    echo "  down      - Остановить"
    echo "  restart   - Перезагрузить"
    echo "  logs      - Просмотр логов (-f)"
    echo "  update    - Обновить код из ветки dev"
    echo "  edit      - Вручную редактировать .env"
    echo "  uninstall - Полное удаление проекта"
}

# --- Основная логика ---

case "$1" in
    setup)
        setup_env
        ;;
    up)
        check_env
        ensure_cookie_files
        docker compose up -d --build
        echo -e "${GREEN}Бот запущен.${NC}"
        ;;
    down)
        docker compose down
        echo -e "${YELLOW}Бот остановлен.${NC}"
        ;;
    restart)
        check_env
        ensure_cookie_files
        docker compose restart
        ;;
    logs)
        docker compose logs -f --tail=100
        ;;
    update)
        bash update.sh
        ;;
    edit)
        ${EDITOR:-nano} .env
        ;;
    uninstall)
        bash uninstall.sh
        ;;
    *)
        usage
        ;;
esac