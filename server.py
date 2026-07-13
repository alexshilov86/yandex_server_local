
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from typing import Any, Dict, List
import logging
from logger_config import init_logger
from handlers import handle_message_logic
from parse_update import parse_update
from apscheduler.schedulers.background import BackgroundScheduler
from contextlib import asynccontextmanager
from data_from_base_update import update_data_from_base

init_logger()
logger = logging.getLogger(__name__)
logger.info ("Запуск сервера")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- ЭТОТ КОД СРАБАТЫВАЕТ ПРИ СТАРТЕ СЕРВЕРА ---
    # BackgroundScheduler работает в отдельном фоновом потоке
    scheduler = BackgroundScheduler()
    
    # Добавляем задачу: вызывать update_base каждые 3 часа
    # Для теста перед продакшеном можете заменить hours=3 на seconds=30
    scheduler.add_job(update_data_from_base, 'interval', hours=3)
    
    # Запускаем планировщик
    scheduler.start()
    logger.info("📅 Планировщик задач запущен: обновление базы настроено на каждые 3 часа.")
    
    yield # В этой точке сервер начинает принимать запросы пользователей
    
    # --- ЭТОТ КОД СРАБАТЫВАЕТ ПРИ ВЫКЛЮЧЕНИИ СЕРВЕРА ---
    scheduler.shutdown()
    logger.info("📅 Планировщик задач успешно остановлен.")

app = FastAPI(lifespan=lifespan)
@app.post("/webhook")
async def handle_webhook(request: Request) -> JSONResponse:
    
    try:
        payload = await request.json()
    except Exception as e:
        logger.error("Invalid JSON: %s", e)
        return JSONResponse(status_code=200, content={"status": "ok", "handled": False, "error": "invalid_json"})
    
    logger.info("=== ВХОДЯЩИЙ ВЕБХУК ===")
    logger.info(payload)
    from_data = payload.get("updates", [{}])[0].get("from", {})
    chat_data = payload.get("updates", [{}])[0].get("chat", {})
    text = payload.get("updates", [{}])[0].get("text")
    user_login = from_data.get("login")
    display_name = from_data.get("display_name")    
    logger.info(
        "Получено сообщение: login=%s, name=%s, text='%s'",
        user_login,
        display_name,
        text
    )

    updates = payload.get("updates", [])
    if not isinstance(updates, list):
        logger.warning("Поле 'updates' не является списком")
        return JSONResponse(status_code=200, content={"status": "ok", "handled": False, "error": "updates_not_list"})

    responses: List[Dict[str, Any]] = []

    if not isinstance(updates, list):
        logger.warning("Поле 'updates' не является списком")
        return JSONResponse(status_code=200, content={"status": "ok", "handled": False, "error": "updates_not_list"})

    for idx, update in enumerate(updates):
        parsed = parse_update(update)
        if not parsed:
            logger.warning("Не удалось распарсить update #%d", idx)
            responses.append({"update_index": idx, "status": "skipped", "reason": "parse_error"})
            continue
        
        if not parsed.get("chat_id"):
            logger.warning("Update #%d: отсутствуют chat_id", idx)
            responses.append({"update_index": idx, "status": "skipped", "reason": "missing_ids"})
            continue

        logger.info(
            "Обрабатываем update #%d: chat_id=%s user_id=%s text=%s",
            idx, parsed["chat_id"], parsed["user_id"], parsed.get("text")
        )

        try:
            reply_text = await handle_message_logic(parsed)
            responses.append({
                "update_index": idx,
                "status": "handled",
                "chat_id": parsed["chat_id"],
                "reply": reply_text,
            })
        except Exception as e:
            logger.exception("Ошибка при обработке update #%d: %s", idx, e)
            responses.append({
                "update_index": idx,
                "status": "error",
                "reason": str(e),
            })                    
    result = {
        "status": "ok",
        "handled_count": sum(1 for r in responses if r["status"] == "handled"),
        "errors_count": sum(1 for r in responses if r["status"] == "error"),
        "details": responses,
    }

    return JSONResponse(status_code=200, content=result)            
# Создаем lifespan-обработчик для FastAPI


# Запуск тестового сервера на локальном компьюетере
# if __name__ == "__main__":
#     import uvicorn

#     uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)