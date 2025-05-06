from typing import Callable, Dict, Any, Awaitable, Union
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from integrations.database.models.user import is_user_exists, create_user


class RegisterCheck(BaseMiddleware):
    def __init__(self):
        pass

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Union[Message, CallbackQuery],
            data: Dict[str, Any]
    ) -> Any:
        if data.get('session_maker'):
            session_maker = data['session_maker']
            if not await is_user_exists(user_id=event.from_user.id, session_maker=session_maker):
                await create_user(user_id=event.from_user.id, session_maker=session_maker)
                return await handler(event, data)
            else:
                return await handler(event, data)
