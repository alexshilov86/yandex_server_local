# модуль для обработки входящих данных
import logging
from typing import Dict, Any
logger = logging.getLogger(__name__)

def parse_update(update: Dict[str, Any]) -> Dict[str, Any] | None:
    """Парсит один update из массива updates."""
    try:
        from_data = update.get("from", {})
        chat_data = update.get("chat", {})

        return {
            "user_id": from_data.get("id"),
            "user_login": from_data.get("login"),
            "user_name": from_data.get("display_name"),
            "chat_id": chat_data.get("id"),
            "chat_type": chat_data.get("type"),
            "text": update.get("text"),
            "timestamp": update.get("timestamp"),
            "message_id": update.get("message_id"),
            "payload_id": update.get("payload_id"),
            "update_id": update.get("update_id"),
        }
    except Exception as e:
        logger.error("Ошибка парсинга update: %s", e)
        return None