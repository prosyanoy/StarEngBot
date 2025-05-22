import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession
from sqlalchemy.orm import sessionmaker
from models import Base
from config import DATABASE_URL

engine: AsyncEngine = None
async_session_maker: sessionmaker = None

async def init_db():
    global engine, async_session_maker
    logging.info("Создаём асинхронный движок для базы данных...")
    engine = create_async_engine(DATABASE_URL, echo=False, future=True)
    async_session_maker = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logging.info("База данных инициализирована.")

async def shutdown_db():
    global engine
    if engine:
        await engine.dispose()
        logging.info("Движок базы данных закрыт.")
