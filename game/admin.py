from django.contrib import admin
from .models import CharacterClass, Character, Race, Item

admin.site.register(CharacterClass)
admin.site.register(Race)
admin.site.register(Character)
admin.site.register(Item)
