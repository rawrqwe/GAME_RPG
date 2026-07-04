from django.db import models
from django.utils.translation import gettext_lazy as _



class Item(models.Model):
    class Type(models.TextChoices):
        # Bronie
        SWORD = "SWORD", "Miecz"
        BOW = "BOW", "Łuk"
        STAFF = "STAFF", "Laska"
        SHIELD = "SHIELD", "Tarcza"

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

    class BonusStats(models.TextChoices):
        NONE = "NONE", "Brak"
        STRENGTH = "STRENGTH", "Siła"
        AGILITY = "AGILITY", "Zręczność"
        INTELLIGENCE = "INTELLIGENCE", "Inteligencja"
        HP = "HP", "HP"
        MANA = "MANA", "Mana"

    name = models.CharField(_("Nazwa"), max_length=100)
    description = models.TextField(_("Opis"), blank=True)

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
        _("Ikona"),
        upload_to="items/icons/",
        blank=True,
        null=True
    )

    power = models.IntegerField(_("Moc (obrażenia/obrona)"), default=0)

    bonus_stat = models.CharField(
        _("Bonus do statystyki"),
        max_length=20,
        choices=BonusStats.choices,
        default=BonusStats.NONE
    )

    bonus_value = models.IntegerField(_("Wartość bonusu"), default=0)

    # Leczenie dla mikstur
    heal_amount = models.IntegerField(_("Leczenie hp"), default=0)

    def __str__(self):
        return self.name
