import logging
import random
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard as keyboard
from vk_api.keyboard import VkKeyboardColor

from settings.token import token

group_id = 196353741
log = logging.getLogger('bot')


def configure_logging():
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter('%(levelname)s %(message)s'))
    stream_handler.setLevel(logging.INFO)
    log.addHandler(stream_handler)

    file_handler = logging.FileHandler('bot.log', encoding='utf8')
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
    file_handler.setLevel(logging.DEBUG)
    log.addHandler(file_handler)

    log.setLevel(logging.DEBUG)


class Bot:
    def __init__(self, group_id, token):
        self.group_id = group_id
        self.token = token
        self.vk = vk_api.VkApi(token=token)
        self.long_poller = VkBotLongPoll(self.vk, self.group_id)
        self.api = self.vk.get_api()

        self.keyboard = keyboard()

    def _send_message(self, label, event, ):
        pass

    def run(self):
        for event in self.long_poller.listen():
            try:
                self.on_event(event)
            except Exception:
                log.exception('Ошибка в обработке события')

    def on_event(self, event):
        if event.type != vk_api.bot_longpoll.VkBotEventType.MESSAGE_NEW:
            log.info('не умею обрабатывать это: %s', event.type)

        if event.obj.text == 'Начать':
            self.delete_buttons()
            self.add_buttons(labels=['Fuck u!', 'Ты кто по жизни, Пепсик?', 'F'], lines=[1])

            message = self.keyboard.get_keyboard()
            log.debug('отправляем сообщение назад')

            self.api.messages.send(message='Кнопку выбери:',
                                   random_id=random.randint(0, 2 ** 20),
                                   peer_id=event.obj.peer_id,
                                   keyboard=message)
        if event.obj.text == 'Fuck u!':
            message = self.keyboard.get_empty_keyboard()
            self.api.messages.send(message='No, fuck u, leather man!',
                                   random_id=random.randint(0, 2 ** 20),
                                   peer_id=event.obj.peer_id,
                                   keyboard=message)

    def delete_buttons(self):
        self.keyboard.lines[0].clear()

    def add_buttons(self, labels: list, color=VkKeyboardColor.POSITIVE, lines: list = None):
        if len(labels) > 4:
            return
        for num, label in enumerate(labels):
            if lines:
                if num in lines:
                    self.keyboard.add_line()

            self.keyboard.add_button(label=label, color=color)


if __name__ == '__main__':
    configure_logging()
    bot = Bot(group_id, token=token)
    bot.run()
