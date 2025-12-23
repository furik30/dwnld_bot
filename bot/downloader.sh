#!/bin/bash

# Определяем папку, где лежит сам скрипт
BOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$BOT_DIR"

# Цвета
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# Данные для Docker
export USER_ID=$(id -u)
export GROUP_ID=$(id -g)

usage() {
    echo -e "${CYAN}Downloader CLI. Использование: downloader [команда]${NC}"
    echo "  up        - Собрать и запустить бота"
    echo "  down      - Остановить"
    echo "  restart   - Перезагрузить"
    echo "  logs      - Просмотр логов (-f)"
    echo "  update    - Обновить код из ветки dev"
    echo "  edit      - Редактировать .env"
    echo "  uninstall - Полное удаление проекта"
}

case "$1" in
    up)
        docker compose up -d --build
        echo -e "${GREEN}Бот запущен.${NC}"
        ;;
    down)
        docker compose down
        echo -e "${YELLOW}Бот остановлен.${NC}"
        ;;
    restart)
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