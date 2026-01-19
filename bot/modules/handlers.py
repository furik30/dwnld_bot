import os
from pyrogram import Client, filters
from pyrogram.types import (
    Message, CallbackQuery, InlineQuery,
    InlineQueryResultArticle, InputTextMessageContent,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from config import MAX_DURATION
from utils.common import get_platform, is_valid_url, normalize_url
from utils.storage import save_deep_link, get_deep_link
from utils.messages import get_message
from modules.youtube import search_youtube, download_audio, download_video, handle_playlist
from modules.instagram import download_instagram
from modules.tiktok import download_tiktok

# --- Обработчики команд ---

async def start_handler(client: Client, message: Message):
    # Проверка на наличие deep link аргумента
    if len(message.command) > 1:
        payload = message.command[1]

        # Скачивание аудио по ID (dl_ID)
        if payload.startswith('dl_'):
            video_id = payload.replace('dl_', '')
            url = f"https://www.youtube.com/watch?v={video_id}"
            await message.reply_text(get_message("downloads.download_start"))
            await download_audio(client, message.chat.id, url)
            return

        # Скачивание видео по ключу (vid_KEY)
        elif payload.startswith('vid_'):
            key = payload.replace('vid_', '')
            url = get_deep_link(key)

            if url:
                url = normalize_url(url) # Нормализуем ссылку из кэша
                await message.reply_text(get_message("downloads.download_start"))
                # Определение платформы
                platform = get_platform(url)
                if platform == "Instagram":
                    await download_instagram(client, message.chat.id, url)
                elif platform == "TikTok":
                    await download_tiktok(client, message.chat.id, url)
                else:
                    await download_video(client, message.chat.id, url)
            else:
                await message.reply_text(get_message("errors.invalid_link"))
            return

    # Обычный старт
    await message.reply_text(
        get_message("start", bot_username=client.me.username, owner_username=os.getenv("OWNER_USERNAME", "неизвестен"))
    )

async def help_handler(client: Client, message: Message):
    await message.reply_text(
        get_message("help",
                    bot_username=client.me.username,
                    owner_username=os.getenv("OWNER_USERNAME", "неизвестен"),
                    max_duration=int(MAX_DURATION/60),
                    max_playlist_items=os.getenv("MAX_PLAYLIST_ITEMS", 10))
    )

async def text_handler(client: Client, message: Message):
    original_text = message.text.strip()
    
    # 1. Сначала пытаемся нормализовать ссылку
    url = normalize_url(original_text)
    
    # 2. Проверяем, является ли это ссылкой ПОСЛЕ нормализации
    if not is_valid_url(url):
        # Если даже с https это не похоже на ссылку, значит это поиск песни
        await search_song_handler(client, message)
        return

    # 3. Работаем дальше с нормализованной ссылкой
    platform = get_platform(url)
    status_msg = await message.reply_text(get_message("downloads.searching", query=url))

    if platform == "Instagram":
        await download_instagram(client, message.chat.id, url, status_msg)
    elif platform == "TikTok":
        await download_tiktok(client, message.chat.id, url, status_msg)
    elif platform == "YouTube":
        await download_video(client, message.chat.id, url, status_msg)
    elif platform == "SoundCloud":
        await download_audio(client, message.chat.id, url, status_msg)
    elif platform in ["YouTubePlaylist", "SoundCloudPlaylist"]:
        # Для плейлистов статус сообщение передаем внутрь handle_playlist, если логика позволяет,
        # но в оригинале handle_playlist сам создает сообщение. Удалим наше.
        await status_msg.delete() 
        await handle_playlist(client, message, url, platform.replace("Playlist", ""))
    else:
        await download_video(client, message.chat.id, url, status_msg)

async def search_song_handler(client: Client, message: Message):
    query = message.text
    loading = await message.reply_text(get_message("downloads.searching", query=query))
    entries = await search_youtube(query)

    if not entries:
        await loading.edit_text(get_message("errors.no_results"))
        return

    buttons = []
    for entry in entries:
        video_id = entry.get('id')
        title = entry.get('title', 'Unknown')
        if len(title) > 50:
             title = title[:47] + "..."
        buttons.append([InlineKeyboardButton(f"🎵 {title}", callback_data=f"download_{video_id}")])

    await loading.edit_text("Выберите песню:", reply_markup=InlineKeyboardMarkup(buttons))

# --- Callback и Inline обработчики ---

async def button_callback(client: Client, query: CallbackQuery):
    if query.data.startswith('download_'):
        video_id = query.data.replace('download_', '')
        await query.answer()
        await query.message.edit_text(get_message("downloads.download_start"))
        await download_audio(client, query.message.chat.id, f"https://www.youtube.com/watch?v={video_id}")

async def inline_query_handler(client: Client, query: InlineQuery):
    text = query.query.strip()
    if not text:
        return

    # Инлайн режим тоже должен поддерживать нормализацию
    normalized_url = normalize_url(text)
    if is_valid_url(normalized_url):
        key = os.urandom(8).hex()
        save_deep_link(key, normalized_url)

        deep_link_url = f"https://t.me/{client.me.username}?start=vid_{key}"

        results = [
            InlineQueryResultArticle(
                title="📹 Скачать видео",
                description=normalized_url,
                input_message_content=InputTextMessageContent(
                    message_text=f"📹 Ссылка на видео:\n{normalized_url}"
                ),
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("▶️ Скачать", url=deep_link_url)
                ]])
            )
        ]
        await query.answer(results, cache_time=300)
        return

    # Поиск музыки
    entries = await search_youtube(text)
    results = []
    for entry in entries:
        video_id = entry.get('id')
        title = entry.get('title', 'Unknown')
        duration = entry.get('duration', 0)

        deep_link_url = f"https://t.me/{client.me.username}?start=dl_{video_id}"
        youtube_url = f"https://www.youtube.com/watch?v={video_id}"

        results.append(
            InlineQueryResultArticle(
                title=title,
                description=f"Длительность: {int(duration//60)}:{int(duration%60):02d}",
                input_message_content=InputTextMessageContent(
                    message_text=f"🎵 {title}\n🔗 {youtube_url}"
                ),
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("▶️ Скачать", url=deep_link_url)
                ]])
            )
        )
    await query.answer(results, cache_time=300)
