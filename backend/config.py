from pydantic_settings import BaseSettings

from bot.config import BOT_TOKEN, SECRET_KEY

class Settings(BaseSettings):
    BOT_TOKEN: str
    JWT_SECRET: str
    JWT_ALG: str = "HS256"
    JWT_EXP_MIN: int = 60 * 24  # 24h

settings = Settings(BOT_TOKEN = BOT_TOKEN, JWT_SECRET = SECRET_KEY)