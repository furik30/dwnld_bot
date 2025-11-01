#!/bin/bash

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}--- Запуск установщика Downloader Bot ---${NC}"

# 1. Проверка наличия python3 и venv
if ! command -v python3 &> /dev/null
then
    echo "Ошибка: python3 не найден. Пожалуйста, установите Python 3."
    exit 1
fi

if ! python3 -c "import ensurepip" &> /dev/null
then
    echo "Ошибка: Модуль venv не найден. Установите его (например, sudo apt install python3-venv)."
    exit 1
fi

# 2. Создание виртуального окружения
if [ ! -d "venv" ]; then
    echo "Создаю виртуальное окружение в папке 'venv'..."
    python3 -m venv venv
else
    echo "Виртуальное окружение 'venv' уже существует."
fi

# 3. Активация окружения и установка зависимостей
echo "Активирую окружение и устанавливаю зависимости из dwnld_bot/requirements.txt..."
source venv/bin/activate
pip install -r dwnld_bot/requirements.txt

# 4. Создание .env файла
if [ ! -f "dwnld_bot/.env" ]; then
    echo "Создаю файл .env в dwnld_bot/ из .env.example..."
    cp dwnld_bot/.env.example dwnld_bot/.env
else
    echo "Файл dwnld_bot/.env уже существует."
fi

echo -e "\n${GREEN}--- Установка завершена! ---${NC}"
echo -e "${YELLOW}ВАЖНО:${NC} Откройте файл ${GREEN}dwnld_bot/.env${NC} и вставьте ваш TELEGRAM_TOKEN."
echo "После этого запустите бота командой:"
echo -e "${GREEN}source venv/bin/activate && python dwnld_bot/dwnld_bot.py${NC}"
