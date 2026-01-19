import os
import yt_dlp
from pyrogram import Client
from pyrogram.types import Message
from config import DOWNLOADS_DIR, TIKTOK_COOKIES_FILE, MAX_DURATION
from utils.common import run_blocking
from utils.logger import logger
from utils.messages import get_message

class DurationLimitError(Exception):
    pass

async def download_tiktok(client: Client, chat_id: int, url: str, status_message: Message = None):
    """
    Специализированный модуль для скачивания видео с TikTok.
    Использует специфичные заголовки и отдельный файл cookies.
    """
    filename = None
    try:
        if status_message:
            await status_message.edit_text(get_message("downloads.downloading_video"))

        # Специфичные заголовки для TikTok, чтобы избежать 403 Forbidden
        http_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://www.tiktok.com/',
            'Accept-Language': 'en-US,en;q=0.9',
        }

        # Опции yt-dlp специально для TikTok
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'impersonate': 'chrome',
            'outtmpl': os.path.join(DOWNLOADS_DIR, 'tiktok_%(id)s.%(ext)s'),
            'noplaylist': True,
            'quiet': True,
            'age_limit': 99,
            'http_headers': http_headers,
            'cookiefile': TIKTOK_COOKIES_FILE if os.path.exists(TIKTOK_COOKIES_FILE) else None
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Получаем информацию без скачивания для проверки длительности
            info = await run_blocking(ydl.extract_info, url, download=False)
            duration = int(info.get('duration', 0))

            if duration > MAX_DURATION:
                 raise DurationLimitError(get_message("errors.duration_limit", duration=duration, max_duration=MAX_DURATION))

            # Скачиваем видео
            await run_blocking(ydl.download, [url])
            filename = ydl.prepare_filename(info)

        if filename and os.path.exists(filename):
            if status_message:
                await status_message.edit_text(get_message("downloads.sending_file"))

            # Отправляем видео
            await client.send_video(
                chat_id=chat_id,
                video=filename,
                caption=get_message("downloads.caption", bot_username=client.me.username),
                duration=duration,
                width=info.get('width'),
                height=info.get('height')
            )
            if status_message:
                await status_message.delete()
        else:
             raise Exception("Файл не найден после скачивания")

    except DurationLimitError as e:
         if status_message: await status_message.edit_text(str(e))
    except Exception as e:
        logger.error(f"Ошибка скачивания TikTok {url}: {e}", exc_info=True)
        if status_message: await status_message.edit_text(get_message("errors.download_failed"))
    finally:
        # Удаляем файл после отправки
        if filename and os.path.exists(filename):
            try:
                os.remove(filename)
            except OSError:
                pass