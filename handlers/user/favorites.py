from aiogram import types, Dispatcher, F
from aiogram.exceptions import TelegramBadRequest, TelegramAPIError
from aiogram.fsm.context import FSMContext
from sqlalchemy.orm import sessionmaker

import utils.aiogram_helper as telegram
from integrations.database.models.user import get_user, update_user
from keyboards.user.user_keyboard import list_favorites_kb, delete_favor_kb, clear_all_kb
from utils.states.user import FSMFavorites


async def start_favorites(call: types.CallbackQuery, state: FSMContext, session_maker: sessionmaker):
    user_info = await get_user({'telegram_id': call.from_user.id}, session_maker)
    if user_info.favorites == 0 or user_info.favorites is None or user_info.favorites == []:
        await call.answer('🍽 Список пуст')
    else:
        await state.set_state(FSMFavorites.start_favorites)
        try:
            await call.message.edit_media(media=types.InputMediaPhoto(
                media=types.URLInputFile('https://grodno24.com/assets/images/2022/10/recept-1.jpeg')),
                reply_markup=await list_favorites_kb())
            msg = await call.message.edit_caption(caption='<b>📋Меню рецептов\n\n'
                                                          '❗️Присутсвует система поиска. '
                                                          'Чтобы воспользоваться поиском нажмите кнопку и '
                                                          'начинайте вводить первые буквы из названия</b>',
                                                  reply_markup=await list_favorites_kb())
        except TelegramAPIError:
            await call.message.delete()
            msg = await call.message.answer('<b>📋Меню рецептов\n\n'
                                            '❗️Присутсвует система поиска. '
                                            'Чтобы воспользоваться поиском нажмите кнопку и '
                                            'начинайте вводить первые буквы из названия</b>',
                                            reply_markup=await list_favorites_kb())
        await state.update_data(msg=msg)


async def search_favorites(query: types.InlineQuery, session_maker: sessionmaker):
    user_info = await get_user({'telegram_id': query.from_user.id}, session_maker)
    if query.query:
        results = []
        print(query.query)
        for favor in user_info.favorites[i]:
            print(favor)
            if query.query.lower() in f'{favor}'.lower():
                results.append(favor)
                print(results)
    else:
        results = user_info.favorites
    list_empty = [['Здесь пока пусто(', 'Добавьте рецепты в\nменю рецептов',
                   'https://bestveb.ru/kr.cgi?4&parameter=kartinki-i-risunki.ru', ' ']]
    if not results:
        await telegram.inline_helper(query, list_empty, 1)
    results = [[f'{favor["name"]}',
                f'Рейтинг {favor["rate"]}',
                f'{favor["photo"]}',
                f'🔗 {favor["url"]}'
                ] for favor in results]
    await telegram.inline_helper(query, results)


async def list_favorites(message: types.Message, state: FSMContext, session_maker: sessionmaker):
    user_info = await get_user({'telegram_id': message.from_user.id}, session_maker)
    url = message.text.split(' ')[1]
    await state.update_data(url=url)
    data = await state.get_data()
    await message.delete()
    for i in range(len(user_info.favorites)):
        if url == user_info.favorites[i]['url']:
            msg = await data['msg'].edit_media(media=
            types.InputMediaPhoto(
                media=types.URLInputFile(str(user_info.favorites[i]["photo"]))),
                reply_markup=await delete_favor_kb())
            await msg.edit_caption(caption=f'<b>✏️ Название</b> <code>{user_info.favorites[i]["name"]}</code>\n'
                                           f'<b>⭐️ Рейтинг</b> <code>{user_info.favorites[i]["rate"]}</code>\n\n'
                                           f'<b>📋 Используемые ингридиенты</b>\n'
                                           f'<i>{user_info.favorites[i]["ingredients"]}</i>'
                                           f'<b>🔗 Сылка</b> <a href="{user_info.favorites[i]["url"]}">Нажми на меня</a>',
                                   parse_mode='html', reply_markup=await delete_favor_kb())


async def delete_favorites(call: types.CallbackQuery, state: FSMContext, session_maker: sessionmaker):
    await call.answer('🗑 Удаленно из избранного')
    data = await state.get_data()
    user_info = await get_user({'telegram_id': call.from_user.id}, session_maker)
    new_favor = []
    for i in range(len(user_info.favorites)):
        if data['url'] != user_info.favorites[i]['url']:
            new_favor.append(user_info.favorites[i])
    await update_user(call.from_user.id, {'favorites': new_favor}, session_maker)


async def clear_all(call: types.CallbackQuery, session_maker: sessionmaker, state: FSMContext):
    await call.answer('🗑 Очищено')
    await update_user(call.from_user.id, {'favorites': 0}, session_maker)
    try:
        await call.message.edit_media(media=types.InputMediaPhoto(
            media=types.URLInputFile('https://grodno24.com/assets/images/2022/10/recept-1.jpeg')),
            reply_markup=await clear_all_kb())
        msg = await call.message.edit_caption(caption='<b>✔️ Меню рецептов очищено</b>\n'
                                                      '<code>*чисто*</code>',
                                              reply_markup=await clear_all_kb())
    except TelegramAPIError:
        await call.message.delete()
        msg = await call.message.answer('<b>✔️ Меню рецептов очищено</b>\n'
                                        '<code>*чисто*</code>',
                                        reply_markup=await clear_all_kb())
    await state.update_data(msg=msg)


def register_handler(dp: Dispatcher):
    dp.callback_query.register(start_favorites, F.data == 'favorites')
    dp.inline_query.register(search_favorites, FSMFavorites.start_favorites)
    dp.message.register(list_favorites, FSMFavorites.start_favorites, F.text.startswith('🔗'))
    dp.callback_query.register(delete_favorites, F.data == 'delete_favor')
    dp.callback_query.register(clear_all, F.data == 'clear_all')
