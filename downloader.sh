#!/bin/bash

# Цветовые коды
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # Без цвета

# Проверка установки Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker не установлен. Пожалуйста, установите Docker.${NC}"
    exit 1
fi

# Функция вывода справки
usage() {
    echo "Использование: $0 {up|down|restart|logs|status|update|edit-env|login}"
    echo "  up        : Запустить бота (в фоновом режиме)"
    echo "  down      : Остановить бота"
    echo "  restart   : Перезагрузить бота"
    echo "  logs [n]  : Показать логи (опционально: n строк)"
    echo "  status    : Показать статус контейнера"
    echo "  update    : Скачать обновления и перезапустить"
    echo "  edit-env  : Редактировать файл .env"
    echo "  login     : Настройка входа (проверка токена)"
}

# Проверка наличия .env
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        echo -e "${YELLOW}.env не найден. Копирую из .env.example...${NC}"
        cp .env.example .env
        echo -e "${YELLOW}Пожалуйста, отредактируйте .env и укажите ваши данные.${NC}"
    else
        echo -e "${RED}.env и .env.example не найдены!${NC}"
    fi
fi

# Экспорт UID/GID для docker-compose (исправление прав доступа)
export UID=$(id -u)
export GID=$(id -g)

case "$1" in
    up)
        echo -e "${GREEN}Запуск бота...${NC}"
        docker compose up -d --build
        ;;
    down)
        echo -e "${YELLOW}Остановка бота...${NC}"
        docker compose down
        ;;
    restart)
        echo -e "${YELLOW}Перезагрузка бота...${NC}"
        docker compose restart
        ;;
    logs)
        lines=${2:-100}
        docker compose logs -f --tail="$lines"
        ;;
    status)
        docker compose ps
        ;;
    update)
        echo -e "${GREEN}Обновление бота...${NC}"
        git pull
        docker compose up -d --build
        ;;
    edit-env)
        ${EDITOR:-nano} .env
        ;;
    login)
        echo -e "${GREEN}Для входа убедитесь, что TELEGRAM_TOKEN указан в .env${NC}"
        ${EDITOR:-nano} .env
        ;;
    *)
        usage
        exit 1
        ;;
esac
