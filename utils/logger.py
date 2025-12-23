import logging
import json
import os
from logging.handlers import RotatingFileHandler
from config import LOGS_DIR

def setup_logger(name=__name__):
    """Configures and returns a logger with JSON formatting and file rotation."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Prevent adding handlers multiple times if logger is already configured
    if logger.hasHandlers():
        return logger

    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File Handler (JSON)
    log_file = os.path.join(LOGS_DIR, "bot.log")
    file_handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5)
    file_handler.setLevel(logging.INFO)

    class JsonFormatter(logging.Formatter):
        def format(self, record):
            log_record = {
                "timestamp": self.formatTime(record, self.datefmt),
                "level": record.levelname,
                "name": record.name,
                "message": record.getMessage()
            }
            if record.exc_info:
                log_record["exception"] = self.formatException(record.exc_info)
            return json.dumps(log_record)

    file_handler.setFormatter(JsonFormatter())
    logger.addHandler(file_handler)

    return logger

# Global logger instance for easy import
logger = setup_logger("downloader_bot")
