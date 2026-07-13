from typing import Dict, Any
import logging
from logger_config import init_logger
init_logger()
logger = logging.getLogger(__name__)

async def handle_message_logic(parsed: Dict[str, Any]) -> str:
    """
    Бизнес-логика: превращает текст в верхний регистр и отправляет ответ.
    """
    text = parsed.get("text", "")
    user_name = parsed.get("user_name", "пользователь")
    chat_id = parsed.get("chat_id")

    if not text:
        response_text = f"Привет, {user_name}! В твоём сообщении нет текста."
    else:
        response_text = text.upper() # функция, которая принимает текст пользователя и формирует ответ
    
    return response_text