from random import randint
import vk_api
from vk_api import VkUpload
from vk_api.bot_longpoll import VkBotLongPoll
from vk_api.keyboard import VkKeyboard, VkKeyboardColor


class DotDict(dict):
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __init__(self, dct):
        super().__init__()
        for key, value in dct.items():
            if hasattr(value, 'keys'):
                value = DotDict(value)
            self[key] = value


class SupportFunctions:
    @staticmethod
    def get_random_id():
        return randint(0, 2 ** 20)

    @staticmethod
    def isint(n):
        try:
            int(n)
            return True
        except ValueError:
            return False

    @staticmethod
    def build_handler_dict(handler, **filters):
        return DotDict({'function': handler, 'filters': filters})


class VkBot:
    """Use Python 3.7"""

    def __init__(self, group_id, token):
        self.group_id = group_id
        self.token = token
        self.message_list = []

        self.vk = vk_api.VkApi(token=token)
        self.img = VkUpload(self.vk)
        self.keyboard = VkKeyboard(one_time=True)
        self.long_poller = VkBotLongPoll(self.vk, self.group_id)
        self.api = self.vk.get_api()
        self.funcs = SupportFunctions()

    def add_msg_handler(self, handler_dict):
        self.message_list.append(handler_dict)

    def _delete_keyboard(self):
        """Очищает клавиатуру"""
        self.keyboard.lines[0].clear()

    def _upload_image(self, image_path):
        """Готовит картинку для отправки"""
        response = DotDict(self.img.photo_messages(image_path)[0])

        owner_id = response.owner_id
        photo_id = response.id
        access_key = response.access_key

        return owner_id, photo_id, access_key

    def upload_keyboard(self, labels: list, color=VkKeyboardColor.POSITIVE, lines=None):
        """Загружает клавиатуру для отправки"""
        if len(labels) > 4:
            return
        for num, label in enumerate(labels):
            if lines:
                if num in lines:
                    self.keyboard.add_line()
            self.keyboard.add_button(label=label, color=color)

    def send_image(self, user_id, image_path, keyboard=False):
        """Отправляет картинку пользователю"""
        owner_id, photo_id, access_key = self._upload_image(image_path)
        attachment = f'photo{owner_id}_{photo_id}_{access_key}'

        self.api.messages.send(
            random_id=self.funcs.get_random_id(),
            peer_id=user_id,
            attachment=attachment,
            keyboard=self.keyboard.get_keyboard() if keyboard else None
        )
        self._delete_keyboard()

    def send_message(self, message, user_id, keyboard=False):
        """Отправляет сообщение пользователю"""
        self.api.messages.send(
            message=message,
            random_id=self.funcs.get_random_id(),
            peer_id=user_id,
            keyboard=self.keyboard.get_keyboard() if keyboard else None
        )
        if keyboard:
            self._delete_keyboard()

    def message_handler(self, commands=None, func=None, **kwargs):
        def wrapper(handler):
            handler_dict = self.funcs.build_handler_dict(handler,
                                                         commands=commands,
                                                         func=func,
                                                         **kwargs)
            self.add_msg_handler(handler_dict)

        return wrapper

    def _on_event(self, event):
        if event.type != vk_api.bot_longpoll.VkBotEventType.MESSAGE_NEW:
            print('не умею обрабатывать это: %s', event.type)

        requisites = DotDict(event.obj)
        for msg in self.message_list:
            if msg.filters.commands is not None and requisites.text in msg.filters.commands:
                var = msg.function
                var(requisites)
                break
            if msg.filters.func is not None and msg.filters.func(requisites):
                var = msg.function
                var(requisites)
                break

    def listen(self):
        for event in self.long_poller.listen():
            self._on_event(event)
