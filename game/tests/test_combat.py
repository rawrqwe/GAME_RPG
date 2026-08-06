from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from game.combat import (
    calculate_enemy_damage,
    calculate_player_damage,
    process_turn,
    use_potion,
)

from game.models import (
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
        self.owner = User.objects.create_user(
            username="tester"
        )

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
            owner=self.owner,
            name="Bohater",
            race=race,
            character_class=character_class,
            strength=10,
        )
        self.client.force_login(
            self.owner,
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
        self.assertEqual(battle.character_current_hp, 94)
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
        self.assertEqual(result["enemy_damage"], 6)
        self.assertEqual(battle.character_current_hp, 74)
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
        self.assertEqual(battle.character_current_hp, 94)
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

    @patch("game.combat.random.randint", return_value=0)
    def test_weapon_uses_correct_character_stat(self, mocked_randint):
        self.character.strength = 16
        self.character.agility = 18
        self.character.intelligence = 20
        self.character.save()

        enemy = Enemy.objects.create(
            name="Cel treningowy",
            max_hp=100,
            defense=4,
        )

        weapon_cases = [
            {
                "name": "Miecz testowy",
                "type": Item.Type.SWORD,
                "power": 5,
                "expected_damage": 17,
            },
            {
                "name": "Łuk testowy",
                "type": Item.Type.BOW,
                "power": 6,
                "expected_damage": 20,
            },
            {
                "name": "Laska testowa",
                "type": Item.Type.STAFF,
                "power": 4,
                "expected_damage": 20,
            },
        ]

        for weapon_case in weapon_cases:
            with self.subTest(weapon=weapon_case["name"]):
                weapon = Item.objects.create(
                    name=weapon_case["name"],
                    type=weapon_case["type"],
                    power=weapon_case["power"],
                )

                self.character.equipment.weapon = weapon
                self.character.equipment.save()

                damage = calculate_player_damage(
                    self.character,
                    enemy
                )

                self.assertEqual(
                    damage,
                    weapon_case["expected_damage"]
                )

    @patch("game.combat.random.randint", return_value=0)
    def test_armor_and_agility_reduce_enemy_damage(self,mocked_randint):
        self.character.agility = 12
        self.character.save()

        armor = Item.objects.create(
            name="Pancerz testowy",
            type=Item.Type.ARMOR,
            power=9,
        )

        self.character.equipment.armor = armor
        self.character.equipment.save()

        enemy = Enemy.objects.create(
            name="Silny przeciwnik",
            attack=16,
        )

        damage = calculate_enemy_damage(
            enemy,
            self.character
        )

        self.assertEqual(damage, 12)

    def test_character_class_can_only_equip_allowed_weapon_type(self):
        bow = Item.objects.create(
            name="Łuk klasowy",
            type=Item.Type.BOW,
            power=5,
        )

        sword = Item.objects.create(
            name="Niedozwolony miecz",
            type=Item.Type.SWORD,
            power=5,
        )

        self.character.character_class.starting_weapon = bow
        self.character.character_class.save()

        InventoryItem.objects.create(
            character=self.character,
            item=bow,
            quantity=1,
        )

        self.character.equipment.equip_item(bow)
        self.character.equipment.refresh_from_db()

        self.assertEqual(
            self.character.equipment.weapon,
            bow
        )

        InventoryItem.objects.create(
            character=self.character,
            item=sword,
            quantity=1,
        )

        with self.assertRaises(ValueError):
            self.character.equipment.equip_item(sword)

        self.character.equipment.refresh_from_db()

        self.assertEqual(
            self.character.equipment.weapon,
            bow
        )
    def test_character_cannot_equip_item_above_its_level(self):
        sword = Item.objects.create(
            name="Miecz wysokiego poziomu",
            type=Item.Type.SWORD,
            power=20,
            required_level=5,
        )

        self.character.character_class.starting_weapon = sword
        self.character.character_class.save()

        InventoryItem.objects.create(
            character=self.character,
            item=sword,
            quantity=1,
        )

        with self.assertRaises(ValueError):
            self.character.equipment.equip_item(sword)

        self.character.equipment.refresh_from_db()

        self.assertIsNone(
            self.character.equipment.weapon
        )

    @patch("game.combat.random.randint", return_value=0)
    def test_equipment_bonus_increases_weapon_damage(self,mocked_randint):
        self.character.agility = 18
        self.character.save()

        bow = Item.objects.create(
            name="Łuk z bonusem",
            type=Item.Type.BOW,
            power=6,
            bonus_stat=Item.BonusStats.AGILITY,
            bonus_value=4,
        )

        gloves = Item.objects.create(
            name="Rękawice łucznika",
            type=Item.Type.GLOVES,
            power=0,
            bonus_stat=Item.BonusStats.AGILITY,
            bonus_value=2,
        )

        self.character.equipment.weapon = bow
        self.character.equipment.gloves = gloves
        self.character.equipment.save()

        enemy = Enemy.objects.create(
            name="Cel treningowy",
            defense=4,
        )

        damage = calculate_player_damage(
            self.character,
            enemy
        )

        self.assertEqual(damage, 26)

    def test_new_character_uses_class_and_race_statistics(self):
        race = Race.objects.create(
            name="Rasa testowa",
            hp_bonus=10,
            mana_bonus=5,
            strength_bonus=3,
            agility_bonus=2,
            intelligence_bonus=4,
        )

        character_class = CharacterClass.objects.create(
            name="Klasa testowa",
            base_hp=120,
            base_mana=40,
            base_strength=14,
            base_agility=8,
            base_intelligence=6,
            hp_growth=10,
            mana_growth=5,
            strength_growth=2,
            agility_growth=1,
            intelligence_growth=1,
        )

        character = Character.objects.create(
            owner=self.character.owner,
            name="Nowa postać",
            race=race,
            character_class=character_class,
        )

        self.assertEqual(character.max_hp, 130)
        self.assertEqual(character.current_hp, 130)

        self.assertEqual(character.max_mana, 45)
        self.assertEqual(character.current_mana, 45)

        self.assertEqual(character.strength, 17)
        self.assertEqual(character.agility, 10)
        self.assertEqual(character.intelligence, 10)

    def test_only_sword_class_can_equip_shield(self):
        bow = Item.objects.create(
            name="Łuk startowy",
            type=Item.Type.BOW,
            power=4,
        )

        shield = Item.objects.create(
            name="Tarcza testowa",
            type=Item.Type.SHIELD,
            power=5,
        )

        self.character.character_class.starting_weapon = bow
        self.character.character_class.save()

        InventoryItem.objects.create(
            character=self.character,
            item=shield,
            quantity=1,
        )

        with self.assertRaises(ValueError):
            self.character.equipment.equip_item(
                shield
            )

        self.character.equipment.refresh_from_db()

        self.assertIsNone(
            self.character.equipment.shield
        )

    def test_fractional_growth_accumulates_between_levels(self):
        character_class = CharacterClass.objects.create(
            name="Klasa z ułamkowym wzrostem",
            base_hp=100,
            base_mana=10,
            base_strength=10,
            base_agility=10,
            base_intelligence=10,
            hp_growth=3.5,
            mana_growth=2.5,
            strength_growth=2.5,
            agility_growth=1.5,
            intelligence_growth=0.5,
        )

        character = Character.objects.create(
            owner=self.character.owner,
            name="Rosnąca postać",
            race=self.character.race,
            character_class=character_class,
        )

        character.experience = 300
        leveled_up = character.try_level_up()

        self.assertTrue(leveled_up)
        self.assertEqual(character.level, 3)
        self.assertEqual(character.experience, 0)

        self.assertEqual(character.max_hp, 107)
        self.assertEqual(character.max_mana, 15)

        self.assertEqual(character.strength, 15)
        self.assertEqual(character.agility, 13)
        self.assertEqual(character.intelligence, 11)

        self.assertEqual(
            character.current_hp,
            character.max_hp
        )

        self.assertEqual(
            character.current_mana,
            character.max_mana
        )

    @patch("game.combat.random.randint", return_value=0)
    def test_turn_updates_character_current_hp(self,mocked_randint):
        enemy = Enemy.objects.create(
            name="Przeciwnik testowy",
            max_hp=30,
            attack=8,
            defense=2,
        )

        battle = Battle.objects.create(
            character=self.character,
            enemy=enemy,
            character_current_hp=(
                self.character.current_hp
            ),
            enemy_current_hp=enemy.max_hp,
        )

        process_turn(battle)

        battle.refresh_from_db()
        self.character.refresh_from_db()

        self.assertEqual(
            self.character.current_hp,
            battle.character_current_hp
        )

        self.assertEqual(
            self.character.current_hp,
            94
        )

    def test_rest_restores_health_and_mana(self):
        self.character.current_hp = 1
        self.character.current_mana = 0
        self.character.save()

        response = self.client.post(
            reverse(
                "game:rest_character",
                args=[self.character.id]
            )
        )

        self.character.refresh_from_db()

        self.assertEqual(response.status_code, 302)

        self.assertEqual(
            self.character.current_hp,
            self.character.max_hp
        )

        self.assertEqual(
            self.character.current_mana,
            self.character.max_mana
        )

    def test_defeated_character_cannot_start_battle(self):
        self.character.current_hp = 0
        self.character.save()

        enemy = Enemy.objects.create(
            name="Przeciwnik testowy",
            max_hp=20,
        )

        response = self.client.post(
            reverse(
                "game:start_battle",
                args=[
                    self.character.id,
                    enemy.id,
                ]
            )
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Battle.objects.count(), 0)

    def test_character_cannot_start_battle_with_enemy_too_high_level(
        self
    ):
        enemy = Enemy.objects.create(
            name="Zbyt silny przeciwnik",
            level=3,
            max_hp=100,
        )

        response = self.client.post(
            reverse(
                "game:start_battle",
                args=[
                    self.character.id,
                    enemy.id,
                ]
            )
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Battle.objects.count(), 0)

    def test_battle_setup_marks_enemy_difficulty(self):
        easy_enemy = Enemy.objects.create(
            name="Łatwy przeciwnik",
            level=1,
        )

        hard_enemy = Enemy.objects.create(
            name="Trudny przeciwnik",
            level=2,
        )

        locked_enemy = Enemy.objects.create(
            name="Zablokowany przeciwnik",
            level=3,
        )

        response = self.client.get(
            reverse(
                "game:battle_setup",
                args=[self.character.id]
            )
        )

        entries = response.context[
            "enemy_entries"
        ]

        entries_by_enemy = {
            entry["enemy"].id: entry
            for entry in entries
        }

        self.assertEqual(
            entries_by_enemy[easy_enemy.id][
                "difficulty_label"
            ],
            "Równy"
        )

        self.assertEqual(
            entries_by_enemy[hard_enemy.id][
                "difficulty_label"
            ],
            "Trudny"
        )

        self.assertFalse(
            entries_by_enemy[locked_enemy.id][
                "available"
            ]
        )