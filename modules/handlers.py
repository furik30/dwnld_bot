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

# --- Command Handlers ---

async def start_handler(client: Client, message: Message):
    # Check for deep link payload
    if len(message.command) > 1:
        payload = message.command[1]

        # Audio download by ID (dl_ID)
        if payload.startswith('dl_'):
            video_id = payload.replace('dl_', '')
            url = f"https://www.youtube.com/watch?v={video_id}"
            await message.reply_text(get_message("downloads.download_start"))
            await download_audio(client, message.chat.id, url)
            return

        # Video download by key (vid_KEY)
        elif payload.startswith('vid_'):
            key = payload.replace('vid_', '')
            url = get_deep_link(key)

            if url:
                await message.reply_text(get_message("downloads.download_start"))
                # Detect platform
                platform = get_platform(url)
                if platform == "Instagram":
                    await download_instagram(client, message.chat.id, url)
                else:
                    await download_video(client, message.chat.id, url)
            else:
                await message.reply_text(get_message("errors.invalid_link"))
            return

    # Normal start
    await message.reply_html(
        get_message("start", bot_username=client.me.username, owner_username=os.getenv("OWNER_USERNAME", "unknown"))
    )

async def help_handler(client: Client, message: Message):
    await message.reply_markdown(
        get_message("help",
                    bot_username=client.me.username,
                    owner_username=os.getenv("OWNER_USERNAME", "unknown"),
                    max_duration=int(MAX_DURATION/60),
                    max_playlist_items=os.getenv("MAX_PLAYLIST_ITEMS", 10))
    )

async def text_handler(client: Client, message: Message):
    text = message.text

    if not is_valid_url(text):
        # Treat as search query
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
        # Fallback to simple audio download if URL provided but unknown platform, or error?
        # Let's try to download video for generic URLs if supported by yt-dlp
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

    await loading.edit_text("Select a song:", reply_markup=InlineKeyboardMarkup(buttons))

# --- Callback & Inline Handlers ---

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

    # Check if it is a link
    if is_valid_url(text):
        # Generate deep link for video
        key = os.urandom(8).hex()
        save_deep_link(key, text)

        deep_link_url = f"https://t.me/{client.me.username}?start=vid_{key}"

        results = [
            InlineQueryResultArticle(
                title="📹 Download Video",
                description=text,
                input_message_content=InputTextMessageContent(
                    message_text=f"📹 Video Link:\n{text}"
                ),
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("▶️ Download", url=deep_link_url)
                ]])
            )
        ]
        await query.answer(results, cache_time=300)
        return

    # Search music
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
                description=f"Duration: {int(duration//60)}:{int(duration%60):02d}",
                input_message_content=InputTextMessageContent(
                    message_text=f"🎵 {title}\n🔗 {youtube_url}"
                ),
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("▶️ Download", url=deep_link_url)
                ]])
            )
        )

    await query.answer(results, cache_time=300)
