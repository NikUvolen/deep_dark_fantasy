import json
import random
from os import remove
from os.path import isfile, normpath

import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.upload import VkUpload
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

from scripts.gaming_mechanics.gaming_mechanics import Game
from scripts.init_user import init_user
from scripts.settings.token import token, group_id
from scripts.Image_generation import image_generation


# TODO: сделать логи
# log = logging.getLogger('bot')


def get_random_id():
    return random.randint(0, 2 ** 20)


def isint(n):
    try:
        int(n)
        return True
    except ValueError:
        return False


class Main:
    """Use Python 3.7"""

    def __init__(self, group_id, token):
        self.group_id = group_id
        self.token = token

        self.vk = vk_api.VkApi(token=token)
        self.img = VkUpload(self.vk)
        self.keyboard = VkKeyboard(one_time=True)
        self.long_poller = VkBotLongPoll(self.vk, self.group_id)
        self.api = self.vk.get_api()

        self.game = Game()

    def _upload_img(self, image_path):
        """Готовит картинку для отправки"""

        response = self.img.photo_messages(image_path)[0]

        owner_id = response['owner_id']
        photo_id = response['id']
        access_key = response['access_key']

        return owner_id, photo_id, access_key

    def _send_img(self, owner_id, photo_id, access_key, peer_id, keyboard=False):
        """Отправляет картинку пользователю"""

        attachment = f'photo{owner_id}_{photo_id}_{access_key}'
        self.api.messages.send(
            random_id=get_random_id(),
            peer_id=peer_id,
            attachment=attachment,
            keyboard=self.keyboard.get_keyboard() if keyboard else None
        )

        self._delete_keyboard()

    def _send_message(self, message, peer_id, keyboard=False):
        """Отправляет сообщение пользователю"""

        self.api.messages.send(
            message=message,
            random_id=get_random_id(),
            peer_id=peer_id,
            keyboard=self.keyboard.get_keyboard() if keyboard else None
        )

        if keyboard:
            self._delete_keyboard()

    def _upload_keyboard(self, labels: list, color=VkKeyboardColor.POSITIVE, lines=None):
        """Загружает клавиатуру для отправки"""

        if len(labels) > 4:
            return
        for num, label in enumerate(labels):
            if lines:
                if num in lines:
                    self.keyboard.add_line()

            self.keyboard.add_button(label=label, color=color)

    def _delete_keyboard(self):
        """Очищает клавиатуру"""
        self.keyboard.lines[0].clear()

    def _new_room(self, peer_id):
        """Генерирует новую комнату и отправляет картинку"""

        self.game.room_generation(user_id=peer_id)
        image_generation(user_id=peer_id)
        self._upload_keyboard(['Начать', 'Новая комната', 'Убить монстра'])
        self._send_img(*self._upload_img('test.png'), peer_id, keyboard=True)
        remove('test.png')

    def _kill_monster(self, peer_id):
        """Убивает монтра и отправляет картинку"""

        result, hit_chance = self.game.fight(user_id=peer_id)
        if result is True:
            self._upload_keyboard(['Начать', 'Новая комната'])
            self._send_message(f'Вы победили с шансом {hit_chance}%! Путь свободен.', peer_id, keyboard=True)
        elif isint(result):
            self._upload_keyboard(['Начать', 'Новая комната', 'Убить монстра'])
            self._send_message(f'К сожалению, Вы промазали c шансом {hit_chance}% и получили урон = {result} ед',
                               peer_id,
                               keyboard=True)
        else:
            self._send_message(f'В комнате нет врагов.', peer_id, keyboard=True)
        image_generation(user_id=peer_id)
        self._send_img(*self._upload_img('test.png'), peer_id)

    def _choose_hero(self, peer_id):
        self._upload_keyboard(['Начать'])
        self._send_message('Пока что доступен только один герой(', peer_id, keyboard=True)

    def _checking_moves(self, peer_id):
        path = normpath(f'..\\database\\{peer_id}.json')
        with open(path, 'r') as file:
            number_daily_moves = json.load(file)['user_data']['number_daily_moves']

        if number_daily_moves <= 0:
            self._upload_keyboard(['Начать', 'Получить ещё ходов'])
            self._send_message('У Вас больше нет ходов на сегодня((', peer_id, keyboard=True)
            return False
        else:
            return True

    def _get_moves(self, peer_id):
        path = normpath(f'..\\database\\{peer_id}.json')
        with open(path, 'r') as file:
            template = json.load(file)

        template['user_data']['number_daily_moves'] += 30
        self._upload_keyboard(['Начать', 'Новая комната'])
        self._send_message(f"Теперь у вас {template['user_data']['number_daily_moves']} ходов", peer_id, keyboard=True)

        with open(path, 'w') as file:
            json.dump(template, file, indent=4)

    def _on_event(self, event):
        """Главный цикл бота"""

        user_msg = event.obj.text
        if event.type != vk_api.bot_longpoll.VkBotEventType.MESSAGE_NEW:
            print('не умею обрабатывать это: %s', event.type)

        if user_msg.lower() == 'начать' or user_msg.lower() == 'start':
            result = init_user(user_id=event.obj.peer_id)
            menu = 'Добро пожаловать в меню.'
            if not result:
                menu = 'Ваша БД создана. ' + menu
            self._upload_keyboard(['Выбор героя', 'Новая комната'])
            self._send_message(menu, event.obj.peer_id, keyboard=True)
        elif isfile(normpath(f'..\\database\\{event.obj.peer_id}.json')):
            if user_msg.lower() == 'выбор героя':
                self._choose_hero(peer_id=event.obj.peer_id)
            elif user_msg.lower() == 'новая комната' and self._checking_moves(peer_id=event.obj.peer_id):
                self._new_room(peer_id=event.obj.peer_id)
            elif user_msg.lower() == 'убить монстра' and self._checking_moves(peer_id=event.obj.peer_id):
                self._kill_monster(peer_id=event.obj.peer_id)
            elif user_msg.lower() == 'получить ещё ходов' and not self._checking_moves(peer_id=event.obj.peer_id):
                self._get_moves(peer_id=event.obj.peer_id)

    def run(self):
        for event in self.long_poller.listen():
            self._on_event(event)


if __name__ == '__main__':
    bot = Main(group_id, token=token)
    bot.run()


# TODO: перевести БД с json'a на sqlLite
