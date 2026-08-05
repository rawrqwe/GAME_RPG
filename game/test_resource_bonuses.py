from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .combat import use_potion
from .models import (
    Battle,
    Character,
    CharacterClass,
    Enemy,
    InventoryItem,
    Item,
    Race,
)


class ResourceBonusTests(TestCase):
    def setUp(self):
        owner = User.objects.create_user(
            username="resource-tester",
        )

        race = Race.objects.create(
            name="Człowiek zasobów",
        )

        character_class = (
            CharacterClass.objects.create(
                name="Klasa zasobów",
                base_hp=100,
                base_mana=40,
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
            owner=owner,
            name="Tester zasobów",
            race=race,
            character_class=character_class,
        )

        self.hp_armor = Item.objects.create(
            name="Pancerz testowy HP",
            type=Item.Type.ARMOR,
            power=2,
            bonus_stat=Item.BonusStats.HP,
            bonus_value=20,
        )

        self.mana_staff = Item.objects.create(
            name="Laska testowa many",
            type=Item.Type.STAFF,
            power=2,
            bonus_stat=Item.BonusStats.MANA,
            bonus_value=30,
        )

    def equip_item(self, item):
        InventoryItem.objects.create(
            character=self.character,
            item=item,
            quantity=1,
        )

        self.character.equipment.equip_item(
            item,
        )

    def test_equipment_increases_max_hp_and_mana(
        self,
    ):
        self.equip_item(self.hp_armor)
        self.equip_item(self.mana_staff)

        self.assertEqual(
            self.character.total_max_hp,
            120,
        )

        self.assertEqual(
            self.character.total_max_mana,
            70,
        )

        self.assertEqual(
            self.character.current_hp,
            100,
        )

        self.assertEqual(
            self.character.current_mana,
            40,
        )

    @patch(
        "game.combat.random.randint",
        return_value=0,
    )
    def test_potion_uses_total_max_hp(
        self,
        mocked_randint,
    ):
        self.equip_item(self.hp_armor)

        self.character.current_hp = 90
        self.character.save(
            update_fields=["current_hp"],
        )

        potion = Item.objects.create(
            name="Mikstura testowa",
            type=Item.Type.POTION,
            heal_amount=50,
        )

        inventory_item = (
            InventoryItem.objects.create(
                character=self.character,
                item=potion,
                quantity=1,
            )
        )

        enemy = Enemy.objects.create(
            name="Słaby przeciwnik",
            max_hp=20,
            attack=1,
        )

        battle = Battle.objects.create(
            character=self.character,
            enemy=enemy,
            character_current_hp=90,
            enemy_current_hp=enemy.max_hp,
        )

        result = use_potion(
            battle,
            inventory_item,
        )

        battle.refresh_from_db()

        self.assertEqual(
            result["healed"],
            30,
        )

        self.assertEqual(
            battle.character_current_hp,
            119,
        )

    def test_rest_uses_total_resource_limits(
        self,
    ):
        self.equip_item(self.hp_armor)
        self.equip_item(self.mana_staff)

        self.character.current_hp = 1
        self.character.current_mana = 2

        self.character.save(
            update_fields=[
                "current_hp",
                "current_mana",
            ]
        )

        response = self.client.post(
            reverse(
                "game:rest_character",
                args=[self.character.id],
            )
        )

        self.character.refresh_from_db()

        self.assertEqual(
            response.status_code,
            302,
        )

        self.assertEqual(
            self.character.current_hp,
            120,
        )

        self.assertEqual(
            self.character.current_mana,
            70,
        )

    def test_unequip_clamps_current_hp(
        self,
    ):
        self.equip_item(self.hp_armor)

        self.character.current_hp = 120

        self.character.save(
            update_fields=["current_hp"],
        )

        self.character.equipment.unequip_slot(
            "armor",
        )

        self.character.refresh_from_db()

        self.assertEqual(
            self.character.total_max_hp,
            100,
        )

        self.assertEqual(
            self.character.current_hp,
            100,
        )