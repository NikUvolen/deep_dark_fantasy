import json
from os.path import normpath
from random import random, choice, randint


class GameMechanics:
    def __init__(self):
        self.enemy = None
        self.common_enemy = ['Arthor.png', 'Jorge.png', 'Jozef.png', 'Lanselot.png']
        self.rare_enemy = ['Fedya.png']

    def _enemy_generation(self):
        act = random()
        if act <= .8:
            self.enemy = choice(self.common_enemy)
        elif .8 < act:
            self.enemy = choice(self.rare_enemy)
        # else:
        #     легендарный моб

    def room_generation(self, database, user_id):
        self._enemy_generation()

        user = database.select().where(database.user_id == user_id).get()
        user.daily_moves -= 1
        user.room_number += 1
        user.enemy_name = self.enemy
        user.save()

    def fight(self, user_id):
        path = normpath(f'..\\database\\{user_id}.json')
        with open(path, 'r') as file:
            template = json.load(file)

        if 'enemy' in template['room']:
            template['user_data']["number_daily_moves"] -= 1
            hero_accuracy = 60
            hero_detection = 30
            if template['room']['enemy']['name'] in self.common_enemy:
                enemy_dexterity = randint(25, 30)
                enemy_damage = randint(10, 15)
            elif template['room']['enemy']['name'] in self.rare_enemy:
                enemy_dexterity = randint(40, 45)
                enemy_damage = randint(25, 30)
            else:
                return False, None

            # вычисление вероятности
            if enemy_dexterity - hero_detection > 0:
                hit_chance = hero_accuracy - (enemy_dexterity - hero_detection)
            else:
                hit_chance = hero_accuracy + ((enemy_dexterity - hero_detection) * -1)

            # Удар
            act = random()
            print(act, hit_chance / 100)
            if act < hit_chance / 100:
                template['room'].pop('enemy')
                with open(path, 'w') as file:
                    json.dump(template, file, indent=4)
                return True, hit_chance
            else:
                template['game_data']['character']['hp'] -= enemy_damage
                with open(path, 'w') as file:
                    json.dump(template, file, indent=4)
                return enemy_damage, hit_chance
        else:
            return False, None
