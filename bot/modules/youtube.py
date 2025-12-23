import os
import yt_dlp
from pyrogram import Client
from pyrogram.types import Message
from config import DOWNLOADS_DIR, COOKIES_FILE, MAX_DURATION, MAX_PLAYLIST_ITEMS
from utils.common import run_blocking
from utils.logger import logger
from utils.messages import get_message

class DurationLimitError(Exception):
    pass

async def search_youtube(query: str, limit: int = 5):
    """Ищет видео на YouTube."""
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'force_generic_extractor': True,
        'age_limit': 99,
        'cookiefile': COOKIES_FILE if os.path.exists(COOKIES_FILE) else None
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = await run_blocking(ydl.extract_info, f"ytsearch{limit}:{query}", download=False)
            return result.get('entries', [])
    except Exception as e:
        logger.error(f"Ошибка поиска на YouTube: {e}", exc_info=True)
        return []

async def download_audio(client: Client, chat_id: int, url: str, status_message: Message = None):
    """Скачивает аудио с YouTube и отправляет его."""
    try:
        if status_message:
            await status_message.edit_text(get_message("downloads.downloading_track"))

        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3'}],
            'outtmpl': os.path.join(DOWNLOADS_DIR, '%(title)s.%(ext)s'),
            'noplaylist': True, 'quiet': True, 'age_limit': 99,
            'cookiefile': COOKIES_FILE if os.path.exists(COOKIES_FILE) else None
        }

        filename = None
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = await run_blocking(ydl.extract_info, url, download=False)
            # Обработка случаев, когда info может быть плейлистом или одиночным видео
            entry = info.get('entries', [info])[0]

            duration = int(entry.get('duration', 0))
            if duration > MAX_DURATION:
                raise DurationLimitError(get_message("errors.duration_limit", duration=duration, max_duration=MAX_DURATION))

            await run_blocking(ydl.download, [url])

            temp_filename = ydl.prepare_filename(entry)
            base_name = temp_filename.rsplit('.', 1)[0]
            filename = f"{base_name}.mp3"

            # Проверка существования файла
            if not os.path.exists(filename):
                pass

        if filename and os.path.exists(filename):
            if status_message:
                await status_message.edit_text(get_message("downloads.sending_file"))

            await client.send_audio(
                chat_id=chat_id,
                audio=filename,
                caption=get_message("downloads.caption", bot_username=client.me.username),
                title=entry.get('track') or entry.get('title') or "Unknown",
                performer=entry.get('artist') or entry.get('uploader') or "Unknown",
                duration=duration
            )
            if status_message:
                await status_message.delete()
        else:
             raise Exception("Файл не найден после скачивания")

    except DurationLimitError as e:
        if status_message: await status_message.edit_text(str(e))
    except Exception as e:
        logger.error(f"Ошибка скачивания аудио {url}: {e}", exc_info=True)
        if status_message: await status_message.edit_text(get_message("errors.download_failed"))
    finally:
        if filename and os.path.exists(filename):
            os.remove(filename)

async def download_video(client: Client, chat_id: int, url: str, status_message: Message = None):
    """Скачивает видео с поддерживаемых сайтов и отправляет его."""
    try:
        if status_message:
            await status_message.edit_text(get_message("downloads.downloading_video"))

        # Используем id в имени файла, чтобы избежать проблем с символами
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': os.path.join(DOWNLOADS_DIR, '%(id)s.%(ext)s'),
            'noplaylist': True, 'quiet': True, 'age_limit': 99,
            'cookiefile': COOKIES_FILE if os.path.exists(COOKIES_FILE) else None
        }

        filename = None
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = await run_blocking(ydl.extract_info, url, download=False)
            duration = int(info.get('duration', 0))

            if duration > MAX_DURATION:
                 raise DurationLimitError(get_message("errors.duration_limit", duration=duration, max_duration=MAX_DURATION))

            await run_blocking(ydl.download, [url])
            filename = ydl.prepare_filename(info)

        if filename and os.path.exists(filename):
            if status_message:
                await status_message.edit_text(get_message("downloads.sending_file"))

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
        logger.error(f"Ошибка скачивания видео {url}: {e}", exc_info=True)
        if status_message: await status_message.edit_text(get_message("errors.download_failed"))
    finally:
        if filename and os.path.exists(filename):
            os.remove(filename)

async def handle_playlist(client: Client, message: Message, url: str, platform: str):
    status_msg = await message.reply_text(get_message("downloads.analyzing_playlist", platform=platform))
    try:
        ydl_opts = {
            'quiet': True,
            'extract_flat': True,
            'playlistend': MAX_PLAYLIST_ITEMS,
            'age_limit': 99,
            'cookiefile': COOKIES_FILE if os.path.exists(COOKIES_FILE) else None
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            playlist_info = await run_blocking(ydl.extract_info, url, download=False)

        entries = playlist_info.get('entries', [])
        if not entries:
            await status_msg.edit_text(get_message("errors.no_results"))
            return

        await status_msg.edit_text(get_message("downloads.playlist_found", count=len(entries)))

        # Скачиваем элементы последовательно
        for i, entry in enumerate(entries):
            video_url = entry.get('url')
            if platform == "YouTube":
                video_url = f"https://www.youtube.com/watch?v={entry['id']}"

            title = entry.get('title', 'Unknown')
            track_msg = await message.reply_text(
                get_message("downloads.playlist_track", current=i+1, total=len(entries), title=title)
            )

            try:
                await download_audio(client, message.chat.id, video_url, track_msg)
            except Exception as e:
                logger.error(f"Ошибка трека из плейлиста: {e}")

    except Exception as e:
        logger.error(f"Ошибка обработки плейлиста {url}: {e}", exc_info=True)
        await status_msg.edit_text(get_message("errors.generic"))
