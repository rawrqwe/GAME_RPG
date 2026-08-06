from django.db import migrations, models


def add_warrior_mana(apps, schema_editor):
    CharacterClass = apps.get_model(
        "game",
        "CharacterClass",
    )

    Character = apps.get_model(
        "game",
        "Character",
    )

    Battle = apps.get_model(
        "game",
        "Battle",
    )

    CharacterClass.objects.filter(
        name="Wojownik",
    ).update(
        base_mana=30,
        mana_growth=4.0,
    )

    warriors = Character.objects.filter(
        character_class__name="Wojownik",
        max_mana=0,
    )

    for character in warriors:
        maximum_mana = (
            30
            + int(
                4.0
                * (character.level - 1)
            )
        )

        character.max_mana = maximum_mana
        character.current_mana = maximum_mana

        character.save(
            update_fields=[
                "max_mana",
                "current_mana",
            ]
        )

    for battle in Battle.objects.select_related(
        "character",
    ):
        battle.character_current_mana = (
            battle.character.current_mana
        )

        battle.save(
            update_fields=[
                "character_current_mana",
            ]
        )


class Migration(migrations.Migration):
    dependencies = [
        (
            "game",
            "0008_inventoryitem",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="battle",
            name="character_current_mana",
            field=models.IntegerField(
                default=0,
                verbose_name=(
                    "Aktualna mana postaci"
                ),
            ),
        ),
        migrations.RunPython(
            add_warrior_mana,
            migrations.RunPython.noop,
        ),
    ]