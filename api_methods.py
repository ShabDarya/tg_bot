import requests
from datetime import date
from config import API_KEY, Y_token, model_id
import json


today = date.today()

def get_current_temp(town):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={town}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    data_res = response.json()
    print(data_res)
    return data_res

def get_future_temp(town):
    data_res = get_current_temp(town)
    url = f"http://api.openweathermap.org/data/2.5/forecast?lat={data_res['coord']['lat']}&lon={data_res['coord']['lon']}&appid={API_KEY}"
    response = requests.get(url)
    data_res = response.json()
    print(data_res)

def get_token_yandex():
    headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    }

    data = {"yandexPassportOauthToken": Y_token}
    data = json.dumps(data)

    response = requests.post('https://iam.api.cloud.yandex.net/iam/v1/tokens', headers=headers, data=data)
    
    return response.json()['iamToken']

def get_food_calories(food):
    token = get_token_yandex()

    body = {"modelUri": f"gpt://{model_id}/yandexgpt-lite/latest", "completionOptions": {"maxTokens":50,"temperature":0}, "messages": [{"role":"user","text":f"Напиши очень коротко. Сколько калорий в 100 грамм стандартный {food}. Пример ответа: 30 калорий"}]}
    body = json.dumps(body)

    headers = {'Content-Type': 'application/json','Authorization': 'Bearer ' + token,'x-folder-id': model_id,}

    response = requests.post('https://llm.api.cloud.yandex.net/foundationModels/v1/completion', headers=headers, data=body)
    print(response.json())
    return response.json()

def get_train_calories(train):
    token = get_token_yandex()

    body = {"modelUri": f"gpt://{model_id}/yandexgpt-lite/latest", "completionOptions": {"maxTokens":50,"temperature":0}, "messages": [{"role":"user","text":f"Напиши 2 словами. Сколько в среднем калорий сжигается за 30 минут тренировки {train} вне зависимости от любых факторов"}]}
    body = json.dumps(body)

    headers = {'Content-Type': 'application/json','Authorization': 'Bearer ' + token,'x-folder-id': model_id,}

    response = requests.post('https://llm.api.cloud.yandex.net/foundationModels/v1/completion', headers=headers, data=body)
    print(response.json())
    return response.json()
