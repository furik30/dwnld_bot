#!/bin/bash

BOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$BOT_DIR"

BRANCH=${1:-main}
GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}🔄 Обновление из ветки $BRANCH...${NC}"

# Сохраняем локальные правки если есть
git stash 2>/dev/null

git fetch origin
git checkout "$BRANCH"
git pull origin "$BRANCH"

# Возвращаем правки
git stash pop 2>/dev/null

echo -e "${CYAN}🚀 Пересборка контейнеров...${NC}"
docker compose up -d --build

echo -e "${GREEN}✅ Обновление завершено успешно!${NC}"