import random
from .models import Battle


# obrażenia zadawane przez postać
def calculate_player_damage(character, enemy):
    weapon_power = character.equipment.weapon.power if character.equipment.weapon else 0
    attack_power = character.strength + weapon_power
    variation = random.randint(-2, 2)

    defense = enemy.defense

    damage = attack_power + variation - defense
    return max(damage, 1)


# obrażenia zadawane postaci przez wroga
def calculate_enemy_damage(enemy, character):
    armor_power = character.equipment.get_total_armor_power()
    attack_power = enemy.attack
    variation = random.randint(-2, 2)

    defense = character.agility // 2 + armor_power

    damage = attack_power + variation - defense
    return max(damage, 1)


# postać atakuje przeciwnika. Zwraca zadane obrażenia.
def player_attack(battle):
    damage = calculate_player_damage(battle.character, battle.enemy)
    battle.enemy_current_hp -= damage

    if battle.enemy_current_hp <= 0:
        battle.enemy_current_hp = 0
        battle.status = Battle.Status.WON

    battle.save()
    return damage


# Przeciwnik atakuje postać. Zwraca zadane obrażenia.
def enemy_attack(battle):
    damage = calculate_enemy_damage(battle.enemy, battle.character)
    battle.character_current_hp -= damage

    if battle.character_current_hp <= 0:
        battle.character_current_hp = 0
        battle.status = Battle.Status.LOSE

    battle.save()
    return damage


def process_turn(battle):
    result = {"player_damage": 0, "enemy_damage": 0}

    if battle.status != Battle.Status.ONGOING:
        return result

    result["player_damage"] = player_attack(battle)

    if battle.status == Battle.Status.ONGOING:
        result["enemy_damage"] = enemy_attack(battle)
        battle.turn_number += 1
        battle.save()

    return result
