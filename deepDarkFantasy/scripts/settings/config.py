from os.path import normpath
from enum import Enum

db_file = normpath('..\\..\\database')


class States(Enum):
    S_MENU = '0'
    S_CHOICE_HERO = '1'
    S_SEND_IMAGE = '2'
    S_CHOICE_ACT = '3'
