import os
from pyrogram import Client, filters
from pyrogram.types import (
    Message, CallbackQuery, InlineQuery,
    InlineQueryResultArticle, InputTextMessageContent,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from config import MAX_DURATION
from utils.common import get_platform, is_valid_url
from utils.storage import save_deep_link, get_deep_link
from utils.messages import get_message
from modules.youtube import search_youtube, download_audio, download_video, handle_playlist
from modules.instagram import download_instagram

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
                await message.reply_text(get_message("downloads.download_start"))
                # Определение платформы
                platform = get_platform(url)
                if platform == "Instagram":
                    await download_instagram(client, message.chat.id, url)
                else:
                    await download_video(client, message.chat.id, url)
            else:
                await message.reply_text(get_message("errors.invalid_link"))
            return

    # Обычный старт
    await message.reply_html(
        get_message("start", bot_username=client.me.username, owner_username=os.getenv("OWNER_USERNAME", "неизвестен"))
    )

async def help_handler(client: Client, message: Message):
    await message.reply_markdown(
        get_message("help",
                    bot_username=client.me.username,
                    owner_username=os.getenv("OWNER_USERNAME", "неизвестен"),
                    max_duration=int(MAX_DURATION/60),
                    max_playlist_items=os.getenv("MAX_PLAYLIST_ITEMS", 10))
    )

async def text_handler(client: Client, message: Message):
    text = message.text

    if not is_valid_url(text):
        # Если не ссылка, считаем поисковым запросом
        await search_song_handler(client, message)
        return

    platform = get_platform(text)

    if platform == "Instagram":
        await download_instagram(client, message.chat.id, text, await message.reply_text(get_message("downloads.searching", query=text)))
    elif platform in ["YouTube", "TikTok"]:
        await download_video(client, message.chat.id, text, await message.reply_text(get_message("downloads.searching", query=text)))
    elif platform == "SoundCloud":
        await download_audio(client, message.chat.id, text, await message.reply_text(get_message("downloads.searching", query=text)))
    elif platform in ["YouTubePlaylist", "SoundCloudPlaylist"]:
        await handle_playlist(client, message, text, platform.replace("Playlist", ""))
    else:
        # Попытка скачать видео для общих URL
        await download_video(client, message.chat.id, text, await message.reply_text(get_message("downloads.searching", query=text)))

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

    # Проверка, является ли текст ссылкой
    if is_valid_url(text):
        # Генерация deep link для видео
        key = os.urandom(8).hex()
        save_deep_link(key, text)

        deep_link_url = f"https://t.me/{client.me.username}?start=vid_{key}"

        results = [
            InlineQueryResultArticle(
                title="📹 Скачать видео",
                description=text,
                input_message_content=InputTextMessageContent(
                    message_text=f"📹 Ссылка на видео:\n{text}"
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
