from peewee import IntegrityError


def init_user(datadase, user_id, character_name='Kirill.png'):
    """
    Функция проверяет есть ли пользователь в БД.
    Если нет - добавляет.
    """
    try:
        datadase.create(user_id=user_id,
                        daily_moves=30,
                        room_number=0,
                        character_name=character_name,
                        character_hp=100,
                        enemy_name=None)
        return True
    except IntegrityError:
        return False
