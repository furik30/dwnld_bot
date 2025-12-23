import logging
import os
from logging.handlers import RotatingFileHandler
from config import LOGS_DIR

def setup_logger(name=__name__):
    """Настраивает и возвращает логгер с записью в файл и консоль."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Предотвращаем дублирование обработчиков
    if logger.hasHandlers():
        return logger

    # Форматтер
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Консольный обработчик
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Файловый обработчик
    log_file = os.path.join(LOGS_DIR, "bot.log")
    file_handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

# Глобальный экземпляр логгера для удобного импорта
logger = setup_logger("downloader_bot")
