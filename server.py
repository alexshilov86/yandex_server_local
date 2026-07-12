
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

import logging
from logger_config import init_logger

init_logger()
logger = logging.getLogger(__name__)

app = FastAPI()

@app.post("/webhook")
async def handle_webhook(request: Request) -> JSONResponse:
    try:
        payload = await request.json()
    except Exception as e:
        logger.error("Invalid JSON: %s", e)
        return JSONResponse(status_code=200, content={"status": "ok", "handled": False, "error": "invalid_json"})

    logger.info("=== ВХОДЯЩИЙ ВЕБХУК ===")
