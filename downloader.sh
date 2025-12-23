#!/bin/bash

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

# Function to show usage
usage() {
    echo "Usage: $0 {up|down|restart|logs|status|update|edit-env|login}"
    echo "  up        : Start the bot (detached mode)"
    echo "  down      : Stop the bot"
    echo "  restart   : Restart the bot"
    echo "  logs [n]  : Show logs (optional: n lines)"
    echo "  status    : Show container status"
    echo "  update    : Pull latest changes and restart"
    echo "  edit-env  : Edit .env file"
    echo "  login     : Run a script to generate session (if needed)"
}

# Ensure .env exists
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        echo -e "${YELLOW}.env not found. Copying from .env.example...${NC}"
        cp .env.example .env
        echo -e "${YELLOW}Please edit .env with your credentials.${NC}"
    else
        echo -e "${RED}.env and .env.example not found!${NC}"
    fi
fi

# Export UID/GID for docker-compose to fix permission issues
export UID=$(id -u)
export GID=$(id -g)

case "$1" in
    up)
        echo -e "${GREEN}Starting bot...${NC}"
        docker compose up -d --build
        ;;
    down)
        echo -e "${YELLOW}Stopping bot...${NC}"
        docker compose down
        ;;
    restart)
        echo -e "${YELLOW}Restarting bot...${NC}"
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
        echo -e "${GREEN}Updating bot...${NC}"
        git pull
        docker compose up -d --build
        ;;
    edit-env)
        ${EDITOR:-nano} .env
        ;;
    login)
        # Assuming login logic is just ensuring .env is set or running a specialized script
        # Since we use Bot Token, 'login' is mostly about config.
        echo -e "${GREEN}To login, ensure TELEGRAM_TOKEN is set in .env${NC}"
        ${EDITOR:-nano} .env
        ;;
    *)
        usage
        exit 1
        ;;
esac
