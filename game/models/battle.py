from django.db import models
from django.utils.translation import gettext_lazy as _
from .character import Character
from .enemy import Enemy


class Battle(models.Model):
    class Status(models.TextChoices):
        ONGOING = "ONGOING", "W trakcie"
        WON = "WON", "Wygrana"
        LOSE = "LOSE", "Przegrana"

    character = models.ForeignKey(
        Character,
        on_delete=models.CASCADE,
        verbose_name=_("Postać")
    )
    enemy = models.ForeignKey(
        Enemy,
        on_delete=models.CASCADE,
        verbose_name=_("Przeciwnik")
    )

    character_current_hp = models.IntegerField(_("Aktualne HP postaci"))
    enemy_current_hp = models.IntegerField(_("Aktualne HP postaci"))

    status = models.CharField(
        _("Status"),
        max_length=20,
        choices=Status.choices,
        default=Status.ONGOING
    )

    turn_number = models.PositiveIntegerField(
        _("Numer tury"),
        default=1,
    )

    def __str__(self):
        return f"{self.character.name} vs {self.enemy.name}"
