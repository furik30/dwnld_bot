import asyncio
import functools
import re
from urllib.parse import urlparse

async def run_blocking(func, *args, **kwargs):
    """Runs a blocking function in a separate thread."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, functools.partial(func, *args, **kwargs))

def is_valid_url(url: str) -> bool:
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

def get_platform(url: str) -> str:
    if "youtube.com" in url or "youtu.be" in url:
        if "list=" in url:
            return "YouTubePlaylist"
        return "YouTube"
    elif "instagram.com" in url:
        return "Instagram"
    elif "tiktok.com" in url:
        return "TikTok"
    elif "soundcloud.com" in url:
        if "/sets/" in url:
            return "SoundCloudPlaylist"
        return "SoundCloud"
    return "Unknown"
