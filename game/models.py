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

    hp = models.IntegerField(default=100)
    mana = models.IntegerField(default=0)

    strength = models.IntegerField(default=10)
    agility = models.IntegerField(default=10)
    intelligence = models.IntegerField(default=10)

    def __str__(self):
        return self.name
