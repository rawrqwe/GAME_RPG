from django.contrib import messages
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)
from django.views.decorators.http import require_POST

from .combat import (
    get_character_skill,
    process_skill,
    process_turn,
    use_potion,
)
from .models import (
    Battle,
    Character,
    Enemy,
    InventoryItem,
    Item,
)
from .shop import (
    ShopError,
    buy_item,
    sell_item,
)


MAX_ENEMY_LEVEL_ADVANTAGE = 1


def character_list(request):
    characters = Character.objects.all()
    enemies = Enemy.objects.all()

    return render(
        request,
        "game/character_list.html",
        {
            "characters": characters,
            "enemies": enemies,
        }
    )


def can_character_fight_enemy(
    character,
    enemy,
):
    maximum_enemy_level = (
        character.level
        + MAX_ENEMY_LEVEL_ADVANTAGE
    )

    return (
        enemy.level
        <= maximum_enemy_level
    )


def get_enemy_difficulty(
    character,
    enemy,
):
    level_difference = (
        enemy.level
        - character.level
    )

    if not can_character_fight_enemy(
        character,
        enemy,
    ):
        return {
            "label": "Zablokowany",
            "css_class": (
                "difficulty-locked"
            ),
            "available": False,
        }

    if level_difference < 0:
        return {
            "label": "Łatwy",
            "css_class": (
                "difficulty-easy"
            ),
            "available": True,
        }

    if level_difference == 0:
        return {
            "label": "Równy",
            "css_class": (
                "difficulty-equal"
            ),
            "available": True,
        }

    return {
        "label": "Trudny",
        "css_class": (
            "difficulty-hard"
        ),
        "available": True,
    }


@require_POST
def start_battle(
    request,
    character_id,
    enemy_id,
):
    character = get_object_or_404(
        Character,
        id=character_id,
    )

    enemy = get_object_or_404(
        Enemy,
        id=enemy_id,
    )

    if not can_character_fight_enemy(
        character,
        enemy,
    ):
        messages.error(
            request,
            "Ten przeciwnik ma zbyt wysoki poziom.",
        )

        return redirect(
            "game:battle_setup",
            character_id=character.id,
        )

    if character.current_hp <= 0:
        messages.error(
            request,
            "Postać nie ma punktów życia. "
            "Odpocznij przed rozpoczęciem walki.",
        )

        return redirect(
            "game:battle_setup",
            character_id=character.id,
        )

    battle = Battle.objects.create(
        character=character,
        enemy=enemy,
        character_current_hp=(
            character.current_hp
        ),
        character_current_mana=(
            character.current_mana
        ),
        enemy_current_hp=enemy.max_hp,
    )

    return redirect(
        "game:battle_detail",
        battle_id=battle.id,
    )


def battle_detail(request, battle_id):
    battle = get_object_or_404(
        Battle,
        id=battle_id,
    )

    session_key = (
        f"battle_{battle.id}_turn_result"
    )

    turn_result = request.session.pop(
        session_key,
        None,
    )

    potions = InventoryItem.objects.filter(
        character=battle.character,
        item__type=Item.Type.POTION,
    )

    skill = get_character_skill(
        battle.character,
    )

    return render(
        request,
        "game/battle_detail.html",
        {
            "battle": battle,
            "potions": potions,
            "turn_result": turn_result,
            "skill": skill,
        }
    )


def battle_attack(request, battle_id):
    battle = get_object_or_404(
        Battle,
        id=battle_id,
    )

    result = process_turn(battle)

    session_key = (
        f"battle_{battle.id}_turn_result"
    )

    request.session[session_key] = result

    return redirect(
        "game:battle_detail",
        battle_id=battle.id,
    )


@require_POST
def battle_skill(request, battle_id):
    battle = get_object_or_404(
        Battle,
        id=battle_id,
    )

    result = process_skill(battle)

    session_key = (
        f"battle_{battle.id}_turn_result"
    )

    request.session[session_key] = result

    return redirect(
        "game:battle_detail",
        battle_id=battle.id,
    )


def battle_use_potion(
    request,
    battle_id,
    inventory_item_id,
):
    battle = get_object_or_404(
        Battle,
        id=battle_id,
    )

    inventory_item = get_object_or_404(
        InventoryItem,
        id=inventory_item_id,
        character=battle.character,
        item__type=Item.Type.POTION,
    )

    result = use_potion(
        battle,
        inventory_item,
    )

    session_key = (
        f"battle_{battle.id}_turn_result"
    )

    request.session[session_key] = result

    return redirect(
        "game:battle_detail",
        battle_id=battle.id,
    )


def battle_setup(request, character_id):
    character = get_object_or_404(
        Character,
        id=character_id,
    )

    enemies = Enemy.objects.all().order_by(
        "level",
        "is_boss",
        "name",
    )

    enemy_entries = []

    for enemy in enemies:
        difficulty = get_enemy_difficulty(
            character,
            enemy,
        )

        enemy_entries.append({
            "enemy": enemy,
            "difficulty_label": (
                difficulty["label"]
            ),
            "difficulty_class": (
                difficulty["css_class"]
            ),
            "available": (
                difficulty["available"]
            ),
        })

    return render(
        request,
        "game/battle_setup.html",
        {
            "character": character,
            "enemy_entries": enemy_entries,
        }
    )


@require_POST
def rest_character(
    request,
    character_id,
):
    character = get_object_or_404(
        Character,
        id=character_id,
    )

    character.current_hp = (
        character.total_max_hp
    )

    character.current_mana = (
        character.total_max_mana
    )

    character.save(
        update_fields=[
            "current_hp",
            "current_mana",
        ]
    )

    messages.success(
        request,
        "Postać odpoczęła i odzyskała siły.",
    )

    return redirect(
        "game:battle_setup",
        character_id=character.id,
    )


def shop_detail(request, character_id):
    character = get_object_or_404(
        Character,
        id=character_id,
    )

    items = Item.objects.all().order_by(
        "name",
    )

    inventory_items = (
        InventoryItem.objects.filter(
            character=character,
        ).select_related("item")
    )

    error_message = request.GET.get(
        "error",
    )

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
        can_afford = (
            character.gold
            >= item.buy_price
        )

        meets_level = (
            character.level
            >= item.required_level
        )

        entry = {
            "item": item,
            "can_buy": (
                can_afford
                and meets_level
            ),
            "can_afford": can_afford,
            "meets_level": meets_level,
        }

        if item.type in weapon_types:
            category_name = "Broń"

        elif item.type in armor_types:
            category_name = (
                "Elementy pancerza"
            )

        elif item.type == Item.Type.POTION:
            category_name = "Mikstury"

        else:
            category_name = (
                "Pozostałe przedmioty"
            )

        shop_categories[
            category_name
        ].append(entry)

    shop_categories = {
        category_name: entries
        for category_name, entries
        in shop_categories.items()
        if entries
    }

    return render(
        request,
        "game/shop_detail.html",
        {
            "character": character,
            "shop_categories": (
                shop_categories
            ),
            "inventory_items": (
                inventory_items
            ),
            "error_message": (
                error_message
            ),
        }
    )


def shop_buy(
    request,
    character_id,
    item_id,
):
    character = get_object_or_404(
        Character,
        id=character_id,
    )

    item = get_object_or_404(
        Item,
        id=item_id,
    )

    try:
        buy_item(
            character,
            item,
            quantity=1,
        )
    except ShopError as error:
        return redirect(
            f"/game/shop/{character_id}/"
            f"?error={error}"
        )

    return redirect(
        "game:shop_detail",
        character_id=character_id,
    )


def shop_sell(
    request,
    character_id,
    item_id,
):
    character = get_object_or_404(
        Character,
        id=character_id,
    )

    item = get_object_or_404(
        Item,
        id=item_id,
    )

    try:
        sell_item(
            character,
            item,
            quantity=1,
        )
    except ShopError as error:
        return redirect(
            f"/game/shop/{character_id}/"
            f"?error={error}"
        )

    return redirect(
        "game:shop_detail",
        character_id=character_id,
    )


def equip_item(
    request,
    character_id,
    item_id,
):
    character = get_object_or_404(
        Character,
        id=character_id,
    )

    item = get_object_or_404(
        Item,
        id=item_id,
    )

    try:
        character.equipment.equip_item(
            item,
        )
    except ValueError as error:
        return redirect(
            f"/game/shop/{character_id}/"
            f"?error={error}"
        )

    return redirect(
        "game:equipment_detail",
        character_id=character_id,
    )


def unequip_item(
    request,
    character_id,
    slot_name,
):
    character = get_object_or_404(
        Character,
        id=character_id,
    )

    character.equipment.unequip_slot(
        slot_name,
    )

    return redirect(
        "game:equipment_detail",
        character_id=character_id,
    )


def equipment_detail(
    request,
    character_id,
):
    character = get_object_or_404(
        Character,
        id=character_id,
    )

    inventory_items = (
        InventoryItem.objects.filter(
            character=character,
        )
    )

    error_message = request.GET.get(
        "error",
    )

    return render(
        request,
        "game/equipment_detail.html",
        {
            "character": character,
            "inventory_items": (
                inventory_items
            ),
            "error_message": (
                error_message
            ),
        }
    )