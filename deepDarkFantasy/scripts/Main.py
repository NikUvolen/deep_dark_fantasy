from peewee import *

from scripts.VkBot1 import VkBot
from scripts.settings.token import group_id, token
from scripts.settings.config import States
from scripts.dbworker import set_state, get_current_state, check_state
from scripts.gaming_mechanics.gaming_mechanics import GameMechanics
from scripts.Image_generation import image_generation

from scripts.init_user import init_user


vk_bot = VkBot(group_id, token)
game_scripts = GameMechanics()
db = SqliteDatabase('..\\database\\dungeon.db')


class UserData(Model):
    user_id = IntegerField(unique=True)
    daily_moves = IntegerField()
    room_number = IntegerField()
    character_name = CharField()
    character_hp = IntegerField()
    enemy_name = CharField(null=True)

    class Meta:
        database = db


class Warnings:
    @staticmethod
    def hero_warning(message):
        if get_current_state(message.peer_id) == States.S_CHOICE_HERO.value:
            vk_bot.send_message('Ты ещё не закончил выбор ♂leather men\'а♂.', message.peer_id)
            return True


@vk_bot.message_handler(commands=['начать', 'Начать', 'start', 'Start'])
def welcome_menu(message):
    if Warnings.hero_warning(message):
        return

    init_user(UserData, message.peer_id)
    set_state(message.peer_id, States.S_MENU.value)
    welcome_msg = 'Добро пожаловать в подземелье, ♂Dungeon master♂.'
    vk_bot.upload_keyboard(['Меню'])
    vk_bot.send_message(welcome_msg, message.peer_id, keyboard=True)


@vk_bot.message_handler(commands=['меню', 'Меню'])
def menu(message):
    if Warnings.hero_warning(message):
        return

    print(message.peer_id)
    user_data = UserData.select().where(UserData.user_id == message.peer_id).get()
    menu_msg = 'Добро пожаловать в меню.\n' \
               '-------------------------\n' \
               f'Пройдено комнат: {user_data.room_number}\n' \
               f'Заработано опыта: None\n' \
               f'Заработано монет: None'
    vk_bot.upload_keyboard(['Выбор героя', 'Новая комната'])
    vk_bot.send_message(menu_msg, message.peer_id, keyboard=True)


@vk_bot.message_handler(commands=['новая комната', 'Новая комната'])
def new_room(message):
    """Генерирует новую комнату и отправляет картинку"""
    if Warnings.hero_warning(message):
        return

    game_scripts.room_generation(UserData, message.peer_id)
    img = image_generation(UserData, message.peer_id)
    vk_bot.upload_keyboard(['Меню', 'Новая комната', 'Убить монстра'])
    vk_bot.send_image(message.peer_id, img, keyboard=True)


@vk_bot.message_handler(commands=['выбор героя', 'Выбор героя'])
def choice_hero(message):
    set_state(message.peer_id, States.S_CHOICE_HERO.value)
    vk_bot.send_message('Введите название героя', message.peer_id)


@vk_bot.message_handler(func=lambda message: get_current_state(message.peer_id) == States.S_CHOICE_HERO.value)
def choice_hero(message):
    print(get_current_state(message.peer_id), States.S_CHOICE_HERO.value)
    set_state(message.peer_id, States.S_MENU.value)
    print(get_current_state(message.peer_id), States.S_CHOICE_HERO.value)
    vk_bot.upload_keyboard(['Меню'])
    vk_bot.send_message(f'Ваш новый герой: {message.text}', message.peer_id, keyboard=True)


if __name__ == '__main__':
    UserData.create_table()
    vk_bot.listen()
