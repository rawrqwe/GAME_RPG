from django.contrib.auth import (
    get_user_model,
)
from django.test import TestCase
from django.urls import reverse

from game.models import (
    Character,
    CharacterClass,
    Race,
)


User = get_user_model()


class CharacterCreationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="player",
            password="SafePassword-2026!",
        )

        self.other_user = (
            User.objects.create_user(
                username="other-player",
                password="SafePassword-2026!",
            )
        )

        self.race = Race.objects.create(
            name="Człowiek",
            description="Wszechstronna rasa.",
            hp_bonus=10,
            mana_bonus=5,
            strength_bonus=2,
            agility_bonus=1,
            intelligence_bonus=1,
        )

        self.character_class = (
            CharacterClass.objects.create(
                name="Wojownik",
                description="Silny wojownik.",
                base_hp=100,
                base_mana=20,
                base_strength=12,
                base_agility=7,
                base_intelligence=4,
                hp_growth=10,
                mana_growth=2,
                strength_growth=2,
                agility_growth=1,
                intelligence_growth=0.5,
            )
        )

    def get_character_data(
        self,
        name="Arthas",
    ):
        return {
            "name": name,
            "race": self.race.id,
            "character_class": (
                self.character_class.id
            ),
        }

    def test_login_is_required(
        self,
    ):
        create_url = reverse(
            "game:character_create"
        )

        response = self.client.get(
            create_url
        )

        expected_url = (
            f"{reverse('login')}"
            f"?next={create_url}"
        )

        self.assertRedirects(
            response,
            expected_url,
        )

    def test_creation_page_is_available(
        self,
    ):
        self.client.force_login(
            self.user
        )

        response = self.client.get(
            reverse(
                "game:character_create"
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertContains(
            response,
            "Utwórz postać",
        )

    def test_user_can_create_character(
        self,
    ):
        self.client.force_login(
            self.user
        )

        character_data = (
            self.get_character_data()
        )

        character_data["owner"] = (
            self.other_user.id
        )

        response = self.client.post(
            reverse(
                "game:character_create"
            ),
            character_data,
        )

        self.assertRedirects(
            response,
            reverse(
                "game:character_list"
            ),
        )

        character = Character.objects.get(
            name="Arthas",
        )

        self.assertEqual(
            character.owner,
            self.user,
        )

        self.assertEqual(
            character.max_hp,
            110,
        )

        self.assertEqual(
            character.current_hp,
            110,
        )

        self.assertEqual(
            character.max_mana,
            25,
        )

        self.assertEqual(
            character.current_mana,
            25,
        )

        self.assertEqual(
            character.strength,
            14,
        )

        self.assertEqual(
            character.agility,
            8,
        )

        self.assertEqual(
            character.intelligence,
            5,
        )

        self.assertTrue(
            hasattr(
                character,
                "equipment",
            )
        )

    def test_user_can_create_second_character(
        self,
    ):
        Character.objects.create(
            owner=self.user,
            name="Pierwszy",
            race=self.race,
            character_class=(
                self.character_class
            ),
        )

        self.client.force_login(
            self.user
        )

        response = self.client.post(
            reverse(
                "game:character_create"
            ),
            self.get_character_data(
                name="Drugi",
            ),
        )

        self.assertRedirects(
            response,
            reverse(
                "game:character_list"
            ),
        )

        self.assertEqual(
            Character.objects.filter(
                owner=self.user,
            ).count(),
            2,
        )

    def test_duplicate_name_is_rejected(
        self,
    ):
        Character.objects.create(
            owner=self.user,
            name="Arthas",
            race=self.race,
            character_class=(
                self.character_class
            ),
        )

        self.client.force_login(
            self.user
        )

        response = self.client.post(
            reverse(
                "game:character_create"
            ),
            self.get_character_data(
                name="ARTHAS",
            ),
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertContains(
            response,
            "Masz już postać o takiej nazwie.",
        )

        self.assertEqual(
            Character.objects.filter(
                owner=self.user,
            ).count(),
            1,
        )