#!/bin/bash

# Путь к директории бота (определяется автоматически)
BOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$BOT_DIR"

# Цвета
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# Экспорт ID для Docker
export USER_ID=$(id -u)
export GROUP_ID=$(id -g)

usage() {
    echo -e "${CYAN}Использование: downloader [команда]${NC}"
    echo "  up        - Запустить бота (в фоне)"
    echo "  down      - Остановить бота"
    echo "  restart   - Перезагрузить"
    echo "  logs      - Посмотреть логи (-f)"
    echo "  status    - Состояние контейнеров"
    echo "  update    - Обновить код и пересобрать"
    echo "  edit      - Редактировать .env"
    echo "  uninstall - Полное удаление проекта"
}

case "$1" in
    up)
        docker compose up -d --build
        echo -e "${GREEN}Бот запущен в фоне.${NC}"
        ;;
    down)
        docker compose down
        echo -e "${YELLOW}Бот остановлен.${NC}"
        ;;
    restart)
        docker compose restart
        echo -e "${GREEN}Бот перезагружен.${NC}"
        ;;
    logs)
        docker compose logs -f --tail=100
        ;;
    status)
        docker compose ps
        ;;
    update)
        bash update.sh "$2"
        ;;
    edit)
        ${EDITOR:-nano} .env
        echo -e "${YELLOW}Не забудьте выполнить 'downloader up' для применения правок.${NC}"
        ;;
    uninstall)
        bash uninstall.sh
        ;;
    *)
        usage
        ;;
esac