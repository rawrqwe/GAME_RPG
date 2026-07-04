from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


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

    race = models.ForeignKey("Race", on_delete=models.PROTECT, verbose_name=_("Rasa"))
    character_class = models.ForeignKey("CharacterClass", on_delete=models.PROTECT, verbose_name=_("Klasa postaci"))

    level = models.IntegerField(_("Poziom"), default=1)
    experience = models.IntegerField(_("Doświadczenie"), default=0)

    max_hp = models.IntegerField(_("Maksymalne HP"), default=100)
    current_hp = models.IntegerField(_("Aktualne HP"), default=100)

    max_mana = models.IntegerField(_("Maksymalna mana"), default=0)
    current_mana = models.IntegerField(_("Aktualna mana"), default=0)

    strength = models.IntegerField(_("Siła"), default=10)
    agility = models.IntegerField(_("Zręczność"), default=10)
    intelligence = models.IntegerField(_("Inteligencja"), default=10)

    def __str__(self):
        return self.name


class Item(models.Model):
    class Type(models.TextChoices):
        # Bronie
        SWORD = "SWORD", "Miecz"
        BOW = "BOW", "Łuk"
        STAFF = "STAFF", "Laska"

        # Pancerz
        HELMET = "HELMET", "Hełm"
        ARMOR = "ARMOR", "Pancerz"
        LEGGINGS = "LEGGINGS", "Spodnie"
        GLOVES = "GLOVES", "Rękawice"
        BOOTS = "BOOTS", "Buty"

        # Pozostałe
        POTION = "POTION", "Mikstura"
        MATERIAL = "MATERIAL", "Materiał"
        QUEST_ITEM = "QUEST_ITEM", "Przedmiot fabularny"

    class Rarity(models.TextChoices):
        COMMON = "COMMON", "Zwykły"
        UNCOMMON = "UNCOMMON", "Niepospolity"
        RARE = "RARE", "Rzadki"
        EPIC = "EPIC", "Epicki"
        LEGENDARY = "LEGENDARY", "Legendarny"

    name = models.CharField(max_length=100)
    description = models.TextField()

    type = models.CharField(
        _("Typ"),
        max_length=20,
        choices=Type.choices
    )

    rarity = models.CharField(
        _("Rzadkość"),
        max_length=20,
        choices=Rarity.choices,
        default=Rarity.COMMON
    )

    required_level = models.PositiveIntegerField(_("Wymagany poziom"), default=1)

    buy_price = models.PositiveIntegerField(_("Cena zakupu"), default=0)
    sell_price = models.PositiveIntegerField(_("Cena sprzedaży"), default=0)

    icon = models.ImageField(
        _("Okona"),
        upload_to="items/icons/",
        blank=True,
        null=True
    )

    def __str__(self):
        return self.name