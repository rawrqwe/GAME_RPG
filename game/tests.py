from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .combat import process_turn, use_potion
from .models import (
    Battle,
    Character,
    CharacterClass,
    Enemy,
    InventoryItem,
    Item,
    Race,
)


class ProcessTurnTests(TestCase):
    def setUp(self):
        owner = User.objects.create_user(username="tester")

        race = Race.objects.create(
            name="Człowiek"
        )

        character_class = CharacterClass.objects.create(
            name="Wojownik",
            base_hp=100,
            base_mana=0,
            base_strength=10,
            base_agility=10,
            base_intelligence=5,
            hp_growth=10,
            mana_growth=0,
            strength_growth=2,
            agility_growth=1,
            intelligence_growth=0,
        )

        self.character = Character.objects.create(
            owner=owner,
            name="Bohater",
            race=race,
            character_class=character_class,
            strength=10,
        )

    @patch("game.combat.random.randint", return_value=0)
    def test_winning_turn_awards_rewards(self, mocked_randint):
        enemy = Enemy.objects.create(
            name="Szczur",
            max_hp=5,
            attack=1,
            defense=0,
            experience_reward=25,
            gold_reward=7,
        )

        battle = Battle.objects.create(
            character=self.character,
            enemy=enemy,
            character_current_hp=self.character.current_hp,
            enemy_current_hp=enemy.max_hp,
        )

        result = process_turn(battle)

        battle.refresh_from_db()
        self.character.refresh_from_db()

        self.assertEqual(battle.status, Battle.Status.WON)
        self.assertEqual(self.character.experience, 25)
        self.assertEqual(self.character.gold, 7)
        self.assertEqual(result["experience_reward"], 25)
        self.assertEqual(result["gold_reward"], 7)

    @patch("game.combat.random.randint", return_value=0)
    def test_winning_turn_reports_level_up(self, mocked_randint):
        self.character.experience = 90
        self.character.save()

        enemy = Enemy.objects.create(
            name="Goblin",
            max_hp=5,
            attack=1,
            defense=0,
            experience_reward=20,
            gold_reward=0,
        )

        battle = Battle.objects.create(
            character=self.character,
            enemy=enemy,
            character_current_hp=self.character.current_hp,
            enemy_current_hp=enemy.max_hp,
        )

        result = process_turn(battle)

        self.character.refresh_from_db()
        battle.refresh_from_db()

        self.assertEqual(battle.status, Battle.Status.WON)
        self.assertTrue(result["leveled_up"])
        self.assertEqual(self.character.level, 2)
        self.assertEqual(self.character.experience, 10)

    @patch("game.combat.random.randint", return_value=0)
    def test_ongoing_turn_does_not_award_rewards(self, mocked_randint):
        enemy = Enemy.objects.create(
            name="Ork",
            max_hp=30,
            attack=8,
            defense=2,
            experience_reward=50,
            gold_reward=15,
        )

        battle = Battle.objects.create(
            character=self.character,
            enemy=enemy,
            character_current_hp=self.character.current_hp,
            enemy_current_hp=enemy.max_hp,
        )

        result = process_turn(battle)

        battle.refresh_from_db()
        self.character.refresh_from_db()

        self.assertEqual(battle.status, Battle.Status.ONGOING)
        self.assertEqual(battle.enemy_current_hp, 22)
        self.assertEqual(battle.character_current_hp, 97)
        self.assertEqual(battle.turn_number, 2)

        self.assertEqual(self.character.experience, 0)
        self.assertEqual(self.character.gold, 0)
        self.assertEqual(result["experience_reward"], 0)
        self.assertEqual(result["gold_reward"], 0)
        self.assertFalse(result["leveled_up"])

    @patch("game.combat.random.randint", return_value=0)
    def test_losing_turn_sets_lose_status(self, mocked_randint):
        enemy = Enemy.objects.create(
            name="Ogr",
            max_hp=30,
            attack=20,
            defense=2,
            experience_reward=100,
            gold_reward=50,
        )

        battle = Battle.objects.create(
            character=self.character,
            enemy=enemy,
            character_current_hp=2,
            enemy_current_hp=enemy.max_hp,
        )

        result = process_turn(battle)

        battle.refresh_from_db()
        self.character.refresh_from_db()

        self.assertEqual(battle.status, Battle.Status.LOSE)
        self.assertEqual(battle.character_current_hp, 0)
        self.assertEqual(self.character.experience, 0)
        self.assertEqual(self.character.gold, 0)
        self.assertEqual(result["experience_reward"], 0)
        self.assertEqual(result["gold_reward"], 0)
        self.assertFalse(result["leveled_up"])

    @patch("game.combat.random.randint", return_value=0)
    def test_using_potion_heals_and_uses_one_item(self, mocked_randint):
        potion = Item.objects.create(
            name="Mikstura zdrowia",
            type=Item.Type.POTION,
            heal_amount=30,
        )

        inventory_item = InventoryItem.objects.create(
            character=self.character,
            item=potion,
            quantity=2,
        )

        enemy = Enemy.objects.create(
            name="Wilk",
            max_hp=20,
            attack=8,
            defense=0,
        )

        battle = Battle.objects.create(
            character=self.character,
            enemy=enemy,
            character_current_hp=50,
            enemy_current_hp=enemy.max_hp,
        )

        result = use_potion(battle, inventory_item)

        battle.refresh_from_db()
        inventory_item.refresh_from_db()

        self.assertEqual(result["healed"], 30)
        self.assertEqual(result["enemy_damage"], 3)
        self.assertEqual(battle.character_current_hp, 77)
        self.assertEqual(battle.turn_number, 2)
        self.assertEqual(inventory_item.quantity, 1)

    @patch("game.combat.random.randint", return_value=0)
    def test_potion_reports_actual_healing(self, mocked_randint):
        potion = Item.objects.create(
            name="Duża mikstura zdrowia",
            type=Item.Type.POTION,
            heal_amount=30,
        )

        inventory_item = InventoryItem.objects.create(
            character=self.character,
            item=potion,
            quantity=1,
        )

        enemy = Enemy.objects.create(
            name="Wilk",
            max_hp=20,
            attack=8,
            defense=0,
        )

        battle = Battle.objects.create(
            character=self.character,
            enemy=enemy,
            character_current_hp=95,
            enemy_current_hp=enemy.max_hp,
        )

        result = use_potion(battle, inventory_item)

        battle.refresh_from_db()

        self.assertEqual(result["healed"], 5)
        self.assertEqual(battle.character_current_hp, 97)
        self.assertFalse(
            InventoryItem.objects.filter(id=inventory_item.id).exists()
        )

    def test_cannot_use_another_characters_potion(self):
        second_character = Character.objects.create(
            owner=self.character.owner,
            name="Drugi bohater",
            race=self.character.race,
            character_class=self.character.character_class,
        )

        potion = Item.objects.create(
            name="Cudza mikstura",
            type=Item.Type.POTION,
            heal_amount=20,
        )

        foreign_inventory_item = InventoryItem.objects.create(
            character=second_character,
            item=potion,
            quantity=1,
        )

        enemy = Enemy.objects.create(
            name="Szkielet",
            max_hp=20,
            attack=5,
        )

        battle = Battle.objects.create(
            character=self.character,
            enemy=enemy,
            character_current_hp=50,
            enemy_current_hp=enemy.max_hp,
        )

        response = self.client.post(
            reverse(
                "game:battle_use_potion",
                args=[battle.id, foreign_inventory_item.id],
            )
        )

        self.assertEqual(response.status_code, 404)

    def test_cannot_use_non_potion_item(self):
        sword = Item.objects.create(
            name="Miecz",
            type=Item.Type.SWORD,
            power=5,
        )

        inventory_item = InventoryItem.objects.create(
            character=self.character,
            item=sword,
            quantity=1,
        )

        enemy = Enemy.objects.create(
            name="Szkielet",
            max_hp=20,
            attack=5,
        )

        battle = Battle.objects.create(
            character=self.character,
            enemy=enemy,
            character_current_hp=50,
            enemy_current_hp=enemy.max_hp,
        )

        response = self.client.post(
            reverse(
                "game:battle_use_potion",
                args=[battle.id, inventory_item.id],
            )
        )

        self.assertEqual(response.status_code, 404)

    @patch("game.combat.random.randint", return_value=0)
    def test_attack_result_is_stored_in_session_once(self, mocked_randint):
        enemy = Enemy.objects.create(
            name="Ork",
            max_hp=30,
            attack=8,
            defense=2,
        )

        battle = Battle.objects.create(
            character=self.character,
            enemy=enemy,
            character_current_hp=self.character.current_hp,
            enemy_current_hp=enemy.max_hp,
        )

        session_key = f"battle_{battle.id}_turn_result"

        self.client.post(
            reverse("game:battle_attack", args=[battle.id])
        )

        self.assertIn(session_key, self.client.session)

        response = self.client.get(
            reverse("game:battle_detail", args=[battle.id])
        )

        self.assertIsNotNone(response.context["turn_result"])
        self.assertNotIn(session_key, self.client.session)
