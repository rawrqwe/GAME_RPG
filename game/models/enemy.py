from django.db import models
from django.utils.translation import gettext_lazy as _

class Enemy(models.Model):
    name = models.CharField(_("Nazwa"), max_length=100)
    description = models.TextField(_("Opis"), blank=True)

    level = models.PositiveIntegerField(_("Poziom"), default=1)

    max_hp = models.IntegerField(_("Maksymalne HP"), default=10)
    attack = models.IntegerField(_("Atak"), default=1)
    defense = models.IntegerField(_("Obrona"), default=0)

    experience_reward = models.IntegerField(_("Nagroda XP"), default=1)
    gold_reward = models.IntegerField(_("Nagroda złota"), default=0)

    is_boss = models.BooleanField(_("Boss"), default=False)

    def __str__(self):
        return self.name