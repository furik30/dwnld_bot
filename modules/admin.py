import os
import psutil
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from config import OWNER_ID, LOGS_DIR
from utils.messages import get_message

async def admin_command(client: Client, message: Message):
    if message.from_user.id != OWNER_ID:
        return

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📜 Логи", callback_data="admin_logs"),
         InlineKeyboardButton("📊 Статус", callback_data="admin_status")],
        [InlineKeyboardButton("❌ Ошибки", callback_data="admin_errors")]
    ])

    await message.reply_text(get_message("admin.panel"), reply_markup=keyboard)

async def admin_callback(client: Client, callback_query: CallbackQuery):
    if callback_query.from_user.id != OWNER_ID:
        await callback_query.answer(get_message("admin.access_denied"), show_alert=True)
        return

    data = callback_query.data

    if data == "admin_logs":
        await send_logs(callback_query, error_only=False)
    elif data == "admin_errors":
        await send_logs(callback_query, error_only=True)
    elif data == "admin_status":
        await send_status(callback_query)

async def send_logs(query: CallbackQuery, error_only: bool):
    log_file = os.path.join(LOGS_DIR, "bot.log")
    if not os.path.exists(log_file):
        await query.answer(get_message("admin.logs_empty"), show_alert=True)
        return

    lines = []
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            # Читаем все строки
            all_lines = f.readlines()

            # Фильтруем (теперь логи - это просто текст)
            for line in reversed(all_lines): # Читаем с конца
                if len(lines) >= 20:
                    break
                if error_only:
                     if 'ERROR' in line or 'CRITICAL' in line:
                         lines.append(line)
                else:
                    lines.append(line)
    except Exception as e:
        await query.message.edit_text(f"Ошибка чтения логов: {e}")
        return

    if not lines:
        await query.answer(get_message("admin.logs_empty"), show_alert=True)
        return

    # Возвращаем порядок (сверху - старые, снизу - новые, или наоборот? Обычно логи читают сверху вниз)
    # Но мы читали с конца. Так что reversed(lines) вернет хронологический порядок последних N строк.
    text = get_message("admin.logs_header") + "".join(reversed(lines))

    # Лимит сообщения Telegram 4096 символов.
    if len(text) > 4000:
        text = text[-4000:]

    await query.message.edit_text(f"```\n{text}\n```", parse_mode=None)

async def send_status(query: CallbackQuery):
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    memory_usage = round(mem_info.rss / 1024 / 1024, 2)
    threads = process.num_threads()

    status_text = get_message(
        "admin.status",
        threads=threads,
        memory_usage=memory_usage
    )

    await query.message.edit_text(status_text)
