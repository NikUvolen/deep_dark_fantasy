# -*- coding: utf-8 -*-
from vedis import Vedis
from scripts.settings import config


# State of the user from the "state" database
def get_current_state(user_id):
    with Vedis(config.db_file) as db:
        try:
            return db[user_id].decode()
        except KeyError:
            return config.States.S_MENU.value


# Saving the current "state" of the user in the database
def set_state(user_id, value):
    with Vedis(config.db_file) as db:
        try:
            db[user_id] = value
            return True
        except:
            return False
