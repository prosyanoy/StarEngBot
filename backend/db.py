import logging
import sys
import os
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from contextlib import asynccontextmanager


# Add the parent directory to the path to import from the bot directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from bot.models import Base
from bot.config import DATABASE_URL

# Create engine and session factory
engine = create_async_engine(DATABASE_URL, poolclass=NullPool)
async_session_maker = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)

# Define lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

async def init_db():
    logging.info("Initializing database...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logging.info("Database initialized.")

async def get_session() -> AsyncSession:
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()
