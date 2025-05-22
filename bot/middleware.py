from aiogram.dispatcher.middlewares.base import BaseMiddleware
from sqlalchemy.orm import sessionmaker

class DBSessionMiddleware(BaseMiddleware):
    def __init__(self, session_maker: sessionmaker):
        super().__init__()
        self.session_maker = session_maker

    async def __call__(self, handler, event, data):
        async with self.session_maker() as session:
            data["db_session"] = session
            return await handler(event, data)
