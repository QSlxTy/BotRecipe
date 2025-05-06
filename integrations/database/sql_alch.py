from sqlalchemy.ext.asyncio import create_async_engine as _create_async_engine
from sqlalchemy.orm import sessionmaker

from integrations.database.models.user import User
from integrations.database.models.settings import Settings
from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy.ext.asyncio
import os
from src.config import conf


def get_session_maker(engine: sqlalchemy.ext.asyncio.AsyncEngine) -> sessionmaker:
    return sessionmaker(engine, class_=sqlalchemy.ext.asyncio.AsyncSession, expire_on_commit=False)


async def create_connection() -> sqlalchemy.ext.asyncio.AsyncEngine:
    url = conf.db.build_connection_str()

    engine = _create_async_engine(
        url=url, pool_pre_ping=True)
    return engine


class Database:
    def __init__(
            self,
            session: AsyncSession,
            user: User = None,
            settings: Settings = None,
    ):
        self.session = session
        self.user = user or User()
        self.chat = settings or Settings()


async def init_models(engine):
    async with engine.begin() as conn:
        await conn.run_sync(User.metadata.create_all)
        await conn.run_sync(Settings.metadata.create_all)
