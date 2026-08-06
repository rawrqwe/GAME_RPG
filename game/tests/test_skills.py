from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from game.combat import (
    get_character_skill,
    process_skill,
)
from game.models import (
    Battle,
    Character,
    CharacterClass,
    Enemy,
    Item,
    Race,
)


class ClassSkillTests(TestCase):
    def setUp(self):
        owner = User.objects.create_user(
            username="skill-tester",
        )

        race = Race.objects.create(
            name="Rasa umiejętności",
        )

        bow = Item.objects.create(
            name="Łuk testowy",
            type=Item.Type.BOW,
            power=6,
        )

        character_class = (
            CharacterClass.objects.create(
                name="Łucznik testowy",
                base_hp=100,
                base_mana=30,
                base_strength=10,
                base_agility=16,
                base_intelligence=5,
                hp_growth=8,
                mana_growth=4,
                strength_growth=1,
                agility_growth=2,
                intelligence_growth=1,
                starting_weapon=bow,
            )
        )

        self.character = Character.objects.create(
            owner=owner,
            name="Bohater umiejętności",
            race=race,
            character_class=character_class,
        )
        self.client.force_login(
            owner,
        )

        self.enemy = Enemy.objects.create(
            name="Cel umiejętności",
            max_hp=100,
            attack=8,
            defense=4,
            experience_reward=20,
            gold_reward=7,
        )

    def create_battle(
        self,
        character_mana=30,
        enemy_hp=None,
    ):
        if enemy_hp is None:
            enemy_hp = self.enemy.max_hp

        self.character.current_mana = (
            character_mana
        )

        self.character.save(
            update_fields=["current_mana"],
        )

        return Battle.objects.create(
            character=self.character,
            enemy=self.enemy,
            character_current_hp=(
                self.character.current_hp
            ),
            character_current_mana=(
                character_mana
            ),
            enemy_current_hp=enemy_hp,
        )

    def test_archer_has_class_skill(self):
        skill = get_character_skill(
            self.character,
        )

        self.assertEqual(
            skill["name"],
            "Precyzyjny strzał",
        )

        self.assertEqual(
            skill["mana_cost"],
            12,
        )

    @patch(
        "game.combat.random.randint",
        return_value=0,
    )
    def test_skill_uses_mana_and_deals_damage(
        self,
        mocked_randint,
    ):
        battle = self.create_battle()

        result = process_skill(battle)

        battle.refresh_from_db()
        self.character.refresh_from_db()

        self.assertEqual(
            result["skill_name"],
            "Precyzyjny strzał",
        )

        self.assertEqual(
            result["player_damage"],
            24,
        )

        self.assertEqual(
            result["mana_cost"],
            12,
        )

        self.assertEqual(
            battle.character_current_mana,
            18,
        )

        self.assertEqual(
            self.character.current_mana,
            18,
        )

        self.assertEqual(
            battle.enemy_current_hp,
            76,
        )

        self.assertEqual(
            battle.character_current_hp,
            96,
        )

        self.assertEqual(
            battle.turn_number,
            2,
        )

    @patch(
        "game.combat.random.randint",
        return_value=0,
    )
    def test_skill_cannot_be_used_without_mana(
        self,
        mocked_randint,
    ):
        battle = self.create_battle(
            character_mana=5,
        )

        result = process_skill(battle)

        battle.refresh_from_db()

        self.assertTrue(result["error"])

        self.assertEqual(
            battle.character_current_mana,
            5,
        )

        self.assertEqual(
            battle.enemy_current_hp,
            self.enemy.max_hp,
        )

        self.assertEqual(
            battle.turn_number,
            1,
        )

    @patch(
        "game.combat.random.randint",
        return_value=0,
    )
    def test_winning_with_skill_awards_rewards(
        self,
        mocked_randint,
    ):
        battle = self.create_battle(
            enemy_hp=10,
        )

        result = process_skill(battle)

        battle.refresh_from_db()
        self.character.refresh_from_db()

        self.assertEqual(
            battle.status,
            Battle.Status.WON,
        )

        self.assertEqual(
            battle.enemy_current_hp,
            0,
        )

        self.assertEqual(
            self.character.experience,
            20,
        )

        self.assertEqual(
            self.character.gold,
            7,
        )

        self.assertEqual(
            self.character.current_mana,
            18,
        )

        self.assertEqual(
            result["experience_reward"],
            20,
        )

        self.assertEqual(
            result["gold_reward"],
            7,
        )

    def test_start_battle_copies_character_mana(
        self,
    ):
        response = self.client.post(
            reverse(
                "game:start_battle",
                args=[
                    self.character.id,
                    self.enemy.id,
                ],
            )
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        battle = Battle.objects.get()

        self.assertEqual(
            battle.character_current_mana,
            30,
        )