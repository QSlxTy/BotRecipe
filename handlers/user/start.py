from aiogram import types, Dispatcher, F
from aiogram.exceptions import TelegramAPIError
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy.orm import sessionmaker

from keyboards.user.user_keyboard import menu_kb


async def start_command(message: types.Message, state: FSMContext, session_maker: sessionmaker):
    await state.clear()
    await message.delete()
    msg = await message.answer_photo(
        caption=f'👋 <b>Привет, {message.from_user.full_name}!\n'
                f'Я Готовка Бот, я помогу тебе найти '
                f'множество различных рецептов\n'
                f'Удачи, повар! 🧑‍🍳\n',
        reply_markup=await menu_kb(message.from_user.id, session_maker),
        photo='https://grodno24.com/assets/images/2022/10/recept-1.jpeg'
    )
    await state.update_data(msg=msg)


async def main_menu(call: types.CallbackQuery, state: FSMContext, session_maker: sessionmaker):
    data = await state.get_data()
    await state.clear()
    try:
        try:
            msg = await data['msg'].edit_media(media=types.InputMediaPhoto(
                media=types.URLInputFile('https://grodno24.com/assets/images/2022/10/recept-1.jpeg')),
                reply_markup=await menu_kb(call.from_user.id, session_maker))
            await msg.edit_caption(
                caption=f'👋 <b>Привет, {call.from_user.full_name}!\n'
                        f'Я Готовка Бот, я помогу тебе найти '
                        f'множество различных рецептов\n'
                        f'Удачи, повар! 🧑‍🍳\n',
                reply_markup=await menu_kb(call.from_user.id, session_maker)
            )
        except TelegramAPIError:
            msg = await call.message.edit_text(
                text=f'👋 <b>Привет, {call.from_user.full_name}!\n'
                     f'Я Готовка Бот, я помогу тебе найти '
                     f'множество различных рецептов\n'
                     f'Удачи, повар! 🧑‍🍳\n',
                reply_markup=await menu_kb(call.from_user.id, session_maker),
                disable_web_page_preview=True
            )
    except TelegramAPIError:
        msg = await call.message.answer(
            text=f'👋 <b>Привет, {call.from_user.full_name}!\n'
                 f'Я Готовка Бот, я помогу тебе найти '
                 f'множество различных рецептов\n'
                 f'Удачи, повар! 🧑‍🍳\n',
            reply_markup=await menu_kb(call.from_user.id, session_maker),
            disable_web_page_preview=True
        )
    await state.update_data(msg=msg)


def register_start_handler(dp: Dispatcher):
    dp.message.register(start_command, Command('start'))
    dp.callback_query.register(main_menu, F.data == 'main_menu')
