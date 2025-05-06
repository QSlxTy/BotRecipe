from aiogram.fsm.state import State, StatesGroup


class FSMFavorites(StatesGroup):
    start_favorites = State()
    search_favorites = State()


class FSMSearchRecipe(StatesGroup):
    start_search = State()
    get_words = State()
    choose_recipe_from_search = State()
