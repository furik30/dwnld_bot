import asyncio
import functools
import re
from urllib.parse import urlparse

async def run_blocking(func, *args, **kwargs):
    """Запускает блокирующую функцию в отдельном потоке."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, functools.partial(func, *args, **kwargs))

def is_valid_url(url: str) -> bool:
    """
    Проверяет, является ли строка валидным URL.
    Поддерживает ссылки с протоколом и без (если они похожи на домен).
    """
    if not url:
        return False
        
    # Если протокола нет, временно добавляем его для проверки через urlparse
    if not url.startswith(('http://', 'https://')):
        test_url = f"https://{url}"
    else:
        test_url = url

    try:
        result = urlparse(test_url)
        # Проверяем наличие домена (netloc) и наличие точки в нем (чтобы не путать с простыми словами)
        return bool(result.netloc and '.' in result.netloc)
    except ValueError:
        return False

def normalize_url(url: str) -> str:
    """Очищает ссылку и добавляет https://, если он отсутствует."""
    url = url.strip()
    if not url:
        return url
        
    if not url.startswith(('http://', 'https://')):
        # Если это похоже на путь или домен, добавляем протокол
        return f"https://{url}"
    return url

def get_platform(url: str) -> str:
    """Определяет платформу по URL."""
    url_lower = url.lower()
    if "youtube.com" in url_lower or "youtu.be" in url_lower:
        if "list=" in url:
            return "YouTubePlaylist"
        return "YouTube"
    elif "instagram.com" in url_lower:
        return "Instagram"
    elif "tiktok.com" in url_lower:
        return "TikTok"
    elif "soundcloud.com" in url_lower:
        if "/sets/" in url_lower:
            return "SoundCloudPlaylist"
        return "SoundCloud"
    return "Unknown"

