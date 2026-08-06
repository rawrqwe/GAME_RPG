from django.core.management import (
    call_command,
)
from django.test import TestCase

from game.models import (
    CharacterClass,
    Enemy,
    Item,
    Race,
)


class LoadGameDataCommandTests(TestCase):
    def test_command_loads_all_game_data(
        self,
    ):
        call_command(
            "load_game_data",
            verbosity=0,
        )

        self.assertEqual(
            Item.objects.count(),
            48,
        )

        self.assertEqual(
            CharacterClass.objects.count(),
            3,
        )

        self.assertEqual(
            Race.objects.count(),
            4,
        )

        self.assertEqual(
            Enemy.objects.count(),
            12,
        )