import os
from dotenv import load_dotenv

load_dotenv()

bearer_token = os.getenv("X_BEARER_TOKEN")
api_key = os.getenv("X_API_KEY")
api_secret = os.getenv("X_API_SECRET")
access_token = os.getenv("X_ACCESS_TOKEN")
access_token_secret = os.getenv("X_ACCESS_TOKEN_SECRET")
openai_key = os.getenv("OPENAI_API_KEY")
telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
