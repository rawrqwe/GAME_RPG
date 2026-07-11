from django.urls import path
from . import views

app_name = "game"

urlpatterns = [
    path("", views.character_list, name="character_list"),

    #walka
    path("battle/start/<int:character_id>/<int:enemy_id>/", views.start_battle, name="start_battle"),
    path("battle/<int:battle_id>/", views.battle_detail, name="battle_detail"),
    path("battle/<int:battle_id>/attack/", views.battle_attack, name="battle_attack"),

    #sklep
    path("shop/<int:character_id>/", views.shop_detail, name="shop_detail"),
    path("shop/<int:character_id>/buy/<int:item_id>/", views.shop_buy, name="shop_buy"),
    path("shop/<int:character_id>/sell/<int:item_id>/", views.shop_sell, name="shop_sell"),
]