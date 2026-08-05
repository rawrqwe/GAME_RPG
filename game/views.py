from django.shortcuts import render, redirect, get_object_or_404

from .combat import process_turn, use_potion
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

    turn_result = request.session.pop(f"battle_{battle.id}_turn_result", None)

    potions = InventoryItem.objects.filter(
        character=battle.character,
        item__type=Item.Type.POTION
    )

    return render(request, "game/battle_detail.html", {
        "battle": battle,
        "potions": potions,
        "turn_result": turn_result,
    })


def battle_attack(request, battle_id):
    battle = get_object_or_404(Battle, id=battle_id)
    result = process_turn(battle)
    request.session[f"battle_{battle.id}_turn_result"] = result
    return redirect("game:battle_detail", battle_id=battle.id)


def shop_detail(request, character_id):
    character = get_object_or_404(
        Character,
        id=character_id
    )

    items = Item.objects.all().order_by("name")

    inventory_items = InventoryItem.objects.filter(
        character=character
    ).select_related("item")

    error_message = request.GET.get("error")

    weapon_types = {
        Item.Type.SWORD,
        Item.Type.BOW,
        Item.Type.STAFF,
    }

    armor_types = {
        Item.Type.SHIELD,
        Item.Type.HELMET,
        Item.Type.ARMOR,
        Item.Type.LEGGINGS,
        Item.Type.GLOVES,
        Item.Type.BOOTS,
    }

    shop_categories = {
        "Broń": [],
        "Elementy pancerza": [],
        "Mikstury": [],
        "Pozostałe przedmioty": [],
    }

    for item in items:
        can_afford = character.gold >= item.buy_price
        meets_level = character.level >= item.required_level

        entry = {
            "item": item,
            "can_buy": can_afford and meets_level,
            "can_afford": can_afford,
            "meets_level": meets_level,
        }

        if item.type in weapon_types:
            category_name = "Broń"
        elif item.type in armor_types:
            category_name = "Elementy pancerza"
        elif item.type == Item.Type.POTION:
            category_name = "Mikstury"
        else:
            category_name = "Pozostałe przedmioty"

        shop_categories[category_name].append(entry)

    shop_categories = {
        category_name: entries
        for category_name, entries in shop_categories.items()
        if entries
    }

    return render(request, "game/shop_detail.html", {
        "character": character,
        "shop_categories": shop_categories,
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


def equip_item(request, character_id, item_id):
    character = get_object_or_404(Character, id=character_id)
    item = get_object_or_404(Item, id=item_id)

    try:
        character.equipment.equip_item(item)
    except ValueError as e:
        return redirect(f"/game/shop/{character_id}/?error={e}")

    return redirect("game:equipment_detail", character_id=character_id)


def unequip_item(request, character_id, slot_name):
    character = get_object_or_404(Character, id=character_id)
    character.equipment.unequip_slot(slot_name)
    return redirect("game:equipment_detail", character_id=character_id)


def equipment_detail(request, character_id):
    character = get_object_or_404(Character, id=character_id)
    inventory_items = InventoryItem.objects.filter(character=character)
    error_message = request.GET.get('error')

    return render(request, "game/equipment_detail.html", {
        "character": character,
        "inventory_items": inventory_items,
        "error_message": error_message,
    })


def battle_use_potion(request, battle_id, inventory_item_id):
    battle = get_object_or_404(Battle, id=battle_id)
    inventory_item = get_object_or_404(
        InventoryItem,
        id=inventory_item_id,
        character=battle.character,
        item__type=Item.Type.POTION,
    )

    result = use_potion(battle, inventory_item)
    request.session[f"battle_{battle.id}_turn_result"] = result

    return redirect("game:battle_detail", battle_id=battle.id)


def battle_setup(request, character_id):
    character = get_object_or_404(
        Character,
        id=character_id
    )

    enemies = Enemy.objects.all().order_by(
        "level",
        "is_boss",
        "name",
    )

    return render(request, "game/battle_setup.html", {
        "character": character,
        "enemies": enemies,
    })
