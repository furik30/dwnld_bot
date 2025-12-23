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
        logger.error(f"Error loading deep links: {e}")
        return {}

def _save_links(links):
    try:
        with open(DEEP_LINKS_FILE, 'w') as f:
            json.dump(links, f)
    except Exception as e:
        logger.error(f"Error saving deep links: {e}")

def save_deep_link(key: str, url: str):
    """Saves a deep link key and URL to persistent storage."""
    links = _load_links()
    links[key] = {
        "url": url,
        "timestamp": time.time()
    }
    _save_links(links)

def get_deep_link(key: str) -> str:
    """Retrieves and removes a URL by its deep link key."""
    links = _load_links()
    data = links.pop(key, None)

    # Optional: cleanup old links here if needed
    # ...

    _save_links(links)
    return data["url"] if data else None
