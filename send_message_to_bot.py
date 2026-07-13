import os
import logging
import aiohttp
import asyncio
from logger_config import init_logger
from dotenv import load_dotenv

load_dotenv()
init_logger()
logger = logging.getLogger(__name__)
BOT_TOKEN = os.getenv("YANDEX_BOT_TOKEN", "")
SEND_MESSAGE_URL = "https://botapi.messenger.yandex.net/bot/v1/messages/sendText/"  # <-- замени на реальный URL из документации

async def send_message_to_chat(chat_id: str, text: str) -> bool:
    """
    Отправляет сообщение в чат через API Яндекс Мессенджера.
    Использует заголовки строго по документации:
      Authorization: OAuth <токен>
      Content-Type: application/json
    """
    if not chat_id or not text:
        logger.warning("Некорректные параметры для отправки: chat_id=%s, text=%s", chat_id, text)
        return False

    if not BOT_TOKEN:
        logger.error("КРИТИЧЕСКАЯ ОШИБКА: YANDEX_BOT_TOKEN не найден! Проверьте .env и наличие load_dotenv() в server.py.")
        return False

    payload = {
        "chat_id": chat_id,
        "text": text,
    }

    # Строго как в curl примере
    headers = {
        "Authorization": f"OAuth {BOT_TOKEN}",
        "Content-Type": "application/json",
    }

    logger.info("Отправка сообщения: chat_id=%s", chat_id)

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                SEND_MESSAGE_URL, 
                json=payload, 
                headers=headers, 
                timeout=10
            ) as resp:
                
                logger.info("Статус ответа API: %d", resp.status)
                
                if resp.status == 200:
                    logger.info("Сообщение успешно отправлено.")
                    return True
                elif resp.status == 401:
                    logger.error("Ошибка 401: Неверный токен. Проверьте YANDEX_BOT_TOKEN в .env")
                    return False
                elif resp.status == 403:
                    logger.error("Ошибка 403: Доступ запрещён. Возможно, у бота нет прав на отправку.")
                    return False
                else:
                    body = await resp.text()
                    logger.error("Ошибка отправки (status=%d): %s", resp.status, body)
                    return False
                    
    except asyncio.TimeoutError:
        logger.error("Таймаут при отправке сообщения.")
        return False
    except Exception as e:
        logger.exception("Исключение при отправке сообщения: %s", e)
        return False
