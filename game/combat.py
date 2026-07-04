import random
from .models import Battle


# obrażenia zadawane przez postać
def calculate_player_damage(character, enemy):
    attack_power = character.strength
    variation = random.randint(-2, 2)

    defense = enemy.defense

    damage = attack_power + variation - defense
    return max(damage, 1)


# obrażenia zadawane postaci przez wroga
def calculate_enemy_damage(enemy, character):
    attack_power = enemy.attack
    variation = random.randint(-2, 2)

    defense = character.agility // 2

    damage = attack_power + variation - defense
    return max(damage, 1)


# postać atakuje przeciwnika. Zwraca zadane obrażenia.
def player_attack(battle):
    damage = calculate_player_damage(battle.character)
    battle.enemy_current_hp -= damage

    if battle.enemy_current_hp <= 0:
        battle.enemy_current_hp = 0
        battle.status = Battle.Status.WON

    battle.save()
    return damage


# Przeciwnik atakuje postać. Zwraca zadane obrażenia.
def enemy_attack(battle):
    damage = calculate_enemy_damage(battle.enemy)
    battle.character_current_hp -= damage

    if battle.character_current_hp <= 0:
        battle.character_current_hp = 0
        battle.status - Battle.Status.LOSE

    battle.save()
    return damage
