from django.urls import path

from . import views

app_name = "game"

urlpatterns = [

    path(
        "register/",
        views.register,
        name="register",
    ),

    path(
        "",
        views.character_list,
        name="character_list",
    ),

    path(
        "battle/setup/<int:character_id>/",
        views.battle_setup,
        name="battle_setup",
    ),

    path(
        "battle/setup/<int:character_id>/reset/",
        views.rest_character,
        name="rest_character",
    ),

    path(
        "battle/start/<int:character_id>/<int:enemy_id>/",
        views.start_battle,
        name="start_battle",
    ),

    path(
        "battle/<int:battle_id>/",
        views.battle_detail,
        name="battle_detail",
    ),

    path(
        "battle/<int:battle_id>/attack/",
        views.battle_attack,
        name="battle_attack",
    ),

    path(
        "battle/<int:battle_id>/skill/",
        views.battle_skill,
        name="battle_skill",
    ),

    path(
        "battle/<int:battle_id>/use-potion/<int:inventory_item_id>/",
        views.battle_use_potion,
        name="battle_use_potion",
    ),

    path(
        "shop/<int:character_id>/",
        views.shop_detail,
        name="shop_detail",
    ),

    path(
        "shop/<int:character_id>/buy/<int:item_id>/",
        views.shop_buy,
        name="shop_buy",
    ),

    path(
        "shop/<int:character_id>/sell/<int:item_id>/",
        views.shop_sell,
        name="shop_sell",
    ),

    path(
        "<int:character_id>/equipment/",
        views.equipment_detail,
        name="equipment_detail",
    ),

    path(
        "<int:character_id>/equip/<int:item_id>/",
        views.equip_item,
        name="equip_item",
    ),

    path(
        "<int:character_id>/unequip/<str:slot_name>/",
        views.unequip_item,
        name="unequip_item",
    ),
]
