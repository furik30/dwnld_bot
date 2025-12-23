import yaml
import os
from typing import Dict, Any
from utils.logger import logger
from config import MESSAGES_FILE

class MessageLoader:
    """Service for loading messages from YAML file"""

    def __init__(self, config_path: str = MESSAGES_FILE):
        self.config_path = config_path
        self._messages = None
        self._last_modified = 0
        self.load_messages()

    def load_messages(self) -> None:
        """Loads messages from YAML file"""
        try:
            if not os.path.exists(self.config_path):
                logger.error(f"Messages file not found: {self.config_path}")
                self._messages = {}
                return

            with open(self.config_path, 'r', encoding='utf-8') as file:
                self._messages = yaml.safe_load(file) or {}
                self._last_modified = os.path.getmtime(self.config_path)
                logger.info(f"Messages loaded from {self.config_path}")

        except Exception as e:
            logger.error(f"Error loading messages: {e}")
            self._messages = {}

    def _check_and_reload(self) -> None:
        """Checks for file changes and reloads if necessary"""
        try:
            if os.path.exists(self.config_path):
                current_modified = os.path.getmtime(self.config_path)
                if current_modified > self._last_modified:
                    logger.info("Messages file changed, reloading...")
                    self.load_messages()
        except Exception as e:
            logger.error(f"Error checking file changes: {e}")

    def get_message(self, key_path: str, **kwargs) -> str:
        """
        Retrieves a message by key path and formats it

        Args:
            key_path: Path to the message (e.g., "sections.profile.content")
            **kwargs: Parameters for formatting the message

        Returns:
            Formatted message string
        """
        try:
            # Check for file changes and reload if necessary
            self._check_and_reload()

            keys = key_path.split('.')
            message = self._messages

            for key in keys:
                if isinstance(message, dict) and key in message:
                    message = message[key]
                else:
                    logger.warning(f"Key not found: {key_path}")
                    return f"Message not found: {key_path}"

            if isinstance(message, str):
                return message.format(**kwargs) if kwargs else message
            else:
                logger.warning(f"Value at {key_path} is not a string")
                return str(message)

        except Exception as e:
            logger.error(f"Error getting message {key_path}: {e}")
            return f"Error loading message: {key_path}"

    def get_section(self, section_path: str) -> Dict[str, Any]:
        """
        Retrieves a whole section of messages

        Args:
            section_path: Path to the section (e.g., "sections.profile")

        Returns:
            Dictionary with section messages
        """
        try:
            keys = section_path.split('.')
            section = self._messages

            for key in keys:
                if isinstance(section, dict) and key in section:
                    section = section[key]
                else:
                    logger.warning(f"Section not found: {section_path}")
                    return {}

            return section if isinstance(section, dict) else {}

        except Exception as e:
            logger.error(f"Error getting section {section_path}: {e}")
            return {}

    def reload_messages(self) -> None:
        """Reloads messages from file"""
        logger.info("Reloading messages")
        self.load_messages()

# Create global instance of message loader
message_loader = MessageLoader()

# Helper functions for quick access
def get_message(key_path: str, **kwargs) -> str:
    """Get message by key"""
    return message_loader.get_message(key_path, **kwargs)

def get_section(section_path: str) -> Dict[str, Any]:
    """Get section of messages"""
    return message_loader.get_section(section_path)

def reload_messages() -> None:
    """Reload messages"""
    message_loader.reload_messages()
