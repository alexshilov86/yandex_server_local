import requests

url = "http://127.0.0.1:8000/webhook"
nakl = "26-10531005882"
update = {'updates': [{'from': {'login': 'avshilov995', 'id': '8cdbb306-2ef5-92cb-796d-65179fd679cc', 'display_name': 'Александр Шилов', 'robot': False}, 'chat': {'type': 'private', 'id': '23208209-4a77-9fd8-5064-77aeffd34a20_8cdbb306-2ef5-92cb-796d-65179fd679cc'}, 'text':  nakl , 'timestamp': 1783850113, 'message_id': 1783850113344034, 'payload_id': 'a4eadbe6-370f-7f7b-be9fd9f1', 'update_id': 1783850113344034}]}

response = requests.post(url, json=update)
print(response.json())