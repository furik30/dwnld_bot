import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- TELEGRAM ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
OWNER_ID = int(os.getenv("OWNER_ID", 0))

# --- INSTAGRAM ---
INSTAGRAM_USERNAME = os.getenv("INSTAGRAM_USERNAME", "")
# Path to Instagram cookies file (Netscape format)
INSTAGRAM_COOKIES_FILE = os.getenv("INSTAGRAM_COOKIES_FILE", "instagram_cookies.txt")

# --- PATHS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOADS_DIR = os.path.join(BASE_DIR, "downloads")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
DATA_DIR = os.path.join(BASE_DIR, "data")
MESSAGES_FILE = os.path.join(BASE_DIR, "config", "messages.yml")
DEEP_LINKS_FILE = os.path.join(DATA_DIR, "deep_links_cache.json")

# --- LIMITS ---
MAX_DURATION = int(os.getenv("MAX_DURATION", 1200))  # 20 minutes default
MAX_PLAYLIST_ITEMS = int(os.getenv("MAX_PLAYLIST_ITEMS", 10))

# --- YOUTUBE COOKIES ---
COOKIES_FILE = os.path.join(BASE_DIR, 'youtube_cookies.txt')

# Ensure directories exist
for directory in [DOWNLOADS_DIR, LOGS_DIR, DATA_DIR]:
    os.makedirs(directory, exist_ok=True)
