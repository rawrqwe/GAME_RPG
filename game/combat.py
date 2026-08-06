import random

from .models import Battle, Item


CLASS_SKILLS = {
    Item.Type.SWORD: {
        "name": "Potężne uderzenie",
        "mana_cost": 10,
    },
    Item.Type.BOW: {
        "name": "Precyzyjny strzał",
        "mana_cost": 12,
    },
    Item.Type.STAFF: {
        "name": "Kula ognia",
        "mana_cost": 20,
    },
}


def get_character_weapon_type(character):
    starting_weapon = (
        character
        .character_class
        .starting_weapon
    )

    if starting_weapon is None:
        return None

    return starting_weapon.type


def get_character_skill(character):
    weapon_type = get_character_weapon_type(
        character,
    )

    return CLASS_SKILLS.get(
        weapon_type,
    )


def get_player_attack_stat(character, weapon):
    equipment = character.equipment

    strength = (
        character.strength
        + equipment.get_stat_bonus(
            Item.BonusStats.STRENGTH,
        )
    )

    agility = (
        character.agility
        + equipment.get_stat_bonus(
            Item.BonusStats.AGILITY,
        )
    )

    intelligence = (
        character.intelligence
        + equipment.get_stat_bonus(
            Item.BonusStats.INTELLIGENCE,
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
        strength,
    )


def calculate_player_damage(character, enemy):
    weapon = character.equipment.weapon

    weapon_power = (
        weapon.power
        if weapon
        else 0
    )

    attack_stat = get_player_attack_stat(
        character,
        weapon,
    )

    attack_power = (
        attack_stat
        + weapon_power
    )

    variation = random.randint(-2, 2)

    damage = (
        attack_power
        + variation
        - enemy.defense
    )

    return max(damage, 1)


def calculate_skill_damage(character, enemy):
    equipment = character.equipment

    equipped_weapon = equipment.weapon

    class_weapon = (
        character
        .character_class
        .starting_weapon
    )

    weapon_type = get_character_weapon_type(
        character,
    )

    weapon_for_stat = (
        class_weapon
        if class_weapon is not None
        else equipped_weapon
    )

    attack_stat = get_player_attack_stat(
        character,
        weapon_for_stat,
    )

    weapon_power = 0

    if (
        equipped_weapon is not None
        and equipped_weapon.type == weapon_type
    ):
        weapon_power = equipped_weapon.power

    attack_power = (
        attack_stat
        + weapon_power
    )

    variation = random.randint(-2, 2)

    if weapon_type == Item.Type.SWORD:
        damage = (
            attack_power
            + attack_stat // 2
            + variation
            - enemy.defense
        )

    elif weapon_type == Item.Type.BOW:
        damage = (
            attack_power
            + 4
            + variation
            - enemy.defense // 2
        )

    elif weapon_type == Item.Type.STAFF:
        damage = (
            attack_power
            + attack_stat // 2
            + variation
            - enemy.defense // 2
        )

    else:
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
        Item.BonusStats.AGILITY,
    )

    effective_agility = (
        character.agility
        + agility_bonus
    )

    agility_defense = (
        effective_agility // 4
    )

    armor_defense = (
        armor_power // 5
    )

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


def sync_character_resources(battle):
    character = battle.character

    character.current_hp = (
        battle.character_current_hp
    )

    character.current_mana = (
        battle.character_current_mana
    )

    character.save(
        update_fields=[
            "current_hp",
            "current_mana",
        ]
    )


def resolve_player_damage(battle, damage):
    battle.enemy_current_hp -= damage

    leveled_up = False

    if battle.enemy_current_hp <= 0:
        battle.enemy_current_hp = 0
        battle.status = Battle.Status.WON

        leveled_up = award_rewards(
            battle,
        )

        if leveled_up:
            battle.character_current_hp = (
                battle.character.current_hp
            )

            battle.character_current_mana = (
                battle.character.current_mana
            )

    battle.save()

    return leveled_up


def player_attack(battle):
    damage = calculate_player_damage(
        battle.character,
        battle.enemy,
    )

    leveled_up = resolve_player_damage(
        battle,
        damage,
    )

    return damage, leveled_up


def enemy_attack(battle):
    damage = calculate_enemy_damage(
        battle.enemy,
        battle.character,
    )

    battle.character_current_hp -= damage

    if battle.character_current_hp <= 0:
        battle.character_current_hp = 0
        battle.status = Battle.Status.LOSE

    battle.save()

    return damage


def get_empty_turn_result():
    return {
        "player_damage": 0,
        "enemy_damage": 0,
        "experience_reward": 0,
        "gold_reward": 0,
        "leveled_up": False,
        "skill_name": "",
        "mana_cost": 0,
        "error": "",
    }


def add_rewards_to_result(result, battle):
    if battle.status != Battle.Status.WON:
        return

    result["experience_reward"] = (
        battle.enemy.experience_reward
    )

    result["gold_reward"] = (
        battle.enemy.gold_reward
    )


def finish_enemy_turn(result, battle):
    if battle.status != Battle.Status.ONGOING:
        return

    result["enemy_damage"] = enemy_attack(
        battle,
    )

    battle.turn_number += 1
    battle.save()


def process_turn(battle):
    result = get_empty_turn_result()

    if battle.status != Battle.Status.ONGOING:
        return result

    damage, leveled_up = player_attack(
        battle,
    )

    result["player_damage"] = damage
    result["leveled_up"] = leveled_up

    add_rewards_to_result(
        result,
        battle,
    )

    finish_enemy_turn(
        result,
        battle,
    )

    sync_character_resources(battle)

    return result


def process_skill(battle):
    result = get_empty_turn_result()

    if battle.status != Battle.Status.ONGOING:
        return result

    skill = get_character_skill(
        battle.character,
    )

    if skill is None:
        result["error"] = (
            "Ta postać nie posiada "
            "umiejętności klasowej."
        )

        return result

    mana_cost = skill["mana_cost"]

    if (
        battle.character_current_mana
        < mana_cost
    ):
        result["error"] = (
            "Masz za mało many, aby użyć "
            f"umiejętności: {skill['name']}."
        )

        return result

    battle.character_current_mana -= (
        mana_cost
    )

    damage = calculate_skill_damage(
        battle.character,
        battle.enemy,
    )

    leveled_up = resolve_player_damage(
        battle,
        damage,
    )

    result["player_damage"] = damage
    result["leveled_up"] = leveled_up
    result["skill_name"] = skill["name"]
    result["mana_cost"] = mana_cost

    add_rewards_to_result(
        result,
        battle,
    )

    finish_enemy_turn(
        result,
        battle,
    )

    sync_character_resources(battle)

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
        character.total_max_hp,
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
            battle,
        )

        battle.turn_number += 1
        battle.save()

    sync_character_resources(battle)

    return result


def award_rewards(battle):
    character = battle.character
    enemy = battle.enemy

    character.experience += (
        enemy.experience_reward
    )

    character.gold += (
        enemy.gold_reward
    )

    character.save()

    return character.try_level_up()