import random

from .models import Battle, Item


# Wybór głównej statystyki ataku na podstawie używanej broni.
def get_player_attack_stat(character, weapon):
    if weapon is None:
        return character.strength

    attack_stats = {
        Item.Type.SWORD: character.strength,
        Item.Type.BOW: character.agility,
        Item.Type.STAFF: character.intelligence,
    }

    return attack_stats.get(
        weapon.type,
        character.strength
    )


# Obrażenia zadawane przez postać.
def calculate_player_damage(character, enemy):
    weapon = character.equipment.weapon

    weapon_power = weapon.power if weapon else 0
    attack_stat = get_player_attack_stat(character, weapon)

    attack_power = attack_stat + weapon_power
    variation = random.randint(-2, 2)

    damage = attack_power + variation - enemy.defense

    return max(damage, 1)


# Obrażenia zadawane postaci przez przeciwnika.
def calculate_enemy_damage(enemy, character):
    armor_power = character.equipment.get_total_armor_power()
    attack_power = enemy.attack
    variation = random.randint(-2, 2)

    agility_defense = character.agility // 4
    armor_defense = armor_power // 3

    defense = agility_defense + armor_defense

    damage = attack_power + variation - defense

    return max(damage, 1)


# Postać atakuje przeciwnika.
# Funkcja zwraca zadane obrażenia oraz informację o awansie.
def player_attack(battle):
    damage = calculate_player_damage(
        battle.character,
        battle.enemy
    )

    battle.enemy_current_hp -= damage

    leveled_up = False

    if battle.enemy_current_hp <= 0:
        battle.enemy_current_hp = 0
        battle.status = Battle.Status.WON
        leveled_up = award_rewards(battle)

    battle.save()

    return damage, leveled_up


# Przeciwnik atakuje postać.
# Funkcja zwraca zadane obrażenia.
def enemy_attack(battle):
    damage = calculate_enemy_damage(
        battle.enemy,
        battle.character
    )

    battle.character_current_hp -= damage

    if battle.character_current_hp <= 0:
        battle.character_current_hp = 0
        battle.status = Battle.Status.LOSE

    battle.save()

    return damage


# Przetworzenie pełnej tury walki.
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
        result["experience_reward"] = (
            battle.enemy.experience_reward
        )

        result["gold_reward"] = (
            battle.enemy.gold_reward
        )

    if battle.status == Battle.Status.ONGOING:
        result["enemy_damage"] = enemy_attack(battle)

        battle.turn_number += 1
        battle.save()

    return result


# Użycie mikstury podczas walki.
def use_potion(battle, inventory_item):
    if battle.status != Battle.Status.ONGOING:
        return {
            "healed": 0,
            "enemy_damage": 0,
        }

    item = inventory_item.item
    character = battle.character

    hp_before_healing = battle.character_current_hp

    new_hp = hp_before_healing + item.heal_amount

    battle.character_current_hp = min(
        new_hp,
        character.max_hp
    )

    actual_healing = (
        battle.character_current_hp
        - hp_before_healing
    )

    battle.save()

    inventory_item.quantity -= 1

    if inventory_item.quantity <= 0:
        inventory_item.delete()
    else:
        inventory_item.save()

    result = {
        "healed": actual_healing,
        "enemy_damage": 0,
    }

    if battle.status == Battle.Status.ONGOING:
        result["enemy_damage"] = enemy_attack(battle)

        battle.turn_number += 1
        battle.save()

    return result


# Przyznanie nagród po zwycięskiej walce.
def award_rewards(battle):
    character = battle.character
    enemy = battle.enemy

    character.experience += enemy.experience_reward
    character.gold += enemy.gold_reward
    character.save()

    leveled_up = character.try_level_up()

    return leveled_up