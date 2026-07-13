import logging
from dotenv import load_dotenv
from logger_config import init_logger
import os
import aiohttp

load_dotenv()
init_logger()
logger = logging.getLogger(__name__)
BOT_TOKEN = os.getenv("YANDEX_BOT_TOKEN", "")
SEND_MESSAGE_URL = "https://botapi.messenger.yandex.net/bot/v1/messages/sendText/"


async def send_message_to_chat(
    session: aiohttp.ClientSession, 
    chat_id: str, 
    text: str, 
    keyboard=None
) -> bool:
    url = "https://botapi.messenger.yandex.net/bot/v1/messages/sendText/"
    headers = {"Authorization": f"OAuth {BOT_TOKEN}", "Content-Type": "application/json"}
    
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    
    if keyboard:
        prepared_buttons = []
        btn_counter = 0  # Счётчик для автоматической генерации уникальных id кнопок
        
        for row in keyboard:
            prepared_row = []
            for button in row:
                if isinstance(button, (tuple, list)) and len(button) == 2:
                    btn_text, btn_callback = button
                elif isinstance(button, dict):
                    btn_text = button.get("text", "")
                    btn_callback = button.get("callback_data", "")
                else:
                    continue
                
                btn_counter += 1
                
                # Собираем кнопку по спецификации SuggestButtons Яндекса
                prepared_row.append({
                    "id": f"btn_{btn_counter}_{btn_callback}",
                    "title": btn_text,
                    "directives": [
                        {
                            "type": "server_action",
                            "name": btn_callback,
                            "payload": {"data": btn_callback}
                        }
                    ]
                })
            prepared_buttons.append(prepared_row)
            
        # Упаковываем массив в объект suggest_buttons с ключом layout
        payload["suggest_buttons"] = {
            "layout": "true",
            "buttons": prepared_buttons
        }

    try:
        async with session.post(url, json=payload, headers=headers, timeout=10) as response:
            if response.status == 200:
                result = await response.json()
                if result.get("ok") is True:
                    return True
            
            error_text = await response.text()
            logging.error(f"Ошибка API Яндекса: status={response.status}, body={error_text}")
            return False
            
    except Exception as e:
        logging.error(f"Сетевая ошибка при отправке сообщения: {e}")
        return False

    
import asyncio

async def main():
    # Создаем одну глобальную сессию на всё время жизни бота
    async with aiohttp.ClientSession() as session:
        
        chat_id = "23208209-4a77-9fd8-5064-77aeffd34a20_8cdbb306-2ef5-92cb-796d-65179fd679cc"
        menu = [[("Да", "yes"), ("Нет", "no")]]
        my_keyboard = [
            [("👍 Да", "yes"), ("👎 Нет", "no")],
            [("🔙 В главное меню", "main_menu")]
        ]        
        # Передаем сессию внутрь функции отправки
        success = await send_message_to_chat(session, chat_id, "Вы готовы?", keyboard=my_keyboard)
        print("Отправлено:", success)

if __name__ == "__main__":
    asyncio.run(main())

