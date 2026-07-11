from django.db import models
from django.utils.translation import gettext_lazy as _

from .character import Character
from .inventory import InventoryItem
from .items import Item

SLOT_BY_ITEM_TYPE = {
    Item.Type.SWORD: "weapon",
    Item.Type.BOW: "weapon",
    Item.Type.STAFF: "weapon",
    Item.Type.SHIELD: "shield",
    Item.Type.HELMET: "helmet",
    Item.Type.ARMOR: "armor",
    Item.Type.LEGGINGS: "leggings",
    Item.Type.GLOVES: "gloves",
    Item.Type.BOOTS: "boots",
}


class Equipment(models.Model):
    character = models.OneToOneField(
        Character,
        on_delete=models.CASCADE,
        related_name="equipment",
        verbose_name=_("Postać")
    )

    weapon = models.ForeignKey(
        Item,
        on_delete=models.SET_NULL, null=True, blank=True,
        related_name="equipped_as_weapon",
        verbose_name=_("Broń")
    )
    shield = models.ForeignKey(
        Item,
        on_delete=models.SET_NULL, null=True, blank=True,
        related_name="equipped_as_shield",
        verbose_name=_("Tarcza")
    )
    helmet = models.ForeignKey(
        Item,
        on_delete=models.SET_NULL, null=True, blank=True,
        related_name="equipped_as_helmet",
        verbose_name=_("Hełm")
    )
    armor = models.ForeignKey(
        Item,
        on_delete=models.SET_NULL, null=True, blank=True,
        related_name="equipped_as_armor",
        verbose_name=_("Pancerz")
    )
    leggings = models.ForeignKey(
        Item,
        on_delete=models.SET_NULL, null=True, blank=True,
        related_name="equipped_as_leggings",
        verbose_name=_("Spodnie")
    )
    gloves = models.ForeignKey(
        Item,
        on_delete=models.SET_NULL, null=True, blank=True,
        related_name="equipped_as_gloves",
        verbose_name=_("Rękawice")
    )
    boots = models.ForeignKey(
        Item,
        on_delete=models.SET_NULL, null=True, blank=True,
        related_name="equipped_as_boots",
        verbose_name=_("Buty")
    )

    def get_total_armor_power(self):
        armor_pieces = [self.shield, self.helmet, self.armor, self.leggings, self.gloves, self.boots]
        return sum(item.power for item in armor_pieces if item is not None)

    # zakładnie przedmiotu
    def equip_item(self, item):
        slot = SLOT_BY_ITEM_TYPE.get(item.type)
        if slot is None:
            raise ValueError("Tego przedmiotu nie można założyć.")

        currently_equipped = getattr(self, slot)
        if currently_equipped:
            self._return_to_inventory(currently_equipped)

        setattr(self, slot, item)
        self.save()

        self._remove_from_inventory(item)

    # zdejmowanie przedmiotu
    def unequip_slot(self, slot_name):
        item = getattr(self, slot_name)
        if item is None:
            return

        self._return_to_inventory(item)
        setattr(self, slot_name, None)
        self.save()

    # dodanie do plecaka
    def _return_to_inventory(self, item):
        inventory_item, created = InventoryItem.objects.get_or_create(
            character=self.character,
            item=item,
            defaults={"quantity": 0}
        )
        inventory_item.quantity += 1
        inventory_item.save()

    # usuwanie 1 sztukę przedmiotu z plecaka
    def _remove_from_inventory(self, item):
        inventory_item = InventoryItem.objects.get(character=self.character, item=item)
        inventory_item.quantity -= 1
        if inventory_item.quantity <= 0:
            inventory_item.delete()
        else:
            inventory_item.save()

    class Meta:
        verbose_name = _("Ekwipunek")
        verbose_name_plural = _("Ekwipunki")

    def __str__(self):
        return f"Ekwipunek: {self.character.name}"
