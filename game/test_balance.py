from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase

from .balance import simulate_battles
from .models import (
    Character,
    CharacterClass,
    Enemy,
    Race,
)


class BalanceSimulationTests(TestCase):
    def setUp(self):
        owner = User.objects.create_user(
            username="balance-tester",
        )

        race = Race.objects.create(
            name="Człowiek testowy",
        )

        character_class = (
            CharacterClass.objects.create(
                name="Wojownik testowy",
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
        )

        self.character = Character.objects.create(
            owner=owner,
            name="Bohater testowy",
            race=race,
            character_class=character_class,
        )

    @patch(
        "game.combat.random.randint",
        return_value=0,
    )
    def test_simulation_reports_wins(
        self,
        mocked_randint,
    ):
        enemy = Enemy.objects.create(
            name="Słaby przeciwnik",
            max_hp=15,
            attack=8,
            defense=0,
        )

        result = simulate_battles(
            self.character,
            enemy,
            attempts=5,
        )

        self.assertEqual(result["attempts"], 5)
        self.assertEqual(result["wins"], 5)
        self.assertEqual(result["losses"], 0)
        self.assertEqual(result["win_rate"], 100.0)
        self.assertEqual(result["average_turns"], 2.0)

        self.assertEqual(
            result["average_remaining_hp"],
            94.0,
        )

        self.assertEqual(
            result["balance_label"],
            "Za łatwy",
        )

    @patch(
        "game.combat.random.randint",
        return_value=0,
    )
    def test_simulation_reports_losses(
        self,
        mocked_randint,
    ):
        enemy = Enemy.objects.create(
            name="Bardzo silny przeciwnik",
            max_hp=100,
            attack=200,
            defense=0,
        )

        result = simulate_battles(
            self.character,
            enemy,
            attempts=3,
        )

        self.assertEqual(result["attempts"], 3)
        self.assertEqual(result["wins"], 0)
        self.assertEqual(result["losses"], 3)
        self.assertEqual(result["win_rate"], 0.0)

        self.assertEqual(
            result["average_remaining_hp"],
            0,
        )

        self.assertEqual(
            result["balance_label"],
            "Za trudny",
        )