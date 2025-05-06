import json
import random

import requests
from bs4 import BeautifulSoup

count = 0
recipe_info = []
count_rand = 0
for i in random.sample(range(30000), 1000):

    url = f'https://www.iamcook.ru/showrecipe/{i}'
    req = requests.get(url)
    soup = BeautifulSoup(req.text, 'lxml')
    try:
        rate = soup.find('div', class_='rateyocounter')
        if rate == 0:
            rate = round(random.uniform(2, 10), 2)
            print('Рандомный рейтинг')
            count_rand += 1
        name = soup.find('h1', itemprop='name')
        recipe = soup.find('div', class_='ilist')
        photo = soup.find('figure').find('img')
        count += 1
        print('---------', count, '---------')
        recipe_info.append({'name': name.text,
                            'ingredients': recipe.text,
                            'rate': rate.text,
                            'photo': 'https:' + photo['src'],
                            'url': url})
    except AttributeError:
        pass

print(recipe_info)
print('Колличество рецептов без рейтинга из 1000', count_rand)
with open('recipe.json', 'w', encoding='utf8') as outfile:
    json.dump(recipe_info, outfile, ensure_ascii=False, indent=4, sort_keys=True)
