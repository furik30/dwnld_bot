import os
import logging
import asyncio
import functools
import yt_dlp
import instaloader
import glob
import shutil
from telegram.error import BadRequest
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler, InlineQueryHandler
from telegram.constants import ChatAction, ParseMode
import config

# --- НАСТРОЙКИ ---
# Все настройки теперь загружаются из config.py, который читает .env файл
TELEGRAM_TOKEN = config.TELEGRAM_TOKEN
OWNER_USERNAME = config.OWNER_USERNAME
MAX_DURATION = config.MAX_DURATION
MAX_PLAYLIST_ITEMS = config.MAX_PLAYLIST_ITEMS
INSTAGRAM_USERNAME = config.INSTAGRAM_USERNAME
INSTAGRAM_SESSION_FILE = config.INSTAGRAM_SESSION_FILE
COOKIES_FILE = config.COOKIES_FILE

# --- ЛОГИРОВАНИЕ ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- КЛАССЫ ИСКЛЮЧЕНИЙ ---
class DurationLimitError(Exception):
    pass

# --- ОСНОВНЫЕ ФУНКЦИИ ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает команду /start, в том числе и с deep link параметрами."""
    user = update.effective_user
    
    # Проверяем, есть ли у нас аргументы (payload из deep link)
    if context.args:
        payload = context.args[0]
        logger.info(f"Получен deep link с payload: {payload} от пользователя {user.id}")
        
        # Обработка скачивания аудио по ID
        if payload.startswith('dl_'):
            video_id = payload.replace('dl_', '')
            url = f"https://www.youtube.com/watch?v={video_id}"
            await update.message.reply_text("✅ Отлично! Начинаю загрузку вашего трека...")
            await download_and_send_audio(update, context, url)
            return

        # Обработка скачивания видео по ссылке (через ключ)
        elif payload.startswith('vid_'):
            key = payload.replace('vid_', '')
            # Извлекаем и удаляем URL из кэша, чтобы ссылка была одноразовой
            url = context.bot_data.pop(key, None)
            
            if url:
                await update.message.reply_text("✅ Понял! Начинаю загрузку видео...")
                await download_and_send_video(update, context, url)
            else:
                await update.message.reply_text("❌ Эта ссылка для скачивания устарела. Пожалуйста, попробуйте выполнить поиск снова.")
            return

    # Если аргументов нет — показываем обычное приветствие
    keyboard = [["ℹ️ Помощь"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    start_text = (
        "🎶 <b>Привет! Я бот для скачивания музыки и видео.</b>\n\n"
        "<b>Как пользоваться:</b>\n"
        "1.  Отправьте мне название песни для поиска.\n"
        "2.  Или отправьте ссылку на видео из TikTok, Instagram Reels, или плейлист с YouTube/SoundCloud.\n\n"
        "<b>Inline-режим:</b>\n"
        "Напишите в любом чате мое имя (<code>@{context.bot.username}</code>) и ваш запрос для поиска или ссылку.\n\n"
        f"Владелец бота: {OWNER_USERNAME}"
    )
    await update.message.reply_html(start_text.format(context=context), reply_markup=reply_markup)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет справочное сообщение."""
    help_text = (
        "**Как пользоваться ботом:**\n\n"
        "🎵 **Поиск и скачивание музыки:**\n"
        "   - Просто отправьте мне название песни (например, \"Blinding Lights\").\n"
        "   - Бот предложит 5 вариантов с кнопками для скачивания.\n\n"
        "📹 **Скачивание видео и плейлистов:**\n"
        "   - Отправьте ссылку на видео из TikTok, Instagram Reels.\n"
        "   - Отправьте ссылку на плейлист из YouTube или SoundCloud.\n\n"
        "🤖 **Inline-режим:**\n"
        "   - В любом чате введите `@{context.bot.username}` и через пробел название песни или ссылку.\n"
        "   - Нажмите на результат, и вы перейдете ко мне в чат для скачивания файла.\n\n"
        "**Ограничения:**\n"
        f"- Максимальная длительность одного трека/видео: **{int(MAX_DURATION / 60)} минут**.\n"
        f"- Максимальное количество треков в плейлисте: **{MAX_PLAYLIST_ITEMS}**.\n\n"
        f"Владелец бота: {OWNER_USERNAME}"
    )
    await update.message.reply_markdown(help_text.format(context=context))


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает текстовые сообщения: ссылки или поисковые запросы."""
    text = update.message.text
    if "youtube.com/playlist" in text:
        await handle_playlist(update, context, text, "YouTube")
    elif "soundcloud.com" in text and "/sets/" in text:
        await handle_playlist(update, context, text, "SoundCloud")
    elif any(domain in text for domain in ["tiktok.com", "instagram.com", "soundcloud.com", "youtube.com"]):
        await handle_link(update, context, text)
    else:
        await search_song(update, context)

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE, url: str) -> None:
    """Обрабатывает одиночные ссылки на видео/аудио."""
    if "instagram.com/reels/" in url or "instagram.com/reel/" in url:
        await download_instagram_reel(update, context, url)
    elif "tiktok.com" in url or "youtube.com" in url:
        await download_and_send_video(update, context, url)
    elif "soundcloud.com" in url:
        await download_and_send_audio(update, context, url)
    else:
        await update.message.reply_text("Неизвестный тип ссылки.")

async def search_song(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Ищет песню по текстовому запросу и предлагает варианты с кнопками (для личного чата)."""
    query = update.message.text
    loading_message = await update.message.reply_text(f"🔎 Ищу \"{query}\"...")
    
    try:
        ydl_opts = {'quiet': True, 'extract_flat': True, 'force_generic_extractor': True, 'age_limit': 99}
        if os.path.exists(COOKIES_FILE):
            ydl_opts['cookiefile'] = COOKIES_FILE
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            search_result = await run_blocking(ydl.extract_info, f"ytsearch5:{query}", download=False)

        if not search_result or not search_result.get('entries'):
            await loading_message.edit_text("По вашему запросу ничего не найдено.")
            return

        keyboard = []
        for entry in search_result['entries']:
            video_id, title = entry.get('id'), entry.get('title', 'Без названия')
            if video_id:
                button_text = title if len(title) < 50 else title[:47] + "..."
                keyboard.append([InlineKeyboardButton(f"🎵 {button_text}", callback_data=f"download_{video_id}")])
        
        if not keyboard:
            await loading_message.edit_text("Не удалось найти подходящих треков.")
            return

        await loading_message.edit_text('Выберите песню для скачивания:', reply_markup=InlineKeyboardMarkup(keyboard))

    except Exception as e:
        logger.error(f"Ошибка при поиске песни: {e}", exc_info=True)
        await loading_message.edit_text("Произошла ошибка при поиске.")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает нажатия на inline-кнопки (только для личного чата)."""
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith('download_'):
        loading_message = None
        try:
            video_id = query.data.replace('download_', '')
            loading_message = await query.edit_message_text(text="✅ Выбрано. Начинаю загрузку...")
            await download_and_send_audio(update, context, f"https://www.youtube.com/watch?v={video_id}", loading_message)
        except DurationLimitError as e:
            if loading_message: await query.edit_message_text(text=f"❌ {e}")
        except Exception as e:
            logger.error(f"Ошибка в callback: {e}", exc_info=True)
            if loading_message: await query.edit_message_text(text="❌ Произошла ошибка при начале загрузки.")


async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает inline-запросы, создавая deep link ссылки для скачивания."""
    query = update.inline_query.query.strip()
    
    if not query:
        return

    # --- Обработка ссылок ---
    if any(domain in query.lower() for domain in ['tiktok.com', 'instagram.com', 'youtube.com']):
        try:
            # Генерируем короткий, безопасный ключ для URL
            key = os.urandom(8).hex()
            # Сохраняем URL в кэше бота. Ключ неявно истечет при перезапуске.
            context.bot_data[key] = query
            
            deep_link_url = f"https://t.me/{context.bot.username}?start=vid_{key}"
            
            results = [
                InlineQueryResultArticle(
                    id="video_download",
                    title="📹 Скачать видео",
                    description=query, # Показываем ссылку в описании
                    input_message_content=InputTextMessageContent(
                        message_text=f"📹 Видео для скачивания:\n{query}"
                    ),
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("▶️ Перейти к скачиванию", url=deep_link_url)
                    ]])
                )
            ]
            await update.inline_query.answer(results, cache_time=86400)
            return
        except Exception as e:
            logger.error(f"Ошибка в inline (обработка ссылки): {e}", exc_info=True)
            return
    
    # --- Поиск музыки ---
    try:
        ydl_opts = {'quiet': True, 'extract_flat': True, 'force_generic_extractor': True, 'age_limit': 99}
        if os.path.exists(COOKIES_FILE):
            ydl_opts['cookiefile'] = COOKIES_FILE
            
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            search_result = await run_blocking(ydl.extract_info, f"ytsearch5:{query}", download=False)

        if not search_result or not search_result.get('entries'):
            return

        results = []
        for i, entry in enumerate(search_result['entries'][:5]):
            video_id = entry.get('id')
            title = entry.get('title', 'Без названия')
            duration = entry.get('duration', 0)
            
            if video_id:
                deep_link_url = f"https://t.me/{context.bot.username}?start=dl_{video_id}"
                duration_text = f"⏱ Длительность: {int(duration//60)}:{int(duration%60):02d}" if duration else "Неизвестна"
                youtube_url = f"https://www.youtube.com/watch?v={video_id}"
                results.append(
                    InlineQueryResultArticle(
                        id=str(i),
                        title=title[:64],
                        description=f"{duration_text}\n{youtube_url}",
                        input_message_content=InputTextMessageContent(
                             message_text=f"🎵 {title} \n {duration_text}\n🔗 {youtube_url}",
                             parse_mode=ParseMode.HTML
                        ),
                        reply_markup=InlineKeyboardMarkup([[
                            InlineKeyboardButton("▶️ Перейти к скачиванию", url=deep_link_url)
                        ]])
                    )
                )
        
        # Устанавливаем время кэширования на 1 день (в секундах)
        await update.inline_query.answer(results, cache_time=86400)
        
    except BadRequest as e:
        if "Query is too old" in str(e):
            logger.warning("Не удалось ответить на inline-запрос (слишком старый), бот был занят.")
        else:
            logger.error(f"Ошибка BadRequest в inline (поиск музыки): {e}", exc_info=True)
    except Exception as e:
        logger.error(f"Общая ошибка в inline (поиск музыки): {e}", exc_info=True)

# --- ФУНКЦИИ СКАЧИВАНИЯ ---

async def download_and_send_video(update: Update, context: ContextTypes.DEFAULT_TYPE, url: str, loading_message=None):
    """Скачивает видео по URL и отправляет его в текущий чат."""
    chat_id = update.effective_chat.id
    if loading_message is None:
        loading_message = await context.bot.send_message(chat_id, "⏳ Получаю информацию о видео...")

    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.UPLOAD_VIDEO)

    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': os.path.join('downloads', '%(id)s.%(ext)s'),
        'noplaylist': True, 'quiet': True, 'age_limit': 99,
    }
    if os.path.exists(COOKIES_FILE):
        ydl_opts['cookiefile'] = COOKIES_FILE

    filename = None
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = await run_blocking(ydl.extract_info, url, download=False)
            if info.get('duration', 0) > MAX_DURATION:
                raise DurationLimitError(f"Видео слишком длинное ({int(info.get('duration', 0))}с > {MAX_DURATION}с).")
            
            await loading_message.edit_text("🚀 Начинаю загрузку видео...")
            await run_blocking(ydl.download, [url])
            filename = ydl.prepare_filename(info)
            
            await loading_message.edit_text("📤 Отправляю видео...")
            with open(filename, 'rb') as video_file:
                await context.bot.send_video(chat_id=chat_id, video=video_file, caption=f"Скачано с помощью @{context.bot.username}")
            await loading_message.delete()
                
    except DurationLimitError as e:
        await loading_message.edit_text(f"❌ Ошибка: {e}")
    except Exception as e:
        logger.error(f"Ошибка при скачивании/отправке видео {url}: {e}", exc_info=True)
        await loading_message.edit_text("❌ Произошла ошибка при скачивании или отправке видео.")
    finally:
        if filename and os.path.exists(filename):
            os.remove(filename)

async def download_and_send_audio(update: Update, context: ContextTypes.DEFAULT_TYPE, url: str, loading_message=None):
    """Скачивает аудио по URL, конвертирует в MP3 и отправляет в текущий чат."""
    chat_id = update.effective_chat.id
    if loading_message is None:
        loading_message = await context.bot.send_message(chat_id, "⏳ Получаю информацию о треке...")
    
    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.UPLOAD_DOCUMENT)
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3'}],
        'outtmpl': os.path.join('downloads', '%(title)s.%(ext)s'),
        'noplaylist': True, 'quiet': True, 'age_limit': 99,
    }
    if os.path.exists(COOKIES_FILE):
        ydl_opts['cookiefile'] = COOKIES_FILE

    filename = None
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = await run_blocking(ydl.extract_info, url, download=False)
            entry = info.get('entries', [info])[0]
            
            if entry.get('duration', 0) > MAX_DURATION:
                raise DurationLimitError(f"Трек слишком длинный ({int(entry.get('duration', 0))}с > {MAX_DURATION}с).")

            await loading_message.edit_text("🚀 Начинаю загрузку трека...")
            await run_blocking(ydl.download, [url])
            filename = ydl.prepare_filename(entry).rsplit('.', 1)[0] + '.mp3'
            
            await loading_message.edit_text("📤 Отправляю аудио...")
            with open(filename, 'rb') as audio_file:
                await context.bot.send_audio(
                    chat_id=chat_id,
                    audio=audio_file,
                    caption=f"Скачано с помощью @{context.bot.username}",
                    title=entry.get('track') or entry.get('title') or "Без названия",
                    performer=entry.get('artist') or entry.get('uploader') or "Неизвестен",
                    duration=int(entry.get('duration', 0))
                )
            await loading_message.delete()
            
    except DurationLimitError as e:
        await loading_message.edit_text(f"❌ Ошибка: {e}")
    except Exception as e:
        logger.error(f"Ошибка при скачивании/отправке аудио {url}: {e}", exc_info=True)
        await loading_message.edit_text("❌ Произошла ошибка при скачивании или отправке аудио.")
    finally:
        if filename and os.path.exists(filename):
            os.remove(filename)


async def handle_playlist(update: Update, context: ContextTypes.DEFAULT_TYPE, url: str, platform: str):
    loading_message = await update.message.reply_text(f"🔎 Анализирую плейлист из {platform}...")
    try:
        ydl_opts = {
            'quiet': True, 
            'extract_flat': True, 
            'playlistend': MAX_PLAYLIST_ITEMS, 
            'age_limit': 99
        }
        # Добавляем cookies если файл существует
        if os.path.exists(COOKIES_FILE):
            ydl_opts['cookiefile'] = COOKIES_FILE
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            playlist_info = await run_blocking(ydl.extract_info, url, download=False)
        
        entries = playlist_info.get('entries', [])
        if not entries:
            await loading_message.edit_text("Не удалось найти треки в этом плейлисте.")
            return

        await loading_message.edit_text(f"✅ Найден плейлист из {len(entries)} треков. Начинаю загрузку...")

        for i, entry in enumerate(entries):
            video_url = entry.get('url')
            if platform == "YouTube":
                video_url = f"https://www.youtube.com/watch?v={entry['id']}"
            
            title = entry.get('title', 'Без названия')
            status_message = await update.message.reply_text(f"Скачиваю трек {i+1}/{len(entries)}: {title}")
            try:
                await download_and_send_audio(update, context, video_url, status_message)
            except DurationLimitError as e:
                await status_message.edit_text(f"⚠️ Трек '{title}' пропущен: он длиннее {int(MAX_DURATION/60)} минут.")
            except Exception as e:
                logger.error(f"Ошибка при скачивании трека {video_url} из плейлиста: {e}")
                await status_message.edit_text(f"❌ Не удалось скачать трек '{title}'.")

    except Exception as e:
        logger.error(f"Ошибка при обработке плейлиста {url}: {e}", exc_info=True)
        await loading_message.edit_text("❌ Произошла ошибка при обработке плейлиста.")


async def download_instagram_reel(update: Update, context: ContextTypes.DEFAULT_TYPE, url: str, loading_message=None):
    reply_target = update.message if update.message else None
    if not reply_target:
        logger.error("Не удалось определить цель для ответа в download_instagram_reel.")
        return

    L = instaloader.Instaloader(
        download_pictures=False, download_video_thumbnails=False, download_geotags=False,
        download_comments=False, save_metadata=False, compress_json=False,
        dirname_pattern=os.path.join('downloads', '{profile}'),
        sleep=True, request_timeout=30, max_connection_attempts=3
    )
    target_profile = None
    try:
        if INSTAGRAM_SESSION_FILE and os.path.exists(INSTAGRAM_SESSION_FILE):
            L.load_session_from_file(INSTAGRAM_USERNAME, INSTAGRAM_SESSION_FILE)
        
        shortcode = url.split('/')[-2]
        post = await run_blocking(instaloader.Post.from_shortcode, L.context, shortcode)
        
        if post.video_duration > MAX_DURATION:
            raise DurationLimitError(f"Видео слишком длинное ({int(post.video_duration)}с > {MAX_DURATION}с).")

        target_profile = post.owner_username
        await run_blocking(L.download_post, post, target=target_profile)

        download_dir = os.path.join('downloads', target_profile)
        video_files = glob.glob(os.path.join(download_dir, '*.mp4'))
        if not video_files:
            raise Exception("Не удалось найти скачанный видеофайл.")
        
        await reply_target.reply_video(video=open(video_files[0], 'rb'), caption=f"Скачано с помощью @{context.bot.username}")
        await loading_message.delete()

    except instaloader.exceptions.ConnectionException as e:
        await loading_message.edit_text("❌ Instagram временно ограничил доступ. Попробуйте через несколько минут.")
    except Exception as e:
        logger.error(f"Ошибка instaloader при обработке {url}: {e}", exc_info=True)
        await loading_message.edit_text("❌ Произошла ошибка при скачивании из Instagram.")
    finally:
        if target_profile and os.path.exists(os.path.join('downloads', target_profile)):
            shutil.rmtree(os.path.join('downloads', target_profile))



async def run_blocking(func, *args, **kwargs):
    """Запускает блокирующую функцию в отдельном потоке."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, functools.partial(func, *args, **kwargs))

# --- ЗАПУСК БОТА ---

def main() -> None:
    """Главная функция для запуска бота."""
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.Regex('^ℹ️ Помощь$'), help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(button_callback)) # Для кнопок в ЛС
    application.add_handler(InlineQueryHandler(inline_query))      # Для inline-режима
    
    logger.info("Бот запущен!")
    application.run_polling()

if __name__ == '__main__':
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    main()