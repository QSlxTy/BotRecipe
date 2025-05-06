import random

from aiogram import types, F, Dispatcher
from aiogram.exceptions import TelegramBadRequest, TelegramAPIError
from aiogram.fsm.context import FSMContext
from sqlalchemy.orm import sessionmaker

import utils.aiogram_helper as telegram
from integrations.database.models.settings import get_settings
from integrations.database.models.user import get_user, update_user
from keyboards.user.user_keyboard import back_menu_kb, list_search_kb, result_search_kb
from utils.states.user import FSMSearchRecipe


async def start_search(call: types.CallbackQuery, state: FSMContext):
    await state.set_state(FSMSearchRecipe.start_search)
    try:
        msg = await call.message.edit_caption(caption='<b>📋Поиск по ключевым словам\n\n'
                                                      '❗️Введите ключевые слова через пробел.\n'
                                                      'Пример: <code>мука яйца сыр</code>\n\n'
                                                      '❗️ Поиск может занять время, ожидайте</b>',
                                              reply_markup=await back_menu_kb())
    except TelegramAPIError:
        await call.message.delete()
        msg = await call.message.answer(text='<b>📋Поиск по ключевым словам\n\n'
                                             '❗️Введите ключевые слова через пробел.\n'
                                             'Пример: <code>мука яйца сыр</code>\n\n'
                                             '❗️ Поиск может занять время, ожидайте</b>',
                                        reply_markup=await back_menu_kb())
    await state.update_data(msg=msg)


async def get_words(message: types.Message, state: FSMContext, session_maker: sessionmaker):
    await state.set_state(FSMSearchRecipe.get_words)
    await message.delete()
    data = await state.get_data()
    words = message.text.lower().split()
    info = await get_settings(session_maker)
    list_recipes = []
    for word in words:
        for i in range(0, 988):
            print(info.recipes_data[i]['name'].lower())
            if word in info.recipes_data[i]['ingredients'].lower() or word in info.recipes_data[i]['name'].lower():
                list_recipes.append(info.recipes_data[i])
                print(list_recipes)

    print(list_recipes)
    words_str = ''
    for word in words:
        words_str += word
        words_str += ' '
    try:
        msg = await data['msg'].edit_caption(caption='<b>📋 Ваш результат поиска\n\n'
                                                     'Список ключевых слов:\n'
                                                     f'✔️ <code>{words_str}</code></b>',
                                             reply_markup=await list_search_kb())
    except TelegramAPIError:
        await message.delete()
        msg = await message.answer('<b>📋 Ваш результат поиска\n\n'
                                   'Список ключевых слов:\n'
                                   f'✔️ <code>{words_str}</code></b>',
                                   reply_markup=await list_search_kb())
    await state.update_data(msg=msg,
                            list_recipes=list_recipes)


async def choose_recipe_from_search(query: types.InlineQuery, state: FSMContext):
    data = await state.get_data()
    if query.query:
        results = []
        for recipes in data['list_recipes']:
            if query.query.lower() in f'{recipes["name"]}'.lower():
                results.append(recipes)
    else:
        if len(data['list_recipes']) > 50:
            my_random_choice = random.choices(data['list_recipes'], k=50)
            results = my_random_choice
        else:
            results = data['list_recipes']
    list_empty = [['Здесь пока пусто(', 'Добавьте рецепты в\nменю рецептов',
                   'https://bestveb.ru/kr.cgi?4&parameter=kartinki-i-risunki.ru', ' ']]
    if not results:
        await telegram.inline_helper(query, list_empty, 1)
    results = [[f'{recipe["name"]}',
                f'Рейтинг {recipe["rate"]}',
                f'{recipe["photo"]}',
                f'🔗 {recipe["url"]}'
                ] for recipe in results]
    await telegram.inline_helper(query, results)


async def result_search(message: types.Message, state: FSMContext, session_maker: sessionmaker):
    info = await get_settings(session_maker)
    tag = message.text.split(' ')[1]
    await state.update_data(tag=tag)
    data = await state.get_data()
    await message.delete()
    for i in range(0, 988):
        if tag == info.recipes_data[i]['url']:
            msg = await data['msg'].edit_media(media=
            types.InputMediaPhoto(
                media=types.URLInputFile(str(info.recipes_data[i]["photo"]))),
                reply_markup=await result_search_kb())
            await msg.edit_caption(caption=f'<b>✏️ Название</b> <code>{info.recipes_data[i]["name"]}</code>\n'
                                           f'<b>⭐️ Рейтинг</b> <code>{info.recipes_data[i]["rate"]}</code>\n\n'
                                           f'<b>📋 Используемые ингридиенты</b>\n'
                                           f'<i>{info.recipes_data[i]["ingredients"]}</i>'
                                           f'<b>🔗 Сылка</b> <a href="{info.recipes_data[i]["url"]}">Нажми на меня</a>',
                                   parse_mode='html', reply_markup=await result_search_kb())
            await state.update_data(url=info.recipes_data[i]["url"],
                                    recipe=info.recipes_data[i])


async def add_favorites_from_search(call: types.CallbackQuery, state: FSMContext, session_maker: sessionmaker):
    data = await state.get_data()
    count_complete = 0
    user_info = await get_user({'telegram_id': call.from_user.id}, session_maker)
    info = await get_settings(session_maker)
    if user_info.favorites is None or user_info.favorites == 0 or user_info.favorites == []:
        await call.answer('Рецепт успешно добавлен')
        await update_user(call.from_user.id, {'favorites': [data['recipe']]}, session_maker)
    else:
        user_info = await get_user({'telegram_id': call.from_user.id}, session_maker)
        for i in range(len(user_info.favorites)):
            if data['recipe'] == user_info.favorites[i]:
                await call.answer('Данный рецепт уже в избранном')
            else:
                count_complete += 1

        if count_complete == len(user_info.favorites):
            await call.answer('Рецепт успешно добавлен')
            user_info = await get_user({'telegram_id': call.from_user.id}, session_maker)
            await update_user(call.from_user.id, {'favorites': user_info.favorites + [data['recipe']]}, session_maker)


def register_handler(dp: Dispatcher):
    dp.callback_query.register(start_search, F.data == 'search_recipe')
    dp.message.register(get_words, FSMSearchRecipe.start_search, F.content_type == 'text')
    dp.inline_query.register(choose_recipe_from_search, FSMSearchRecipe.get_words)
    dp.message.register(result_search, FSMSearchRecipe.get_words, F.text.startswith('🔗'))
    dp.callback_query.register(add_favorites_from_search, F.data == 'add_member_from_search')
