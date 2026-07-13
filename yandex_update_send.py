import requests
import logging
from logger_config import init_logger
init_logger()
logger = logging.getLogger(__name__)
url = "http://127.0.0.1:8000/webhook"
nakl = "накладная 26-10531005882"
update = {'updates': [{'from': {'login': 'avshilov995', 'id': '8cdbb306-2ef5-92cb-796d-65179fd679cc', 'display_name': 'Александр Шилов', 'robot': False}, 'chat': {'type': 'private', 'id': '23208209-4a77-9fd8-5064-77aeffd34a20_8cdbb306-2ef5-92cb-796d-65179fd679cc'}, 'text':  nakl , 'timestamp': 1783850113, 'message_id': 1783850113344034, 'payload_id': 'a4eadbe6-370f-7f7b-be9fd9f1', 'update_id': 1783850113344034}]}
try:
    response = requests.post(url, json=update)
    response.raise_for_status()
    logger.info(f"Запрос успешно выполнен. Статус ответа: {response.status_code}")

except requests.exceptions.HTTPError as http_err:
    logger.error(f"Сервер вернул ошибку кода HTTP: {http_err}")
except requests.exceptions.ConnectionError as conn_err:
        logger.error(
            f"Ошибка подключения! Проверьте, запущен ли локальный сервер: {conn_err}"
        )
# 3. Перехватываем превышение времени ожидания (сервер завис и не отвечает)
except requests.exceptions.Timeout as timeout_err:
        logger.error(f"Время ожидания ответа от сервера истекло: {timeout_err}")        

# 4. Перехватываем любые другие непредвиденные ошибки requests
except requests.exceptions.RequestException as general_err:
        logger.error(f"Произошла непредвиденная ошибка при запросе: {general_err}")
response_json = response.json()
logger.info(response_json['details'][0]['reply'])