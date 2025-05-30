import logging
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from bot.models import Base
from bot.config import DATABASE_URL

engine = create_async_engine(DATABASE_URL, echo=False, future=True)
async_session_maker = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def init_db():
    global engine, async_session_maker
    if engine:                     # already initialised
        return

    logging.info("Initialising DB …")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logging.info("DB ready.")


async def shutdown_db():
    global engine
    if engine:
        await engine.dispose()
        logging.info("DB engine closed.")


# Optional helper so FastAPI *can* still use the usual lifespan mechanism
@asynccontextmanager
async def lifespan_context(app):
    await init_db()
    yield
    await shutdown_db()
