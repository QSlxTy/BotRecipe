from aiogram.utils.keyboard import InlineKeyboardBuilder

from integrations.database.models.user import get_user


async def menu_kb(call, session):
    builder = InlineKeyboardBuilder()
    user_info = await get_user({'telegram_id': call}, session)
    builder.button(text='🎲 Получить рандомный рецепт', callback_data='random_recipe')
    builder.button(text='📋 Поиск рецептов', callback_data='search_recipe')
    if user_info.favorites is None or user_info.favorites == 0 or user_info.favorites == []:
        builder.button(text='🫥 Пусто', callback_data='favorites')
    else:
        builder.button(text='❤️ Избранное', callback_data='favorites')

    builder.adjust(2)
    return builder.as_markup()


async def back_menu_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text='🔙 В главное меню', callback_data='main_menu')
    return builder.as_markup()


async def random_menu_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text='🔙 В главное меню', callback_data='main_menu')
    builder.button(text='🔁 Повторить', callback_data='random_recipe')
    builder.button(text='❤️ Добавить в избранное', callback_data='add_member')
    builder.adjust(2)
    return builder.as_markup()


async def list_favorites_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text='🗑  Очистить всё', callback_data='clear_all')
    builder.button(text='🔙 В главное меню', callback_data='main_menu')
    builder.button(text='📋 Список избранного', switch_inline_query_current_chat='')
    builder.adjust(2)
    return builder.as_markup()


async def delete_favor_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text='🔙 В главное меню', callback_data='main_menu')
    builder.button(text='📋 Список избранного', callback_data='favorites')
    builder.button(text='🗑 Удалить из избранного', callback_data='delete_favor')
    builder.adjust(2)
    return builder.as_markup()


async def list_search_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text='📋 Результат запроса', switch_inline_query_current_chat='')
    builder.button(text='🔙 В главное меню', callback_data='main_menu')
    return builder.as_markup()


async def result_search_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text='❤️ Добавить в избранное', callback_data='add_member_from_search')
    builder.button(text='🔙 В главное меню', callback_data='main_menu')
    return builder.as_markup()


async def clear_all_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text='🔙 В главное меню', callback_data='main_menu')
    return builder.as_markup()
