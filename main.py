#!/usr/bin/env python3
import asyncio
import contextlib
import logging

from uvicorn import Config, Server

from db import init_db, shutdown_db
from bot.bot_app import build_bot_and_dispatcher
from backend.api import build_api

logging.basicConfig(level=logging.INFO)


async def run_bot():
    bot, dp = build_bot_and_dispatcher()
    try:
        await dp.start_polling(bot)
    finally:
        # Recommended but not strictly required
        await bot.session.close()


async def run_api():
    app = build_api()
    cfg = Config(app=app, host="0.0.0.0", port=8000, loop="asyncio", lifespan="on")
    server = Server(cfg)
    await server.serve()


async def main():
    await init_db()

    bot_task = asyncio.create_task(run_bot(), name="bot_task")
    api_task = asyncio.create_task(run_api(), name="api_task")

    done, pending = await asyncio.wait(
        {bot_task, api_task},
        return_when=asyncio.FIRST_EXCEPTION,
    )

    for task in pending:
        task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await task

    # 4. shutdown DB
    await shutdown_db()

if __name__ == "__main__":
    asyncio.run(main())
