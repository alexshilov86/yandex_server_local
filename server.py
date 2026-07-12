
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from typing import Any, Dict, List
import logging
from logger_config import init_logger
from handlers import handle_message_logic
from parse_update import parse_update

init_logger()
logger = logging.getLogger(__name__)



app = FastAPI()
@app.post("/webhook")
async def handle_webhook(request: Request) -> JSONResponse:
    logger.info(f"Получен вебхук. Количество обновлений: {len(payload.updates)}")
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)