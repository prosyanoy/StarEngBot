import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.environ.get("BOT_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
DATABASE_URL = os.environ.get("DATABASE_URL")
BOT_USERNAME = os.environ.get("BOT_USERNAME")
MINI_APP_URL = os.environ.get("MINI_APP_URL")
SECRET_KEY = os.environ.get("SECRET_KEY")