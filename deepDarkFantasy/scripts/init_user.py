import json
from os.path import isfile, normpath


def init_user(user_id, character_name='Kirill.png'):
    """
    Функция проверяет есть ли пользователь в БД.
    Если нет - добавляет.

    state: 0 - Инициальзация пользователя
    state: 1 - Выбор героя
    state: 2 - Начало игры
    """
    path = f'..\\database\\{user_id}.json'
    if isfile(path):
        return True
    else:
        template = {
            "user_data": {
                "state": "0",
                "user_id": user_id,
                "number_daily_moves": 30
            },
            "game_data": {
                "character": {
                    "name": character_name,
                    "hp": 100
                },
            }
        }
        with open(path, 'w') as file:
            json.dump(template, file, indent=4)
