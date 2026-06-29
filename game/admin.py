from django.contrib import admin
from .models import CharacterClass, Character, Race

admin.site.register(CharacterClass)
admin.site.register(Race)
admin.site.register(Character)
