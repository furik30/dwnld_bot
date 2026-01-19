import os
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# --- TELEGRAM ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
OWNER_ID = int(os.getenv("OWNER_ID", 0))

# --- ПУТИ ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COOKIES_DIR = os.path.join(BASE_DIR, "cookies")
DOWNLOADS_DIR = os.path.join(BASE_DIR, "downloads")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
DATA_DIR = os.path.join(BASE_DIR, "data")
MESSAGES_FILE = os.path.join(BASE_DIR, "config", "messages.yml")
DEEP_LINKS_FILE = os.path.join(DATA_DIR, "deep_links_cache.json")

# --- INSTAGRAM ---
INSTAGRAM_USERNAME = os.getenv("INSTAGRAM_USERNAME", "")
# Путь к файлу cookies Instagram (формат Netscape)
INSTAGRAM_COOKIES_FILE = os.path.join(COOKIES_DIR, 'instagram_cookies.txt')

# --- YOUTUBE ---
YOUTUBE_COOKIES_FILE = os.path.join(COOKIES_DIR, 'youtube_cookies.txt')

# --- TIKTOK ---
TIKTOK_COOKIES_FILE = os.getenv(COOKIES_DIR, "tiktok_cookies.txt")

# --- ОГРАНИЧЕНИЯ ---
MAX_DURATION = int(os.getenv("MAX_DURATION", 1200))  # 20 минут по умолчанию
MAX_PLAYLIST_ITEMS = int(os.getenv("MAX_PLAYLIST_ITEMS", 10))

# Создание необходимых директорий
for directory in [DOWNLOADS_DIR, LOGS_DIR, DATA_DIR]:
    os.makedirs(directory, exist_ok=True)
