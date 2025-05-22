import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN, OPENAI_API_KEY
import openai

from db import init_db, shutdown_db
from middleware import DBSessionMiddleware

from handlers.start import router as start_router
from handlers.words import router as words_router
from handlers.collections import router as collections_router

logging.basicConfig(level=logging.INFO)

# Инициализируем OpenAI API
openai.api_key = OPENAI_API_KEY

async def main():
    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Регистрируем роутеры
    dp.include_router(start_router)
    dp.include_router(words_router)
    dp.include_router(collections_router)

    # Инициализируем базу данных
    await init_db()

    from db import async_session_maker
    # Регистрируем middleware для создания сессии БД для каждого обновления
    dp.update.middleware.register(DBSessionMiddleware(async_session_maker))

    try:
        await dp.start_polling(bot)
    finally:
        await shutdown_db()

if __name__ == "__main__":
    asyncio.run(main())
