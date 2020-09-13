from os.path import normpath
from enum import Enum

db_file = normpath('..\\..\\database')


class States(Enum):
    S_START = '0'
    S_CHOICE_LANGUAGE = '1'
    S_MENU = '2'
    S_CHOICE_HERO = '3'
    S_SEND_IMAGE = '4'
    S_CHOICE_ACT = '5'
