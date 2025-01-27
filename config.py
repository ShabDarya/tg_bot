import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN_BOT")
API_KEY = os.getenv("API_KEY")
Y_token = os.getenv("Y_token")
model_id = os.getenv("model_id")

if not TOKEN:
    raise ValueError("Переменная окружения TOKEN_BOT не установлена!")