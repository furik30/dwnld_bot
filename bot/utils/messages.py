import yaml
import os
from typing import Dict, Any
from utils.logger import logger
from config import MESSAGES_FILE

class MessageLoader:
    """Сервис для загрузки сообщений из YAML файла"""

    def __init__(self, config_path: str = MESSAGES_FILE):
        self.config_path = config_path
        self._messages = None
        self._last_modified = 0
        self.load_messages()

    def load_messages(self) -> None:
        """Загружает сообщения из YAML файла"""
        try:
            if not os.path.exists(self.config_path):
                logger.error(f"Файл сообщений не найден: {self.config_path}")
                self._messages = {}
                return

            with open(self.config_path, 'r', encoding='utf-8') as file:
                self._messages = yaml.safe_load(file) or {}
                self._last_modified = os.path.getmtime(self.config_path)
                logger.info(f"Сообщения загружены из {self.config_path}")

        except Exception as e:
            logger.error(f"Ошибка при загрузке сообщений: {e}")
            self._messages = {}

    def _check_and_reload(self) -> None:
        """Проверяет изменения файла и перезагружает при необходимости"""
        try:
            if os.path.exists(self.config_path):
                current_modified = os.path.getmtime(self.config_path)
                if current_modified > self._last_modified:
                    logger.info("Обнаружены изменения в файле сообщений, перезагрузка...")
                    self.load_messages()
        except Exception as e:
            logger.error(f"Ошибка при проверке изменений файла: {e}")

    def get_message(self, key_path: str, **kwargs) -> str:
        """
        Получает сообщение по пути ключа и форматирует его

        Args:
            key_path: Путь к сообщению (например, "sections.profile.content")
            **kwargs: Параметры для форматирования сообщения

        Returns:
            Отформатированное сообщение
        """
        try:
            # Проверяем время изменения файла и перезагружаем при необходимости
            self._check_and_reload()

            keys = key_path.split('.')
            message = self._messages

            for key in keys:
                if isinstance(message, dict) and key in message:
                    message = message[key]
                else:
                    logger.warning(f"Ключ не найден: {key_path}")
                    return f"Сообщение не найдено: {key_path}"

            if isinstance(message, str):
                return message.format(**kwargs) if kwargs else message
            else:
                logger.warning(f"Значение по ключу {key_path} не является строкой")
                return str(message)

        except Exception as e:
            logger.error(f"Ошибка при получении сообщения {key_path}: {e}")
            return f"Ошибка загрузки сообщения: {key_path}"

    def get_section(self, section_path: str) -> Dict[str, Any]:
        """
        Получает целую секцию сообщений

        Args:
            section_path: Путь к секции (например, "sections.profile")

        Returns:
            Словарь с сообщениями секции
        """
        try:
            keys = section_path.split('.')
            section = self._messages

            for key in keys:
                if isinstance(section, dict) and key in section:
                    section = section[key]
                else:
                    logger.warning(f"Секция не найдена: {section_path}")
                    return {}

            return section if isinstance(section, dict) else {}

        except Exception as e:
            logger.error(f"Ошибка при получении секции {section_path}: {e}")
            return {}

    def reload_messages(self) -> None:
        """Перезагружает сообщения из файла"""
        logger.info("Перезагрузка сообщений")
        self.load_messages()

# Создаем глобальный экземпляр загрузчика сообщений
message_loader = MessageLoader()

# Удобные функции для быстрого доступа к сообщениям
def get_message(key_path: str, **kwargs) -> str:
    """Получить сообщение по ключу"""
    return message_loader.get_message(key_path, **kwargs)

def get_section(section_path: str) -> Dict[str, Any]:
    """Получить секцию сообщений"""
    return message_loader.get_section(section_path)

def reload_messages() -> None:
    """Перезагрузить сообщения"""
    message_loader.reload_messages()
