# bot/bot_app.py
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from bot.config import BOT_TOKEN
from bot.middleware import DBSessionMiddleware
from db import async_session_maker

from bot.handlers.start import router   as start_router
from bot.handlers.words import router   as words_router
from bot.handlers.collections import router as collections_router


def build_bot_and_dispatcher() -> tuple[Bot, Dispatcher]:
    bot = Bot(token=BOT_TOKEN)
    dp  = Dispatcher(storage=MemoryStorage())

    # Routers
    dp.include_router(start_router)
    dp.include_router(words_router)
    dp.include_router(collections_router)

    # DB middleware (session_maker will be populated by init_db before polling)
    dp.update.middleware.register(DBSessionMiddleware(async_session_maker))

    return bot, dp
