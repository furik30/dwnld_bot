#!/bin/bash

# Скрипт обновления (зафиксирован на ветку dev)
BOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$BOT_DIR")"
BRANCH="dev"

GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}🔄 Обновление из репозитория (ветка: $BRANCH)...${NC}"

cd "$PROJECT_ROOT"

# Сохраняем локальные конфиги
git stash 2>/dev/null

git fetch origin "$BRANCH"
git checkout "$BRANCH"
git pull origin "$BRANCH"

# Возвращаем конфиги
git stash pop 2>/dev/null

echo -e "${CYAN}🚀 Пересборка контейнеров...${NC}"
cd "$BOT_DIR"
docker compose up -d --build

echo -e "${GREEN}✅ Обновление выполнено.${NC}"