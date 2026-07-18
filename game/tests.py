from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase

from .combat import process_turn
from .models import Battle, Character, CharacterClass, Enemy, Race


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
