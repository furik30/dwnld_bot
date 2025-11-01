import os
from dotenv import load_dotenv

# Загружаем переменные окружения из файла .env
load_dotenv()

# --- TELEGRAM ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OWNER_USERNAME = os.getenv("OWNER_USERNAME")
# --- INSTAGRAM ---
# Оставьте пустым, если не используете
INSTAGRAM_USERNAME = os.getenv("INSTAGRAM_USERNAME", "")
# Путь к файлу сессии будет формироваться относительно папки проекта
INSTAGRAM_SESSION_FILE = os.path.join(os.path.dirname(__file__), f"{INSTAGRAM_USERNAME}.session") if INSTAGRAM_USERNAME else ""

# --- ОГРАНИЧЕНИЯ ---
MAX_DURATION = int(os.getenv("MAX_DURATION", 1200))  # 20 минут по умолчанию
MAX_PLAYLIST_ITEMS = int(os.getenv("MAX_PLAYLIST_ITEMS", 10)) # 10 треков по умолчанию

# --- COOKIES ---
# Путь к файлу cookies для YouTube (помогает обходить ограничения по возрасту)
COOKIES_FILE = os.path.join(os.path.dirname(__file__), 'youtube_cookies.txt')

# Проверка наличия токена
if not TELEGRAM_TOKEN:
    raise ValueError("Необходимо указать TELEGRAM_TOKEN в файле .env")
