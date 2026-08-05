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
        verbose_name=_("Postać"),
    )

    weapon = models.ForeignKey(
        Item,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="equipped_as_weapon",
        verbose_name=_("Broń"),
    )

    shield = models.ForeignKey(
        Item,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="equipped_as_shield",
        verbose_name=_("Tarcza"),
    )

    helmet = models.ForeignKey(
        Item,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="equipped_as_helmet",
        verbose_name=_("Hełm"),
    )

    armor = models.ForeignKey(
        Item,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="equipped_as_armor",
        verbose_name=_("Pancerz"),
    )

    leggings = models.ForeignKey(
        Item,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="equipped_as_leggings",
        verbose_name=_("Spodnie"),
    )

    gloves = models.ForeignKey(
        Item,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="equipped_as_gloves",
        verbose_name=_("Rękawice"),
    )

    boots = models.ForeignKey(
        Item,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="equipped_as_boots",
        verbose_name=_("Buty"),
    )

    def get_total_armor_power(self):
        armor_pieces = [
            self.shield,
            self.helmet,
            self.armor,
            self.leggings,
            self.gloves,
            self.boots,
        ]

        return sum(
            item.power
            for item in armor_pieces
            if item is not None
        )

    def get_equipped_items(self):
        return [
            self.weapon,
            self.shield,
            self.helmet,
            self.armor,
            self.leggings,
            self.gloves,
            self.boots,
        ]

    def get_stat_bonus(self, bonus_stat):
        return sum(
            item.bonus_value
            for item in self.get_equipped_items()
            if (
                item is not None
                and item.bonus_stat == bonus_stat
            )
        )

    def equip_item(self, item):
        slot = SLOT_BY_ITEM_TYPE.get(
            item.type,
        )

        if slot is None:
            raise ValueError(
                "Tego przedmiotu nie można założyć."
            )

        if (
            self.character.level
            < item.required_level
        ):
            raise ValueError(
                f"Ten przedmiot wymaga poziomu "
                f"{item.required_level}."
            )

        if slot == "weapon":
            self._validate_weapon_type(
                item,
            )

        if slot == "shield":
            self._validate_shield()

        currently_equipped = getattr(
            self,
            slot,
        )

        if currently_equipped:
            self._return_to_inventory(
                currently_equipped,
            )

        setattr(
            self,
            slot,
            item,
        )

        self.save()

        self._clamp_character_resources()
        self._remove_from_inventory(item)

    def _validate_weapon_type(self, item):
        starting_weapon = (
            self.character
            .character_class
            .starting_weapon
        )

        if starting_weapon is None:
            return

        allowed_weapon_type = (
            starting_weapon.type
        )

        if item.type != allowed_weapon_type:
            allowed_type_name = (
                starting_weapon.get_type_display()
            )

            raise ValueError(
                f"Ta klasa postaci może używać "
                f"tylko broni typu: "
                f"{allowed_type_name}."
            )

    def _validate_shield(self):
        starting_weapon = (
            self.character
            .character_class
            .starting_weapon
        )

        if starting_weapon is None:
            return

        if (
            starting_weapon.type
            != Item.Type.SWORD
        ):
            raise ValueError(
                "Tylko Wojownik może używać tarczy."
            )

    def unequip_slot(self, slot_name):
        item = getattr(
            self,
            slot_name,
        )

        if item is None:
            return

        self._return_to_inventory(item)

        setattr(
            self,
            slot_name,
            None,
        )

        self.save()

        self._clamp_character_resources()

    def _clamp_character_resources(self):
        character = self.character

        maximum_hp = (
            character.max_hp
            + self.get_stat_bonus(
                Item.BonusStats.HP,
            )
        )

        maximum_mana = (
            character.max_mana
            + self.get_stat_bonus(
                Item.BonusStats.MANA,
            )
        )

        update_fields = []

        if character.current_hp > maximum_hp:
            character.current_hp = maximum_hp
            update_fields.append("current_hp")

        if (
            character.current_mana
            > maximum_mana
        ):
            character.current_mana = (
                maximum_mana
            )

            update_fields.append(
                "current_mana"
            )

        if update_fields:
            character.save(
                update_fields=update_fields,
            )

    def _return_to_inventory(self, item):
        inventory_item, created = (
            InventoryItem.objects.get_or_create(
                character=self.character,
                item=item,
                defaults={"quantity": 0},
            )
        )

        inventory_item.quantity += 1
        inventory_item.save()

    def _remove_from_inventory(self, item):
        inventory_item = (
            InventoryItem.objects.get(
                character=self.character,
                item=item,
            )
        )

        inventory_item.quantity -= 1

        if inventory_item.quantity <= 0:
            inventory_item.delete()
        else:
            inventory_item.save()

    class Meta:
        verbose_name = _("Ekwipunek")
        verbose_name_plural = _("Ekwipunki")

    def __str__(self):
        return (
            f"Ekwipunek: "
            f"{self.character.name}"
        )