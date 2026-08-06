from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import (
    login_required,
)
from django.http import Http404
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)
from django.views.decorators.http import (
    require_POST,
)

from .combat import (
    get_character_skill,
    process_skill,
    process_turn,
    use_potion,
)
from .forms import (
    CharacterCreateForm,
    RegistrationForm,
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

VALID_EQUIPMENT_SLOTS = {
    "weapon",
    "shield",
    "helmet",
    "armor",
    "leggings",
    "gloves",
    "boots",
}
def register(request):
    if request.user.is_authenticated:
        return redirect(
            "game:character_list"
        )

    if request.method == "POST":
        form = RegistrationForm(
            request.POST,
        )

        if form.is_valid():
            user = form.save()

            login(
                request,
                user,
            )

            messages.success(
                request,
                "Konto zostało utworzone. "
                "Teraz utwórz swoją pierwszą "
                "postać.",
            )

            return redirect(
                "game:character_create"
            )
    else:
        form = RegistrationForm()

    return render(
        request,
        "registration/register.html",
        {
            "form": form,
        },
    )

def get_owned_character(
    request,
    character_id,
):
    return get_object_or_404(
        Character,
        id=character_id,
        owner=request.user,
    )


def get_owned_battle(
    request,
    battle_id,
):
    battles = Battle.objects.select_related(
        "character",
        "enemy",
    )

    return get_object_or_404(
        battles,
        id=battle_id,
        character__owner=request.user,
    )


@login_required
def character_list(request):
    characters = Character.objects.filter(
        owner=request.user,
    ).select_related(
        "race",
        "character_class",
    )

    return render(
        request,
        "game/character_list.html",
        {
            "characters": characters,
        }
    )
@login_required
def character_create(request):
    if request.method == "POST":
        form = CharacterCreateForm(
            request.POST,
            user=request.user,
        )

        if form.is_valid():
            character = form.save(
                commit=False,
            )

            character.owner = request.user
            character.save()

            messages.success(
                request,
                f"Postać {character.name} "
                f"została utworzona.",
            )

            return redirect(
                "game:character_list"
            )
    else:
        form = CharacterCreateForm(
            user=request.user,
        )

    return render(
        request,
        "game/character_create.html",
        {
            "form": form,
        },
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


@login_required
@require_POST
def start_battle(
    request,
    character_id,
    enemy_id,
):
    character = get_owned_character(
        request,
        character_id,
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


@login_required
def battle_detail(request, battle_id):
    battle = get_owned_battle(
        request,
        battle_id,
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
    ).select_related("item")

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


@login_required
@require_POST
def battle_attack(request, battle_id):
    battle = get_owned_battle(
        request,
        battle_id,
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


@login_required
@require_POST
def battle_skill(request, battle_id):
    battle = get_owned_battle(
        request,
        battle_id,
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


@login_required
@require_POST
def battle_use_potion(
    request,
    battle_id,
    inventory_item_id,
):
    battle = get_owned_battle(
        request,
        battle_id,
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


@login_required
def battle_setup(request, character_id):
    character = get_owned_character(
        request,
        character_id,
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


@login_required
@require_POST
def rest_character(
    request,
    character_id,
):
    character = get_owned_character(
        request,
        character_id,
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


@login_required
def shop_detail(request, character_id):
    character = get_owned_character(
        request,
        character_id,
    )

    items = Item.objects.all().order_by(
        "name",
    )

    inventory_items = (
        InventoryItem.objects.filter(
            character=character,
        )
        .select_related("item")
        .order_by(
            "item__type",
            "item__name",
        )
    )

    error_message = request.GET.get(
        "error",
    )

    category_by_item_type = {
        Item.Type.SWORD: "Broń",
        Item.Type.BOW: "Broń",
        Item.Type.STAFF: "Broń",

        Item.Type.SHIELD: "Tarcze",
        Item.Type.HELMET: "Hełmy",
        Item.Type.ARMOR: "Pancerze",
        Item.Type.LEGGINGS: "Spodnie",
        Item.Type.GLOVES: "Rękawice",
        Item.Type.BOOTS: "Buty",

        Item.Type.POTION: "Mikstury",
        Item.Type.MATERIAL: "Materiały",
        Item.Type.QUEST_ITEM: (
            "Przedmioty fabularne"
        ),
    }

    shop_categories = {
        "Broń": [],
        "Tarcze": [],
        "Hełmy": [],
        "Pancerze": [],
        "Spodnie": [],
        "Rękawice": [],
        "Buty": [],
        "Mikstury": [],
        "Materiały": [],
        "Przedmioty fabularne": [],
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

        category_name = (
            category_by_item_type.get(
                item.type,
                "Pozostałe przedmioty",
            )
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
        },
    )


@login_required
@require_POST
def shop_buy(
    request,
    character_id,
    item_id,
):
    character = get_owned_character(
        request,
        character_id,
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


@login_required
@require_POST
def shop_sell(
    request,
    character_id,
    item_id,
):
    character = get_owned_character(
        request,
        character_id,
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


@login_required
@require_POST
def equip_item(
    request,
    character_id,
    item_id,
):
    character = get_owned_character(
        request,
        character_id,
    )

    inventory_item = get_object_or_404(
        InventoryItem.objects.select_related(
            "item",
        ),
        character=character,
        item_id=item_id,
    )

    item = inventory_item.item

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


@login_required
@require_POST
def unequip_item(
    request,
    character_id,
    slot_name,
):
    character = get_owned_character(
        request,
        character_id,
    )

    if slot_name not in VALID_EQUIPMENT_SLOTS:
        raise Http404(
            "Nieprawidłowy slot wyposażenia."
        )

    character.equipment.unequip_slot(
        slot_name,
    )

    return redirect(
        "game:equipment_detail",
        character_id=character_id,
    )


@login_required
def equipment_detail(
    request,
    character_id,
):
    character = get_owned_character(
        request,
        character_id,
    )

    inventory_items = (
        InventoryItem.objects.filter(
            character=character,
        ).select_related("item")
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