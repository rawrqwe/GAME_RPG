from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import (
    Battle,
    Character,
    CharacterClass,
    Enemy,
    InventoryItem,
    Item,
    Race,
)


class SecurityTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="owner",
            password="test-password",
        )

        self.other_user = (
            User.objects.create_user(
                username="other-user",
                password="test-password",
            )
        )

        race = Race.objects.create(
            name="Rasa bezpieczeństwa",
        )

        character_class = (
            CharacterClass.objects.create(
                name="Klasa bezpieczeństwa",
                base_hp=100,
                base_mana=30,
                base_strength=10,
                base_agility=10,
                base_intelligence=10,
                hp_growth=10,
                mana_growth=5,
                strength_growth=1,
                agility_growth=1,
                intelligence_growth=1,
            )
        )

        self.character = Character.objects.create(
            owner=self.owner,
            name="Moja postać",
            race=race,
            character_class=character_class,
        )

        self.foreign_character = (
            Character.objects.create(
                owner=self.other_user,
                name="Cudza postać",
                race=race,
                character_class=character_class,
            )
        )

        self.enemy = Enemy.objects.create(
            name="Przeciwnik bezpieczeństwa",
            level=1,
            max_hp=50,
            attack=5,
            defense=2,
        )

        self.battle = Battle.objects.create(
            character=self.character,
            enemy=self.enemy,
            character_current_hp=100,
            character_current_mana=30,
            enemy_current_hp=50,
        )

        self.foreign_battle = (
            Battle.objects.create(
                character=self.foreign_character,
                enemy=self.enemy,
                character_current_hp=100,
                character_current_mana=30,
                enemy_current_hp=50,
            )
        )

        self.item = Item.objects.create(
            name="Miecz bezpieczeństwa",
            type=Item.Type.SWORD,
            power=5,
            buy_price=10,
            sell_price=4,
        )

        self.potion = Item.objects.create(
            name="Mikstura bezpieczeństwa",
            type=Item.Type.POTION,
            heal_amount=20,
        )

        self.inventory_potion = (
            InventoryItem.objects.create(
                character=self.character,
                item=self.potion,
                quantity=1,
            )
        )

        self.client.force_login(
            self.owner,
        )

    def test_anonymous_user_is_redirected_to_login(
        self,
    ):
        self.client.logout()

        response = self.client.get(
            reverse("game:character_list")
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.assertIn(
            "/accounts/login/",
            response.url,
        )

    def test_character_list_only_shows_owned_characters(
        self,
    ):
        response = self.client.get(
            reverse("game:character_list")
        )

        self.assertContains(
            response,
            "Moja postać",
        )

        self.assertNotContains(
            response,
            "Cudza postać",
        )

    def test_cannot_access_foreign_character_pages(
        self,
    ):
        get_urls = [
            reverse(
                "game:battle_setup",
                args=[self.foreign_character.id],
            ),
            reverse(
                "game:shop_detail",
                args=[self.foreign_character.id],
            ),
            reverse(
                "game:equipment_detail",
                args=[self.foreign_character.id],
            ),
        ]

        for url in get_urls:
            with self.subTest(url=url):
                response = self.client.get(url)

                self.assertEqual(
                    response.status_code,
                    404,
                )

        post_urls = [
            reverse(
                "game:start_battle",
                args=[
                    self.foreign_character.id,
                    self.enemy.id,
                ],
            ),
            reverse(
                "game:rest_character",
                args=[self.foreign_character.id],
            ),
        ]

        for url in post_urls:
            with self.subTest(url=url):
                response = self.client.post(url)

                self.assertEqual(
                    response.status_code,
                    404,
                )

    def test_cannot_access_or_modify_foreign_battle(
        self,
    ):
        detail_response = self.client.get(
            reverse(
                "game:battle_detail",
                args=[self.foreign_battle.id],
            )
        )

        attack_response = self.client.post(
            reverse(
                "game:battle_attack",
                args=[self.foreign_battle.id],
            )
        )

        skill_response = self.client.post(
            reverse(
                "game:battle_skill",
                args=[self.foreign_battle.id],
            )
        )

        self.assertEqual(
            detail_response.status_code,
            404,
        )

        self.assertEqual(
            attack_response.status_code,
            404,
        )

        self.assertEqual(
            skill_response.status_code,
            404,
        )

    def test_actions_reject_get_requests(self):
        InventoryItem.objects.create(
            character=self.character,
            item=self.item,
            quantity=1,
        )

        urls = [
            reverse(
                "game:start_battle",
                args=[
                    self.character.id,
                    self.enemy.id,
                ],
            ),
            reverse(
                "game:rest_character",
                args=[self.character.id],
            ),
            reverse(
                "game:battle_attack",
                args=[self.battle.id],
            ),
            reverse(
                "game:battle_skill",
                args=[self.battle.id],
            ),
            reverse(
                "game:battle_use_potion",
                args=[
                    self.battle.id,
                    self.inventory_potion.id,
                ],
            ),
            reverse(
                "game:shop_buy",
                args=[
                    self.character.id,
                    self.item.id,
                ],
            ),
            reverse(
                "game:shop_sell",
                args=[
                    self.character.id,
                    self.item.id,
                ],
            ),
            reverse(
                "game:equip_item",
                args=[
                    self.character.id,
                    self.item.id,
                ],
            ),
            reverse(
                "game:unequip_item",
                args=[
                    self.character.id,
                    "weapon",
                ],
            ),
        ]

        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)

                self.assertEqual(
                    response.status_code,
                    405,
                )

    def test_cannot_equip_item_not_in_inventory(
        self,
    ):
        response = self.client.post(
            reverse(
                "game:equip_item",
                args=[
                    self.character.id,
                    self.item.id,
                ],
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )

        self.character.equipment.refresh_from_db()

        self.assertIsNone(
            self.character.equipment.weapon,
        )