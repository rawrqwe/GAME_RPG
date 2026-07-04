from django.contrib import admin
from game.models import CharacterClass, Race, Character, Item, Enemy

admin.site.register(CharacterClass)
admin.site.register(Race)
admin.site.register(Character)
admin.site.register(Item)
admin.site.register(Enemy)