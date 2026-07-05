from django.db import models
from django.utils.translation import gettext_lazy as _

from .character import Character
from .items import Item


class Equipment(models.Model):
    character = models.OneToOneField(
        Character,
        on_delete=models.CASCADE,
        related_name="equipment",
        verbose_name=_("Postać")
    )

    weapon = models.ForeignKey(
        Item, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="equipped_as_weapon",
        verbose_name=_("Broń")
    )
    shield = models.ForeignKey(
        Item, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="equipped_as_shield",
        verbose_name=_("Tarcza")
    )
    helmet = models.ForeignKey(
        Item, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="equipped_as_helmet",
        verbose_name=_("Hełm")
    )
    armor = models.ForeignKey(
        Item, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="equipped_as_armor",
        verbose_name=_("Pancerz")
    )
    leggings = models.ForeignKey(
        Item, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="equipped_as_leggings",
        verbose_name=_("Spodnie")
    )
    gloves = models.ForeignKey(
        Item, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="equipped_as_gloves",
        verbose_name=_("Rękawice")
    )
    boots = models.ForeignKey(
        Item, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="equipped_as_boots",
        verbose_name=_("Buty")
    )

    def get_total_armor_power(self):
        armor_pieces = [self.shield, self.helmet, self.armor, self.leggings, self.gloves, self.boots]
        return sum(item.power for item in armor_pieces if item is not None)

    class Meta:
        verbose_name = _("Ekwipunek")
        verbose_name_plural = _("Ekwipunki")

    def __str__(self):
        return f"Ekwipunek: {self.character.name}"