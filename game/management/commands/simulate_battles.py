from django.core.management.base import (
    BaseCommand,
    CommandError,
)

from game.balance import simulate_battles
from game.models import Character, Enemy


class Command(BaseCommand):
    help = (
        "Symuluje walki wybranej postaci "
        "z przeciwnikami."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "character_id",
            type=int,
            help="ID postaci używanej do symulacji.",
        )

        parser.add_argument(
            "--attempts",
            type=int,
            default=500,
            help=(
                "Liczba symulacji dla każdego "
                "przeciwnika. Domyślnie: 500."
            ),
        )

        parser.add_argument(
            "--enemy-id",
            type=int,
            default=None,
            help=(
                "Opcjonalne ID jednego przeciwnika."
            ),
        )

    def handle(self, *args, **options):
        character_id = options["character_id"]
        attempts = options["attempts"]
        enemy_id = options["enemy_id"]

        if attempts < 1:
            raise CommandError(
                "Liczba symulacji musi być "
                "większa od zera."
            )

        try:
            character = Character.objects.get(
                id=character_id,
            )
        except Character.DoesNotExist as error:
            raise CommandError(
                f"Nie znaleziono postaci o ID "
                f"{character_id}."
            ) from error

        enemies = Enemy.objects.all().order_by(
            "level",
            "is_boss",
            "name",
        )

        if enemy_id is not None:
            enemies = enemies.filter(
                id=enemy_id,
            )

            if not enemies.exists():
                raise CommandError(
                    f"Nie znaleziono przeciwnika "
                    f"o ID {enemy_id}."
                )

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                f"Symulacja dla postaci: "
                f"{character.name}"
            )
        )

        self.stdout.write(
            f"Poziom postaci: {character.level}"
        )

        self.stdout.write(
            f"Liczba prób na przeciwnika: "
            f"{attempts}"
        )

        self.stdout.write("")

        for enemy in enemies:
            result = simulate_battles(
                character,
                enemy,
                attempts=attempts,
            )

            if enemy.level <= character.level + 1:
                availability = "dostępny"
            else:
                availability = "zablokowany"

            boss_label = ""

            if enemy.is_boss:
                boss_label = " [BOSS]"

            self.stdout.write(
                f"{enemy.name}{boss_label}"
            )

            self.stdout.write(
                f"  Poziom: {enemy.level}"
                f" | {availability}"
            )

            self.stdout.write(
                f"  Wygrane: "
                f"{result['wins']}/"
                f"{result['attempts']}"
                f" ({result['win_rate']}%)"
            )

            self.stdout.write(
                f"  Średnia liczba tur: "
                f"{result['average_turns']}"
            )

            self.stdout.write(
                f"  Średnie pozostałe HP "
                f"po zwycięstwie: "
                f"{result['average_remaining_hp']}"
            )

            self.stdout.write(
                f"  Ocena: "
                f"{result['balance_label']}"
            )

            self.stdout.write("")