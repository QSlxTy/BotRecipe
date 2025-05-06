from handlers.user import start, random_choice, favorites, search_recipe


def register_handler(dp):
    start.register_start_handler(dp)
    random_choice.register_handler(dp)
    favorites.register_handler(dp)
    search_recipe.register_handler(dp)
