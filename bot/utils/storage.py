import json
import os
import time
from config import DEEP_LINKS_FILE
from utils.logger import logger

def _load_links():
    if not os.path.exists(DEEP_LINKS_FILE):
        return {}
    try:
        with open(DEEP_LINKS_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Ошибка загрузки deep links: {e}")
        return {}

def _save_links(links):
    try:
        with open(DEEP_LINKS_FILE, 'w') as f:
            json.dump(links, f, indent=4)
    except Exception as e:
        logger.error(f"Ошибка сохранения deep links: {e}")

def save_deep_link(key: str, url: str):
    """
    Сохраняет ключ и URL deep link в постоянное хранилище.
    Без удаления старых ссылок.
    """
    links = _load_links()
    links[key] = {
        "url": url,
        "timestamp": time.time()
    }
    _save_links(links)
    logger.info(f"🔗 Deep Link создан: ключ={key}, ссылка={url}")

def get_deep_link(key: str) -> str:
    """
    Получает URL по ключу deep link без удаления.
    """
    links = _load_links()
    data = links.get(key, None)

    if data:
        logger.info(f"🔗 Переход по Deep Link: ключ={key} -> {data['url']}")
        return data["url"]
    else:
        logger.warning(f"⚠️ Попытка перехода по несуществующему Deep Link: ключ={key}")
        return None