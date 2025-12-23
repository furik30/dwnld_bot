import os
import glob
import shutil
import instaloader
from pyrogram import Client
from pyrogram.types import Message
from config import DOWNLOADS_DIR, INSTAGRAM_COOKIES_FILE, MAX_DURATION
from utils.common import run_blocking
from utils.logger import logger
from utils.messages import get_message

class DurationLimitError(Exception):
    pass

async def download_instagram(client: Client, chat_id: int, url: str, status_message: Message = None):
    """Скачивает Instagram Reel/Video."""
    target_profile = None
    try:
        if status_message:
            await status_message.edit_text(get_message("downloads.downloading_video"))

        L = instaloader.Instaloader(
            download_pictures=False, download_video_thumbnails=False, download_geotags=False,
            download_comments=False, save_metadata=False, compress_json=False,
            dirname_pattern=os.path.join(DOWNLOADS_DIR, '{profile}'),
            sleep=True, request_timeout=30, max_connection_attempts=3
        )

        if os.path.exists(INSTAGRAM_COOKIES_FILE):
             try:
                 L.load_cookies_from_mozilla(INSTAGRAM_COOKIES_FILE)
             except Exception as e:
                 logger.warning(f"Не удалось загрузить cookies Instagram: {e}")

        # Извлечение shortcode
        try:
            shortcode = url.rstrip('/').split('/')[-1]
            if not shortcode: # Handle trailing slash
                 shortcode = url.rstrip('/').split('/')[-2]
        except:
            shortcode = None

        if not shortcode:
             raise Exception("Не удалось извлечь shortcode")

        post = await run_blocking(instaloader.Post.from_shortcode, L.context, shortcode)

        if post.video_duration > MAX_DURATION:
             raise DurationLimitError(get_message("errors.duration_limit", duration=int(post.video_duration), max_duration=MAX_DURATION))

        target_profile = post.owner_username

        # Скачивание
        await run_blocking(L.download_post, post, target=target_profile)

        # Поиск видеофайла
        download_dir = os.path.join(DOWNLOADS_DIR, target_profile)
        video_files = glob.glob(os.path.join(download_dir, '*.mp4'))

        if not video_files:
             raise Exception("Видеофайл не найден")

        video_path = video_files[0]

        if status_message:
             await status_message.edit_text(get_message("downloads.sending_file"))

        await client.send_video(
             chat_id=chat_id,
             video=video_path,
             caption=get_message("downloads.caption", bot_username=client.me.username)
        )
        if status_message:
             await status_message.delete()

    except instaloader.exceptions.ConnectionException:
         if status_message: await status_message.edit_text(get_message("errors.instagram_limit"))
    except DurationLimitError as e:
         if status_message: await status_message.edit_text(str(e))
    except Exception as e:
        logger.error(f"Ошибка скачивания Instagram {url}: {e}", exc_info=True)
        if status_message: await status_message.edit_text(get_message("errors.download_failed"))
    finally:
        # Очистка
        if target_profile:
             dir_path = os.path.join(DOWNLOADS_DIR, target_profile)
             if os.path.exists(dir_path):
                  shutil.rmtree(dir_path)
