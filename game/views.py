from django.shortcuts import render, redirect, get_object_or_404
from .models import Character, Enemy, Battle
from .combat import process_turn


def character_list(request):
    characters = Character.objects.all()
    enemies  = Enemy.objects.all()
    return render(request, "game/character_list.html", {
        "characters": characters,
        "enemies": enemies ,
    })


def start_battle(request, character_id, enemy_id):
    character = get_object_or_404(Character, id=character_id)
    enemy = get_object_or_404(Enemy, id=enemy_id)

    battle = Battle.objects.create(
        character=character,
        enemy=enemy,
        character_current_hp=character.current_hp,
        enemy_current_hp=enemy.max_hp,
    )

    return redirect("game:battle_detail", battle_id=battle.id)


def battle_detail(request, battle_id):
    battle = get_object_or_404(Battle, id=battle_id)
    return render(request, "game/battle_detail.html", {
        "battle": battle
    })


def battle_attack(request, battle_id):
    battle = get_object_or_404(Battle, id=battle_id)
    process_turn(battle)
    return redirect("game:battle_detail", battle_id=battle.id)
