from typing import Dict, Any
import logging
from logger_config import init_logger
from send_message_to_bot import send_message_to_chat

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
    # Отправляем ответ в чат
    if chat_id:
        success = await send_message_to_chat(chat_id, response_text)
        if not success:
            # Даже если отправка не удалась, возвращаем текст как «результат логики»
            logger.warning("Не удалось отправить ответ в чат %s, но логика выполнена", chat_id)
    else:
        logger.warning("chat_id отсутствует, отправка невозможна")    
    
    return response_text