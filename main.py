import os
import logging
from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler, CallbackQueryHandler, InlineQueryHandler
from config import TELEGRAM_TOKEN, API_ID, API_HASH
from utils.logger import logger
from modules.handlers import (
    start_handler, help_handler, text_handler,
    button_callback, inline_query_handler
)
from modules.admin import admin_command, admin_callback

def main():
    if not TELEGRAM_TOKEN:
        logger.error("TELEGRAM_TOKEN is not set.")
        return

    # Initialize Client
    # We use a persistent session in 'data/' folder if needed, or just memory if using Bot Token only
    # Pyrogram creates a .session file. Let's put it in data/
    if not os.path.exists('data'):
        os.makedirs('data')

    app = Client(
        "data/bot",
        api_id=API_ID,
        api_hash=API_HASH,
        bot_token=TELEGRAM_TOKEN
    )

    # Register Handlers
    app.add_handler(MessageHandler(start_handler, filters.command("start")))
    app.add_handler(MessageHandler(help_handler, filters.command("help")))

    # Admin Handlers
    app.add_handler(MessageHandler(admin_command, filters.command(["admin", "logs"])))
    app.add_handler(CallbackQueryHandler(admin_callback, filters.regex("^admin_")))

    # User Handlers
    app.add_handler(MessageHandler(text_handler, filters.text & ~filters.command("start") & ~filters.command("help")))
    app.add_handler(CallbackQueryHandler(button_callback, filters.regex("^download_")))
    app.add_handler(InlineQueryHandler(inline_query_handler))

    logger.info("Starting bot...")
    app.run()

if __name__ == "__main__":
    main()
