from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional

    from aiogram.types import InlineQuery, User, MessageEntity
    from aiogram.fsm.context import FSMContext
    from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, ForceReply
    from aiogram.exceptions import TelegramRetryAfter
    from aiogram.utils.keyboard import InlineKeyboardMarkup

from aiogram import Bot
from aiogram.types.base import UNSET_DISABLE_WEB_PAGE_PREVIEW, UNSET_PROTECT_CONTENT, UNSET_PARSE_MODE
from aiogram.types import InputMediaPhoto, InputMediaDocument, InputMediaAnimation, InputMediaVideo
from aiogram.types import InlineQueryResultArticle, InputTextMessageContent
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
from aiogram.utils.markdown import hlink
from aiogram.exceptions import TelegramAPIError
from aiogram.fsm.context import FSMContext



async def inline_helper(query: InlineQuery, results: list[list[str, str, Optional[str], str]], no_result: int = 0):
    """
    :param no_result: minimum number of results
    :param query: event InlineQuery
    :param results: list[title, description, url, message_text]
    :return:
    """
    offset = int(query.offset) if query.offset else 0
    offset_results = results[offset:offset + 50]
    articles = []
    article_index = 0
    for result in offset_results:
        if article_index == 50:
            break
        articles.append(InlineQueryResultArticle(
            id=str(article_index),
            title=result[0],
            description=result[1],
            thumb_url=result[2],
            input_message_content=InputTextMessageContent(message_text=result[3])
        ))
        article_index += 1
    if len(results) > offset + 50:
        await query.answer(articles, cache_time=1, is_personal=True, next_offset=str(offset + 50))
    else:
        if len(results) == no_result:
            articles.append(InlineQueryResultArticle(
                id=str(no_result), title='🎉Нет', description='Список пуст',
                thumb_url='https://cdn-icons-png.flaticon.com/512/7214/7214241.png',
                input_message_content=InputTextMessageContent(message_text='/start')))
        await query.answer(articles, cache_time=1, is_personal=True)
