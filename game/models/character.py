from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from .items import Item


class CharacterClass(models.Model):
    name = models.CharField(_("Nazwa"), max_length=50, unique=True)
    description = models.TextField(_("Opis"), blank=True)

    base_hp = models.IntegerField(_("Bazowe HP"))
    base_mana = models.IntegerField(_("Bazowa mana"))

    base_strength = models.IntegerField(_("Siła bazowa"))
    base_agility = models.IntegerField(_("Zręczność bazowa"))
    base_intelligence = models.IntegerField(_("Inteligencja bazowa"))

    hp_growth = models.FloatField(_("Przyrost HP"))
    mana_growth = models.FloatField(_("Przyrost many"))

    strength_growth = models.FloatField(_("Przyrost siły"))
    agility_growth = models.FloatField(_("Przyrost zręczności"))
    intelligence_growth = models.FloatField(_("Przyrost inteligencji"))

    starting_weapon = models.ForeignKey(
        Item,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Broń startowa")
    )

    def __str__(self):
        return self.name


class Race(models.Model):
    name = models.CharField(_("Nazwa"), max_length=50)
    description = models.TextField(_("Opis"), blank=True)

    hp_bonus = models.IntegerField(_("Bonus do HP"), default=0)
    mana_bonus = models.IntegerField(_("Bonus do many"), default=0)

    strength_bonus = models.IntegerField(_("Bonus do siły"), default=0)
    agility_bonus = models.IntegerField(_("Bonus do zręczności"), default=0)
    intelligence_bonus = models.IntegerField(_("Bonus do inteligencji"), default=0)

    def __str__(self):
        return self.name


class Character(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("Właściciel"))

    name = models.CharField(_("Nazwa"), max_length=50)

    race = models.ForeignKey(
        "Race",
        on_delete=models.PROTECT,
        verbose_name=_("Rasa")
    )

    character_class = models.ForeignKey(
        "CharacterClass",
        on_delete=models.PROTECT,
        verbose_name=_("Klasa postaci")
    )

    level = models.IntegerField(_("Poziom"), default=1)
    experience = models.IntegerField(_("Doświadczenie"), default=0)

    max_hp = models.IntegerField(_("Maksymalne HP"), default=100)
    current_hp = models.IntegerField(_("Aktualne HP"), default=100)

    max_mana = models.IntegerField(_("Maksymalna mana"), default=0)
    current_mana = models.IntegerField(_("Aktualna mana"), default=0)

    strength = models.IntegerField(_("Siła"), default=10)
    agility = models.IntegerField(_("Zręczność"), default=10)
    intelligence = models.IntegerField(_("Inteligencja"), default=10)

    def save(self, *args, **kwargs):
        from .equipment import Equipment  # import lokalny - unikamy cyklicznego importu

        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new:
            equipment = Equipment.objects.create(character=self)
            if self.character_class.starting_weapon:
                equipment.weapon = self.character_class.starting_weapon
                equipment.save()

    def __str__(self):
        return self.name
