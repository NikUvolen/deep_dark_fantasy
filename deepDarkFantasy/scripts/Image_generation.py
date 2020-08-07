import os
from os.path import normpath, join, isfile
from json import load
from PIL import Image, ImageDraw, ImageFont

from scripts.gaming_mechanics.gaming_mechanics import Game


def finding_picture_enemy(enemy_name):
    image_path = normpath('..\\assets\\sprates\\units')
    files = os.listdir(image_path)
    for file in files:
        l_path = join(image_path, file)
        if os.path.isdir(l_path):
            if enemy_name in os.listdir(l_path):
                return join(l_path, enemy_name)


def generation_hp_bar(hp):
    numbers = [0, 20, 40, 60, 80, 100]
    for enum, num in enumerate(numbers):
        if hp < num:
            hp_bar = Image.open(normpath(f'..\\assets\\sprates\\hp_bar\\hp_bar_{numbers[enum - 1]}.png'))
            break
    else:
        hp_bar = Image.open(normpath(f'..\\assets\\sprates\\hp_bar\\hp_bar_100.png'))

    return hp_bar


def image_generation(user_id):
    """ Функция для генерации картинки """

    path = normpath(f'..\\database\\{user_id}.json')
    with open(path, 'r') as file:
        data = load(file)
        bg_name = 'podzemelye3.png'
        hp = data["game_data"]["character"]["hp"]
        character_name = data["game_data"]["character"]["name"]
        enemy_name = data["room"]["enemy"]["name"] if 'enemy' in data["room"] else None
        print(enemy_name)

    bg = Image.open(normpath(f'..\\assets\\sprates\\bg\\{bg_name}'))
    character = Image.open(normpath(f'..\\assets\\sprates\\units\\hero\\{character_name}'))
    hp_bar = generation_hp_bar(hp=hp)

    # Инициальзация параметров для текста
    idraw = ImageDraw.Draw(bg)
    font = ImageFont.truetype(font=normpath('..\\assets\\fonts\\Gamer.ttf'), size=48)

    if enemy_name is not None:
        enemy = Image.open(normpath(finding_picture_enemy(enemy_name)))
        bg.paste(enemy, (555, -70), enemy)
        idraw.text(xy=(770, 450), text=enemy_name.split('.')[0], font=font)

    bg.paste(hp_bar, (20, -10), hp_bar)
    bg.paste(character, (-50, -70), character)

    # Нанесение текста
    idraw.text(xy=(137, 12), text=str(hp), font=font)

    bg.save(f'test.png')
