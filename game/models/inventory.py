from django.db import models
from .character import Character
from .items import Item
from django.utils.translation import gettext_lazy as _

class InventoryItem(models.Model):
    character = models.ForeignKey(
        Character, on_delete=models.CASCADE,
        related_name="inventory_items",
        verbose_name=_("Postać")
    )

    item = models.ForeignKey(
        Item, on_delete=models.CASCADE,
        verbose_name=_("Przedmioty")
    )

    quantity = models.PositiveIntegerField(_("Ilość"), default=1)

    class Meta:
        verbose_name = _("Przedmioty w ekwipunku")
        verbose_name_plural = _("Przedmioty w ekwipunku")
        unique_together = ("character",'item')

    def __str__(self):
        return f"{self.character.name}: {self.item.name} x {self.quantity}"