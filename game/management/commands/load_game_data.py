from django.core.management import (
    call_command,
)
from django.core.management.base import (
    BaseCommand,
)
from django.db import transaction


FIXTURES = [
    "items",
    "class_weapons",
    "armor_sets",
    "resource_items",
    "character_classes",
    "races",
    "enemies",
]


class Command(BaseCommand):
    help = (
        "Wczytuje wszystkie podstawowe dane gry "
        "w prawidłowej kolejności."
    )

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(
            "Rozpoczynam wczytywanie danych gry."
        )

        for fixture_name in FIXTURES:
            self.stdout.write(
                f"Wczytywanie: {fixture_name}"
            )

            call_command(
                "loaddata",
                fixture_name,
                verbosity=0,
            )

        self.stdout.write(
            self.style.SUCCESS(
                "Wszystkie dane gry zostały "
                "wczytane poprawnie."
            )
        )