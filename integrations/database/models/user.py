import json

from sqlalchemy import select, BigInteger, BOOLEAN, JSON, update, insert
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.orm import sessionmaker, Mapped, mapped_column
from sqlalchemy.sql.operators import add

from ..modeles import AbstractModel


class User(AbstractModel):
    __tablename__ = 'users'

    telegram_id: Mapped[int] = mapped_column(BigInteger(), unique=True)
    is_admin: Mapped[str] = mapped_column(BOOLEAN)
    favorites: Mapped[json] = mapped_column(JSON, default=None)


async def get_user(select_by: dict, session_maker: sessionmaker) -> User:
    async with session_maker() as session:
        async with session.begin():
            result = await session.execute(
                select(User).filter_by(**select_by)
            )
            return result.scalars().one()


async def create_user(user_id: int, session_maker: sessionmaker) -> [User, Exception]:
    async with session_maker() as session:
        async with session.begin():
            user = User(
                telegram_id=user_id,
                is_admin=0,
                favorites=0
            )
            try:
                session.add(user)
                return User
            except ProgrammingError as _e:
                return _e


async def is_user_exists(user_id: int, session_maker: sessionmaker) -> bool:
    async with session_maker() as session:
        async with session.begin():
            sql_res = await session.execute(select(User).where(User.telegram_id == user_id))
            return bool(sql_res.first())


async def update_user(telegram_id: int, data: dict, session_maker: sessionmaker) -> None:
    async with session_maker() as session:
        async with session.begin():
            await session.execute(update(User).where(User.telegram_id == telegram_id).values(data))
            await session.commit()
