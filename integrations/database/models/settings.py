import json

from sqlalchemy import BigInteger, JSON
from sqlalchemy import select
from sqlalchemy.orm import Mapped, mapped_column, sessionmaker

from ..modeles import AbstractModel


class Settings(AbstractModel):
    __tablename__ = 'settings'

    recipes_data: Mapped[json] = mapped_column(JSON)
    admin_topic: Mapped[int] = mapped_column(BigInteger())


async def get_settings(session_maker: sessionmaker) -> Settings:
    async with session_maker() as session:
        async with session.begin():
            result = await session.execute(select(Settings))
            return result.scalars().first()
