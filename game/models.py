from django.db import models
from django.contrib.auth.models import User


class CharacterClass(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    base_hp = models.IntegerField()
    base_mana = models.IntegerField()

    base_strength = models.IntegerField()
    base_agility = models.IntegerField()
    base_intelligence = models.IntegerField()

    hp_growth = models.FloatField()
    mana_growth = models.FloatField()

    strength_growth = models.FloatField()
    agility_growth = models.FloatField()
    intelligence_growth = models.FloatField()

    def __str__(self):
        return self.name


class Race(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)

    hp_bonus = models.IntegerField(default=0)
    mana_bonus = models.IntegerField(default=0)

    strength_bonus = models.IntegerField(default=0)
    agility_bonus = models.IntegerField(default=0)
    intelligence_bonus = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class Character(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    name = models.CharField(max_length=50)

    race = models.ForeignKey(Race, on_delete=models.PROTECT)
    character_class = models.ForeignKey(CharacterClass, on_delete=models.PROTECT)

    level = models.IntegerField(default=1)
    experience = models.IntegerField(default=0)

    max_hp = models.IntegerField(default=100)
    current_hp = models.IntegerField(default=100)

    max_mana = models.IntegerField(default=0)
    current_mana = models.IntegerField(default=0)

    strength = models.IntegerField(default=10)
    agility = models.IntegerField(default=10)
    intelligence = models.IntegerField(default=10)

    def __str__(self):
        return self.name


class Item(models.Model):

    class Type(models.TextChoices):
        SWORD = "SWORD", "Sword"
        AXE = "AXE", "Axe"
        DAGGER = "DAGGER", "Dagger"
        BOW = "BOW", "Bow"
        STAFF = "STAFF", "Staff"
        SHIELD = "SHIELD", "Shield"
        HELMET = "HELMET", "Helmet"
        CHESTPLATE = "CHESTPLATE", "Chestplate"
        LEGGINGS = "LEGGINGS", "Leggings"
        BOOTS = "BOOTS", "Boots"
        GLOVES = "GLOVES", "Gloves"
        RING = "RING", "Ring"
        NECKLACE = "NECKLACE", "Necklace"
        POTION = "POTION", "Potion"
        MATERIAL = "MATERIAL", "Material"
        QUEST_ITEM = "QUEST_ITEM", "Quest Item"

    class Rarity(models.TextChoices):
        COMMON = "COMMON", "Common"
        UNCOMMON = "UNCOMMON", "Uncommon"
        RARE = "RARE", "Rare"
        EPIC = "EPIC", "Epic"
        LEGENDARY = "LEGENDARY", "Legendary"
        MYTHIC = "MYTHIC", "Mythic"

    name = models.CharField(max_length=100)
    description = models.TextField()

    type = models.CharField(
        max_length=20,
        choices=Type.choices
    )

    rarity = models.CharField(
        max_length=20,
        choices=Rarity.choices,
        default=Rarity.COMMON
    )

    required_level = models.PositiveIntegerField(default=1)

    buy_price = models.PositiveIntegerField(default=0)
    sell_price = models.PositiveIntegerField(default=0)

    icon = models.ImageField(
        upload_to="items/icons/",
        blank=True,
        null=True
    )

    def __str__(self):
        return self.name