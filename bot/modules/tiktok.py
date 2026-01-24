import os
import yt_dlp
from yt_dlp.utils import DownloadError
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
    Использует client-impersonation для обхода защиты (требует curl-cffi).
    """
    filename = None
    try:
        if status_message:
            await status_message.edit_text(get_message("downloads.downloading_video"))

        # Опции yt-dlp. 
        # Мы убрали ручные http_headers, так как 'impersonate' генерирует их автоматически.
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': os.path.join(DOWNLOADS_DIR, 'tiktok_%(id)s.%(ext)s'),
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            'age_limit': 99,
            
            # Cookies могут помочь, но иногда конфликтуют с impersonate. 
            # Если будут ошибки, попробуйте временно отключить cookiefile.
            'cookiefile': TIKTOK_COOKIES_FILE if os.path.exists(TIKTOK_COOKIES_FILE) else None
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Получаем информацию
            try:
                info = await run_blocking(ydl.extract_info, url, download=False)
            except DownloadError as e:
                # Если ошибка связана с блокировкой, пробуем еще раз без cookies или логируем
                if "Unable to extract" in str(e) or "403" in str(e):
                    logger.warning(f"TikTok вернул ошибку при получении инфо. Проверьте 'yt-dlp -U' или cookie файл. Ошибка: {e}")
                raise e

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
    
    except DownloadError as e:
        logger.error(f"Ошибка yt-dlp при скачивании TikTok {url}: {e}")
        # Часто TikTok выдает ошибку, если версия yt-dlp устарела
        if status_message: 
            await status_message.edit_text("Ошибка скачивания. Возможно, TikTok обновил защиту. Попробуйте обновить бота.")
            
    except Exception as e:
        logger.error(f"Общая ошибка скачивания TikTok {url}: {e}", exc_info=True)
        if status_message: await status_message.edit_text(get_message("errors.download_failed"))
        
    finally:
        # Удаляем файл после отправки
        if filename and os.path.exists(filename):
            try:
                os.remove(filename)
            except OSError:
                pass