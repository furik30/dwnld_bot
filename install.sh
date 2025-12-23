#!/bin/bash

# Цветовые коды
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

REPO_URL="https://github.com/furik30/dwnld_bot.git"
INSTALL_DIR="dwnld_bot"

echo -e "${CYAN}--- Установщик Telegram Downloader Bot ---${NC}"

# Проверка наличия Git
if ! command -v git &> /dev/null; then
    echo -e "${RED}Ошибка: git не установлен. Пожалуйста, установите git.${NC}"
    exit 1
fi

# Проверка наличия Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Ошибка: docker не установлен. Пожалуйста, установите docker.${NC}"
    echo -e "${YELLOW}Подсказка: curl -fsSL https://get.docker.com | sh${NC}"
    exit 1
fi

# Определение режима работы: клон или локальная настройка
if [ -f "downloader.sh" ] && [ -f "docker-compose.yml" ]; then
    echo -e "${GREEN}Обнаружены файлы проекта. Запускаю настройку в текущей директории...${NC}"
else
    echo -e "${YELLOW}Файлы проекта не найдены. Клонирую репозиторий...${NC}"
    if [ -d "$INSTALL_DIR" ]; then
        echo -e "${RED}Директория $INSTALL_DIR уже существует. Пожалуйста, удалите её или перейдите в неё.${NC}"
        exit 1
    fi
    git clone "$REPO_URL" "$INSTALL_DIR"
    cd "$INSTALL_DIR" || exit 1
fi

# Настройка .env
echo -e "\n${CYAN}--- Настройка конфигурации ---${NC}"
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        cp .env.example .env
        echo -e "${GREEN}Файл .env создан из шаблона.${NC}"
    else
        echo -e "${RED}Ошибка: .env.example не найден!${NC}"
        touch .env
    fi
else
    echo -e "${YELLOW}Файл .env уже существует. Пропускаем создание.${NC}"
fi

# Интерактивный ввод данных, если значения пусты
read_var() {
    local var_name=$1
    local prompt=$2
    local current_val=$(grep "^${var_name}=" .env | cut -d'=' -f2-)

    # Если значение пустое или отсутствует
    if [ -z "$current_val" ]; then
        read -p "$prompt: " input_val
        if [ ! -z "$input_val" ]; then
            # Экранируем спецсимволы для sed
            # Простое добавление или замена
            if grep -q "^${var_name}=" .env; then
                sed -i "s|^${var_name}=.*|${var_name}=${input_val}|" .env
            else
                echo "${var_name}=${input_val}" >> .env
            fi
        fi
    fi
}

echo -e "${YELLOW}Проверка переменных окружения... (Нажмите Enter, чтобы пропустить, если уже заполнено)${NC}"
read_var "TELEGRAM_TOKEN" "Введите Telegram Bot Token"
read_var "API_ID" "Введите API ID (my.telegram.org)"
read_var "API_HASH" "Введите API HASH (my.telegram.org)"
read_var "OWNER_ID" "Введите ваш Telegram User ID (для админки)"

# Проверка прав на выполнение скриптов
chmod +x downloader.sh
chmod +x install.sh
if [ -f update.sh ]; then chmod +x update.sh; fi

echo -e "\n${GREEN}Настройка завершена!${NC}"
echo -e "${CYAN}Запускаю бота...${NC}"

./downloader.sh up

echo -e "\n${GREEN}Бот должен быть запущен!${NC}"
echo -e "Используйте ${YELLOW}./downloader.sh logs${NC} для просмотра логов."
