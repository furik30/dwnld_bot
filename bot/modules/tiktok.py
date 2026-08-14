import os
import re
import urllib.request
import yt_dlp
from yt_dlp.utils import DownloadError
from pyrogram import Client
from pyrogram.types import Message, InputMediaPhoto
from config import DOWNLOADS_DIR, TIKTOK_COOKIES_FILE, MAX_DURATION
from utils.common import run_blocking
from utils.logger import logger
from utils.messages import get_message

PHOTO_POST_RE = re.compile(r'tiktok\.com/@([\w.-]+)/photo/(\d+)')

class DurationLimitError(Exception):
    pass

def _normalize_tiktok_url(url: str) -> str:
    m = PHOTO_POST_RE.search(url)
    if m:
        return f'https://www.tiktok.com/@{m.group(1)}/video/{m.group(2)}'
    return url

def _get_slideshow_images(info: dict) -> list:
    return list(dict.fromkeys(
        t['url'] for t in info.get('thumbnails', []) if 'photomode' in t.get('url', '')
    ))

async def download_tiktok(client: Client, chat_id: int, url: str, status_message: Message = None):
    """
    Скачивание постов TikTok: видео, фото-посты (слайд-шоу) отправляются альбомом.
    Заголовки с обычным Chrome UA; impersonate (curl_cffi) не используется —
    TikTok детектит TLS-отпечатки curl_cffi и отдаёт challenge-страницу.
    """
    downloaded_files = []
    try:
        is_photo_post = bool(PHOTO_POST_RE.search(url))
        url = _normalize_tiktok_url(url)

        if status_message:
            msg_key = "downloads.downloading_photo" if is_photo_post else "downloads.downloading_video"
            await status_message.edit_text(get_message(msg_key))

        http_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
            'Referer': 'https://www.tiktok.com/',
            'Accept-Language': 'en-US,en;q=0.9',
        }

        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': os.path.join(DOWNLOADS_DIR, 'tiktok_%(id)s.%(ext)s'),
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            'age_limit': 99,
            'http_headers': http_headers,
            'cookiefile': TIKTOK_COOKIES_FILE if os.path.exists(TIKTOK_COOKIES_FILE) else None
        }

        url = _normalize_tiktok_url(url)

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = await run_blocking(ydl.extract_info, url, download=False)
            except DownloadError as e:
                # yt-dlp не знает /photo/ — переписываем разрешённый URL на /video/
                if "Unsupported URL" in str(e):
                    m = PHOTO_POST_RE.search(str(e))
                    if not m:
                        raise
                    url = f'https://www.tiktok.com/@{m.group(1)}/video/{m.group(2)}'
                    if status_message:
                        await status_message.edit_text(get_message("downloads.downloading_photo"))
                    info = await run_blocking(ydl.extract_info, url, download=False)
                else:
                    raise

            images = _get_slideshow_images(info)

            if images:
                # Фото-пост: скачиваем изображения и отправляем альбомом
                def _fetch_image(img_url: str, path: str):
                    req = urllib.request.Request(img_url, headers=http_headers)
                    with urllib.request.urlopen(req, timeout=30) as resp, open(path, 'wb') as f:
                        f.write(resp.read())

                post_id = info.get('id')
                for i, img_url in enumerate(images):
                    path = os.path.join(DOWNLOADS_DIR, f'tiktok_{post_id}_{i}.jpg')
                    await run_blocking(_fetch_image, img_url, path)
                    downloaded_files.append(path)

                if status_message:
                    await status_message.edit_text(get_message("downloads.sending_file"))

                caption = get_message("downloads.caption", bot_username=client.me.username)
                if len(downloaded_files) == 1:
                    await client.send_photo(chat_id=chat_id, photo=downloaded_files[0], caption=caption)
                else:
                    for i in range(0, len(downloaded_files), 10):
                        chunk = downloaded_files[i:i + 10]
                        media = [InputMediaPhoto(media=p) for p in chunk]
                        media[0] = InputMediaPhoto(media=chunk[0], caption=caption)
                        await client.send_media_group(chat_id=chat_id, media=media)
            else:
                # Обычное видео
                duration = int(info.get('duration', 0))

                if duration > MAX_DURATION:
                    raise DurationLimitError(get_message("errors.duration_limit", duration=duration, max_duration=MAX_DURATION))

                await run_blocking(ydl.download, [url])
                filename = ydl.prepare_filename(info)
                downloaded_files.append(filename)

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

    except DurationLimitError as e:
        if status_message:
            await status_message.edit_text(str(e))

    except DownloadError as e:
        logger.error(f"Ошибка yt-dlp при скачивании TikTok {url}: {e}")
        error_text = str(e)
        if error_text.startswith("ERROR: "):
            error_text = error_text[len("ERROR: "):]
        if status_message:
            await status_message.edit_text(f"❌ Не удалось скачать: {error_text}")

    except Exception as e:
        logger.error(f"Общая ошибка скачивания TikTok {url}: {e}", exc_info=True)
        if status_message:
            await status_message.edit_text(get_message("errors.download_failed"))
    finally:
        for path in downloaded_files:
            if os.path.exists(path):
                try:
                    os.remove(path)
                except OSError:
                    pass