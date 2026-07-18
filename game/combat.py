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

    leveled_up = False
    if battle.enemy_current_hp <= 0:
        battle.enemy_current_hp = 0
        battle.status = Battle.Status.WON
        leveled_up = award_rewards(battle)

    battle.save()
    return damage, leveled_up


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
    result = {
        "player_damage": 0,
        "enemy_damage": 0,
        "experience_reward": 0,
        "gold_reward": 0,
        "leveled_up": False,
    }

    if battle.status != Battle.Status.ONGOING:
        return result

    damage, leveled_up = player_attack(battle)
    result["player_damage"] = damage
    result["leveled_up"] = leveled_up

    if battle.status == Battle.Status.WON:
        result["experience_reward"] = battle.enemy.experience_reward
        result["gold_reward"] = battle.enemy.gold_reward

    if battle.status == Battle.Status.ONGOING:
        result["enemy_damage"] = enemy_attack(battle)
        battle.turn_number += 1
        battle.save()

    return result


def award_battle(battle):
    character = battle.character
    enemy = battle.enemy

    character.experience += enemy.experience_reward
    character.gold += enemy.gold_reward
    character.save()


def use_potion(battle, inventory_item):
    if battle.status != Battle.Status.ONGOING:
        return {"healed": 0, "enemy_damage": 0}

    item = inventory_item.item
    character = battle.character

    heal_amount = item.heal_amount
    new_hp = battle.character_current_hp + heal_amount
    battle.character_current_hp = min(new_hp, character.max_hp)
    battle.save()

    inventory_item.quantity -= 1
    if inventory_item.quantity <= 0:
        inventory_item.delete()
    else:
        inventory_item.save()

    result = {"healed": heal_amount, "enemy_damage": 0}

    if battle.status == Battle.Status.ONGOING:
        result["enemy_damage"] = enemy_attack(battle)
        battle.turn_number += 1
        battle.save()

    return result


def award_rewards(battle):
    character = battle.character
    enemy = battle.enemy

    character.experience += enemy.experience_reward
    character.gold += enemy.gold_reward
    character.save()

    leveled_up = character.try_level_up()
    return leveled_up
