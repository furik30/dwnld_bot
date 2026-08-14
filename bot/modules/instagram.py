import os
import yt_dlp
from yt_dlp.utils import YoutubeDLError
from pyrogram import Client
from pyrogram.types import Message
from config import DOWNLOADS_DIR, INSTAGRAM_COOKIES_FILE, MAX_DURATION
from utils.common import run_blocking
from utils.logger import logger
from utils.messages import get_message

class DurationLimitError(Exception):
    pass

async def download_instagram(client: Client, chat_id: int, url: str, status_message: Message = None):
    """
    Скачивание видео/Reels с Instagram через yt-dlp.
    Использует cookies из файла для обхода блокировок и авторизации.
    """
    filename = None
    try:
        if status_message:
            await status_message.edit_text(get_message("downloads.downloading_video"))

        # Настройки yt-dlp
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': os.path.join(DOWNLOADS_DIR, 'insta_%(id)s.%(ext)s'),
            'noplaylist': True,
            'quiet': True,
            'age_limit': 99,
            'cookiefile': INSTAGRAM_COOKIES_FILE if os.path.exists(INSTAGRAM_COOKIES_FILE) else None,
        }

        # Пытаемся инициализировать с impersonate (требует curl_cffi)
        # Если не выходит (например, при локальном тесте без либы) — переключаемся на стандартный режим
        try:
            ydl_instance = yt_dlp.YoutubeDL(ydl_opts)
        except (YoutubeDLError, AssertionError, Exception) as e:
            # Мы ловим AssertionError и любые другие ошибки инициализации
            ydl_opts.pop('http_headers', None) 
            ydl_instance = yt_dlp.YoutubeDL(ydl_opts)

        with ydl_instance as ydl:
            # Получаем информацию о видео
            info = await run_blocking(ydl.extract_info, url, download=False)
            
            # Проверяем длительность
            duration = int(info.get('duration', 0))
            if duration > MAX_DURATION:
                 raise DurationLimitError(get_message("errors.duration_limit", duration=duration, max_duration=MAX_DURATION))

            # Скачиваем
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
        logger.error(f"Ошибка скачивания Instagram {url}: {e}", exc_info=True)
        if status_message:
            await status_message.edit_text(get_message("errors.download_failed"))
    finally:
        # Удаляем файл
        if filename and os.path.exists(filename):
            try:
                os.remove(filename)
            except OSError:
                pass