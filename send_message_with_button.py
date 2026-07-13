import requests
import json
import logging
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from logger_config import init_logger
import os
import httpx
import asyncio

load_dotenv()
init_logger()
logger = logging.getLogger(__name__)
BOT_TOKEN = os.getenv("YANDEX_BOT_TOKEN", "")
SEND_MESSAGE_URL = "https://botapi.messenger.yandex.net/bot/v1/messages/sendText/"

async def send_message_to_chat(chat_id: str, text: str, keyboard=None) -> bool:
    TOKEN = os.getenv("YANDEX_BOT_TOKEN")
    if not TOKEN:
        logger.error("YANDEX_BOT_TOKEN не задан в .env")
        return False

    url = SEND_MESSAGE_URL
    headers = {"Authorization": f"OAuth {TOKEN}", "Content-Type": "application/json"}

    payload = {"chat_id": chat_id, "text": text}
    if keyboard:
        payload["inline_keyboard"] = keyboard

    logger.info (payload)
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
            
            if resp.status_code == 200:
                data = resp.json()
                if data.get("ok"):
                    logger.info("Сообщение успешно отправлено в чат %s", chat_id)
                    return True
                else:
                    logger.error("API вернул ok=False: %s", data)
                    return False
            else:
                # ВОТ ЗДЕСЬ МЫ ВИДИМ ПРИЧИНУ ОШИБКИ
                try:
                    error_detail = resp.json()
                except Exception:
                    error_detail = resp.text
                logger.error(
                    "Ошибка API: status=%s, detail=%s",
                    resp.status_code,
                    error_detail
                )
                return False
    except Exception as e:
        logger.exception("Исключение при отправке сообщения: %s", e)
        return False
    

async def test_send_message_with_buttons():
    chat_id="23208209-4a77-9fd8-5064-77aeffd34a20_8cdbb306-2ef5-92cb-796d-65179fd679cc"
    login = "avshilov995"
    inline_keyboard = [
        {
            "text": "👍 Да",
            "callback_data": { "data": "yes_clicked" }
        },
        {
            "text": "👎 Нет",
            "callback_data": { "data": "no_clicked" }
        }
    ]
    
    
    result = await send_message_to_chat(chat_id, "Выберите действие:", inline_keyboard)
    return result
async def main():
    result = await test_send_message_with_buttons()
    logger.info(result)

if __name__ == "__main__":
    asyncio.run(main())