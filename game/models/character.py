from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _

from .items import Item


class CharacterClass(models.Model):
    name = models.CharField(
        _("Nazwa"),
        max_length=50,
        unique=True,
    )

    description = models.TextField(
        _("Opis"),
        blank=True,
    )

    base_hp = models.IntegerField(
        _("Bazowe HP"),
    )

    base_mana = models.IntegerField(
        _("Bazowa mana"),
    )

    base_strength = models.IntegerField(
        _("Siła bazowa"),
    )

    base_agility = models.IntegerField(
        _("Zręczność bazowa"),
    )

    base_intelligence = models.IntegerField(
        _("Inteligencja bazowa"),
    )

    hp_growth = models.FloatField(
        _("Przyrost HP"),
    )

    mana_growth = models.FloatField(
        _("Przyrost many"),
    )

    strength_growth = models.FloatField(
        _("Przyrost siły"),
    )

    agility_growth = models.FloatField(
        _("Przyrost zręczności"),
    )

    intelligence_growth = models.FloatField(
        _("Przyrost inteligencji"),
    )

    starting_weapon = models.ForeignKey(
        Item,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Broń startowa"),
    )

    def __str__(self):
        return self.name


class Race(models.Model):
    name = models.CharField(
        _("Nazwa"),
        max_length=50,
    )

    description = models.TextField(
        _("Opis"),
        blank=True,
    )

    hp_bonus = models.IntegerField(
        _("Bonus do HP"),
        default=0,
    )

    mana_bonus = models.IntegerField(
        _("Bonus do many"),
        default=0,
    )

    strength_bonus = models.IntegerField(
        _("Bonus do siły"),
        default=0,
    )

    agility_bonus = models.IntegerField(
        _("Bonus do zręczności"),
        default=0,
    )

    intelligence_bonus = models.IntegerField(
        _("Bonus do inteligencji"),
        default=0,
    )

    def __str__(self):
        return self.name


class Character(models.Model):
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_("Właściciel"),
    )

    name = models.CharField(
        _("Nazwa"),
        max_length=50,
    )

    race = models.ForeignKey(
        "Race",
        on_delete=models.PROTECT,
        verbose_name=_("Rasa"),
    )

    character_class = models.ForeignKey(
        "CharacterClass",
        on_delete=models.PROTECT,
        verbose_name=_("Klasa postaci"),
    )

    level = models.IntegerField(
        _("Poziom"),
        default=1,
    )

    experience = models.IntegerField(
        _("Doświadczenie"),
        default=0,
    )

    max_hp = models.IntegerField(
        _("Maksymalne HP"),
        default=100,
    )

    current_hp = models.IntegerField(
        _("Aktualne HP"),
        default=100,
    )

    max_mana = models.IntegerField(
        _("Maksymalna mana"),
        default=0,
    )

    current_mana = models.IntegerField(
        _("Aktualna mana"),
        default=0,
    )

    strength = models.IntegerField(
        _("Siła"),
        default=10,
    )

    agility = models.IntegerField(
        _("Zręczność"),
        default=10,
    )

    intelligence = models.IntegerField(
        _("Inteligencja"),
        default=10,
    )

    gold = models.IntegerField(
        _("Złoto"),
        default=0,
    )

    def get_equipment_bonus(self, bonus_stat):
        equipment = getattr(
            self,
            "equipment",
            None,
        )

        if equipment is None:
            return 0

        return equipment.get_stat_bonus(
            bonus_stat,
        )

    @property
    def total_max_hp(self):
        hp_bonus = self.get_equipment_bonus(
            Item.BonusStats.HP,
        )

        return self.max_hp + hp_bonus

    @property
    def total_max_mana(self):
        mana_bonus = self.get_equipment_bonus(
            Item.BonusStats.MANA,
        )

        return self.max_mana + mana_bonus

    def save(self, *args, **kwargs):
        from .equipment import Equipment
        from .inventory import InventoryItem

        is_new = self.pk is None

        if is_new:
            character_class = self.character_class
            race = self.race

            self.max_hp = (
                character_class.base_hp
                + race.hp_bonus
            )

            self.current_hp = self.max_hp

            self.max_mana = (
                character_class.base_mana
                + race.mana_bonus
            )

            self.current_mana = self.max_mana

            self.strength = (
                character_class.base_strength
                + race.strength_bonus
            )

            self.agility = (
                character_class.base_agility
                + race.agility_bonus
            )

            self.intelligence = (
                character_class.base_intelligence
                + race.intelligence_bonus
            )

        super().save(*args, **kwargs)

        if is_new:
            equipment = Equipment.objects.create(
                character=self,
            )

            starting_weapon = (
                self.character_class.starting_weapon
            )

            if starting_weapon:
                InventoryItem.objects.create(
                    character=self,
                    item=starting_weapon,
                    quantity=1,
                )

                equipment.weapon = starting_weapon
                equipment.save()

    def get_xp_to_next_level(self):
        return self.level * 100

    def try_level_up(self):
        leveled_up = False
        growth = self.character_class

        while (
            self.experience
            >= self.get_xp_to_next_level()
        ):
            xp_needed = (
                self.get_xp_to_next_level()
            )

            self.experience -= xp_needed

            old_level = self.level
            self.level += 1

            old_growth_steps = old_level - 1
            new_growth_steps = self.level - 1

            hp_increase = (
                int(
                    growth.hp_growth
                    * new_growth_steps
                )
                - int(
                    growth.hp_growth
                    * old_growth_steps
                )
            )

            mana_increase = (
                int(
                    growth.mana_growth
                    * new_growth_steps
                )
                - int(
                    growth.mana_growth
                    * old_growth_steps
                )
            )

            strength_increase = (
                int(
                    growth.strength_growth
                    * new_growth_steps
                )
                - int(
                    growth.strength_growth
                    * old_growth_steps
                )
            )

            agility_increase = (
                int(
                    growth.agility_growth
                    * new_growth_steps
                )
                - int(
                    growth.agility_growth
                    * old_growth_steps
                )
            )

            intelligence_increase = (
                int(
                    growth.intelligence_growth
                    * new_growth_steps
                )
                - int(
                    growth.intelligence_growth
                    * old_growth_steps
                )
            )

            self.max_hp += hp_increase
            self.max_mana += mana_increase

            self.strength += strength_increase
            self.agility += agility_increase
            self.intelligence += (
                intelligence_increase
            )

            self.current_hp = (
                self.total_max_hp
            )

            self.current_mana = (
                self.total_max_mana
            )

            leveled_up = True

        self.save()

        return leveled_up

    def __str__(self):
        return self.name