from .combat import (
    calculate_enemy_damage,
    calculate_player_damage,
)


MAX_SIMULATION_TURNS = 100


def get_balance_label(
    win_rate,
    remaining_hp_percentage,
):
    if win_rate < 40:
        return "Za trudny"

    if win_rate < 70:
        return "Trudny"

    if remaining_hp_percentage <= 35:
        return "Trudny"

    if (
        win_rate < 90
        or remaining_hp_percentage <= 65
    ):
        return "Zbalansowany"

    return "Za łatwy"


def simulate_battle(
    character,
    enemy,
    max_turns=MAX_SIMULATION_TURNS,
):
    character_hp = character.max_hp
    enemy_hp = enemy.max_hp
    turns = 0

    while (
        character_hp > 0
        and enemy_hp > 0
        and turns < max_turns
    ):
        turns += 1

        player_damage = calculate_player_damage(
            character,
            enemy,
        )

        enemy_hp -= player_damage

        if enemy_hp <= 0:
            enemy_hp = 0
            break

        enemy_damage = calculate_enemy_damage(
            enemy,
            character,
        )

        character_hp -= enemy_damage

        if character_hp <= 0:
            character_hp = 0
            break

    return {
        "won": enemy_hp <= 0,
        "turns": turns,
        "remaining_hp": character_hp,
    }


def simulate_battles(
    character,
    enemy,
    attempts=500,
):
    if attempts < 1:
        raise ValueError(
            "Liczba symulacji musi być większa od zera."
        )

    wins = 0
    total_turns = 0
    total_winning_hp = 0

    for _ in range(attempts):
        result = simulate_battle(
            character,
            enemy,
        )

        total_turns += result["turns"]

        if result["won"]:
            wins += 1

            total_winning_hp += (
                result["remaining_hp"]
            )

    losses = attempts - wins
    win_rate = (wins / attempts) * 100

    if wins > 0:
        average_remaining_hp = (
            total_winning_hp / wins
        )
    else:
        average_remaining_hp = 0

    if character.max_hp > 0:
        remaining_hp_percentage = (
            average_remaining_hp
            / character.max_hp
        ) * 100
    else:
        remaining_hp_percentage = 0

    average_turns = (
        total_turns / attempts
    )

    balance_label = get_balance_label(
        win_rate,
        remaining_hp_percentage,
    )

    return {
        "attempts": attempts,
        "wins": wins,
        "losses": losses,
        "win_rate": round(win_rate, 1),
        "average_turns": round(
            average_turns,
            1,
        ),
        "average_remaining_hp": round(
            average_remaining_hp,
            1,
        ),
        "remaining_hp_percentage": round(
            remaining_hp_percentage,
            1,
        ),
        "balance_label": balance_label,
    }