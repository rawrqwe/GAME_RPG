import random

from .models import Battle, Item


def get_player_attack_stat(character, weapon):
    equipment = character.equipment

    strength = (
        character.strength
        + equipment.get_stat_bonus(
            Item.BonusStats.STRENGTH
        )
    )

    agility = (
        character.agility
        + equipment.get_stat_bonus(
            Item.BonusStats.AGILITY
        )
    )

    intelligence = (
        character.intelligence
        + equipment.get_stat_bonus(
            Item.BonusStats.INTELLIGENCE
        )
    )

    if weapon is None:
        return strength

    attack_stats = {
        Item.Type.SWORD: strength,
        Item.Type.BOW: agility,
        Item.Type.STAFF: intelligence,
    }

    return attack_stats.get(
        weapon.type,
        strength
    )


def calculate_player_damage(character, enemy):
    weapon = character.equipment.weapon

    weapon_power = weapon.power if weapon else 0
    attack_stat = get_player_attack_stat(
        character,
        weapon
    )

    attack_power = attack_stat + weapon_power
    variation = random.randint(-2, 2)

    damage = (
        attack_power
        + variation
        - enemy.defense
    )

    return max(damage, 1)


def calculate_enemy_damage(enemy, character):
    equipment = character.equipment

    armor_power = (
        equipment.get_total_armor_power()
    )

    agility_bonus = equipment.get_stat_bonus(
        Item.BonusStats.AGILITY
    )

    effective_agility = (
        character.agility
        + agility_bonus
    )

    agility_defense = effective_agility // 4
    armor_defense = armor_power // 5

    defense = (
        agility_defense
        + armor_defense
    )

    variation = random.randint(-2, 2)

    damage = (
        enemy.attack
        + variation
        - defense
    )

    return max(damage, 1)


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
        result["enemy_damage"] = enemy_attack(
            battle
        )

        battle.turn_number += 1
        battle.save()

    return result


def use_potion(battle, inventory_item):
    if battle.status != Battle.Status.ONGOING:
        return {
            "healed": 0,
            "enemy_damage": 0,
        }

    item = inventory_item.item
    character = battle.character

    hp_before_healing = (
        battle.character_current_hp
    )

    new_hp = (
        hp_before_healing
        + item.heal_amount
    )

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
        result["enemy_damage"] = enemy_attack(
            battle
        )

        battle.turn_number += 1
        battle.save()

    return result


def award_rewards(battle):
    character = battle.character
    enemy = battle.enemy

    character.experience += (
        enemy.experience_reward
    )

    character.gold += enemy.gold_reward
    character.save()

    return character.try_level_up()