from django.shortcuts import render, redirect, get_object_or_404

from .combat import process_turn
from .models import Character, Item, InventoryItem
from .models import Enemy, Battle
from .shop import buy_item, ShopError, sell_item


def character_list(request):
    characters = Character.objects.all()
    enemies = Enemy.objects.all()
    return render(request, "game/character_list.html", {
        "characters": characters,
        "enemies": enemies,
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


def shop_detail(request, character_id):
    character = get_object_or_404(Character, id=character_id)
    items = Item.objects.all()
    inventory_items = InventoryItem.objects.filter(character=character)

    error_message = request.GET.get('error')

    shop_items = []
    for item in items:
        can_afford = character.gold >= item.buy_price
        meets_level = character.level >= item.required_level
        shop_items.append({
            "item":item,
            "can_buy": can_afford and meets_level,
            "can_afford": can_afford,
            "meets_level": meets_level,
        })
    return render(request, "game/shop_detail.html", {
        "character": character,
        "shop_items": shop_items,
        "inventory_items": inventory_items,
        "error_message": error_message,
    })


def shop_buy(request, character_id, item_id):
    character = get_object_or_404(Character, id=character_id)
    item = get_object_or_404(Item, id=item_id)

    try:
        buy_item(character, item, quantity=1)
    except ShopError as e:
        return redirect(f"/game/shop/{character_id}/?error={e}")

    return redirect("game:shop_detail", character_id=character_id)


def shop_sell(request, character_id, item_id):
    character = get_object_or_404(Character, id=character_id)
    item = get_object_or_404(Item, id=item_id)

    try:
        sell_item(character, item, quantity=1)
    except ShopError as e:
        return redirect(f"/game/shop/{character_id}/?error={e}")

    return redirect("game:shop_detail", character_id=character_id)
