import random

from aiogram import types, Dispatcher, F
from aiogram.exceptions import TelegramAPIError
from aiogram.fsm.context import FSMContext
from sqlalchemy.orm import sessionmaker

from integrations.database.models.settings import get_settings
from integrations.database.models.user import update_user, get_user
from keyboards.user.user_keyboard import random_menu_kb


async def random_recipe(call: types.CallbackQuery, state: FSMContext, session_maker: sessionmaker):
    data = await state.get_data()
    info = await get_settings(session_maker)
    recipe = (info.recipes_data[random.randint(0, 988)])
    ingredients = recipe['ingredients']
    name = recipe['name']
    rate = recipe['rate']
    photo = recipe['photo']
    url = recipe['url']
    try:
        msg = await data['msg'].edit_media(media=types.InputMediaPhoto(media=types.URLInputFile(str(photo))),
                                           reply_markup=await random_menu_kb())
        await msg.edit_caption(caption=f'<b>✏️ Название</b> <code>{name}</code>\n'
                                       f'<b>⭐️ Рейтинг</b> <code>{rate}</code>\n\n'
                                       f'<b>📋 Используемые ингридиенты</b>\n'
                                       f'<i>{ingredients}</i>'
                                       f'<b>🔗 Сылка</b> <a href="{url}">Нажми на меня</a>',
                               parse_mode='html', reply_markup=await random_menu_kb())
    except TelegramAPIError:
        msg = await call.message.answer_photo(photo=types.URLInputFile(str(photo)),
                                              reply_markup=await random_menu_kb(),
                                              caption=f'<b>✏️ Название</b> <code>{name}</code>\n'
                                                      f'<b>⭐️ Рейтинг</b> <code>{rate}</code>\n\n'
                                                      f'<b>📋 Используемые ингридиенты</b>\n'
                                                      f'<i>{ingredients}</i>'
                                                      f'<b>🔗 Сылка</b> <a href="{url}">Нажми на меня</a>')

    await state.update_data(url=url,
                            msg=msg,
                            recipe=recipe)


async def add_to_favorites(call: types.CallbackQuery, state: FSMContext, session_maker: sessionmaker):
    data = await state.get_data()
    count_complete = 0
    user_info = await get_user({'telegram_id': call.from_user.id}, session_maker)
    if user_info.favorites is None or user_info.favorites == 0 or user_info.favorites == []:
        recipe_favor = [data['recipe']]
        await call.answer('Рецепт успешно добавлен')
        await update_user(call.from_user.id, {'favorites': recipe_favor}, session_maker)
    else:
        user_info = await get_user({'telegram_id': call.from_user.id}, session_maker)
        for i in range(len(user_info.favorites)):
            user_info = await get_user({'telegram_id': call.from_user.id}, session_maker)
            if data['url'] == user_info.favorites[i]['url']:
                await call.answer('Данный рецепт уже в избранном')
            else:
                count_complete += 1

        if count_complete == len(user_info.favorites):
            await call.answer('Рецепт успешно добавлен')
            user_info = await get_user({'telegram_id': call.from_user.id}, session_maker)
            await update_user(call.from_user.id, {'favorites': user_info.favorites + [data['recipe']]}, session_maker)


def register_handler(dp: Dispatcher):
    dp.callback_query.register(random_recipe, F.data == 'random_recipe')
    dp.callback_query.register(add_to_favorites, F.data == 'add_member')
