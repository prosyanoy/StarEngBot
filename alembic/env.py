import asyncio
from logging.config import fileConfig

# dev/alembic/env.py
import os, sys

# make sure "dev/" (the folder containing db/ and alembic/) is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from bot.models import Base
from bot.config import DATABASE_URL

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from alembic import context

# this is the Alembic Config object
config = context.config
# interpret the config file for Python logging.
fileConfig(config.config_file_name)

target_metadata = Base.metadata  # <-- set this to your MetaData

def do_run_migrations(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        # include other args like compare_type, etc.
    )
    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online():
    # pull the URL (you could also do config.set_main_option from env)
    connectable: AsyncEngine = create_async_engine(
        DATABASE_URL,
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        # run the synchronous migration logic in the async context
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

if context.is_offline_mode():
    # keep your existing offline logic
    context.run_migrations()
else:
    # kick off the async function
    asyncio.run(run_migrations_online())
