import os
import psutil
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from config import OWNER_ID, LOGS_DIR
from utils.messages import get_message

async def admin_command(client: Client, message: Message):
    if message.from_user.id != OWNER_ID:
        # Silently ignore or say access denied? User asked for "Check if user.id == OWNER_ID"
        return

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📜 Logs", callback_data="admin_logs"),
         InlineKeyboardButton("📊 Status", callback_data="admin_status")],
        [InlineKeyboardButton("❌ Errors", callback_data="admin_errors")]
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
            # Read all lines
            all_lines = f.readlines()

            # Filter if needed (naive implementation since logs are JSON)
            # If error_only, we check if line contains "ERROR" or "CRITICAL"
            for line in reversed(all_lines): # Read from end
                if len(lines) >= 20:
                    break
                if error_only:
                     if '"level": "ERROR"' in line or '"level": "CRITICAL"' in line:
                         lines.append(line)
                else:
                    lines.append(line)
    except Exception as e:
        await query.message.edit_text(f"Error reading logs: {e}")
        return

    if not lines:
        await query.answer(get_message("admin.logs_empty"), show_alert=True)
        return

    # Reverse back to normal order
    text = get_message("admin.logs_header") + "".join(reversed(lines))

    # Telegram message limit is 4096 chars. Truncate if needed.
    if len(text) > 4000:
        text = text[-4000:]

    # Escape HTML/Markdown if necessary or send as monospaced
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
