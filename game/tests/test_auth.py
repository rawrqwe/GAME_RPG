from django.contrib.auth import (
    get_user_model,
)
from django.test import TestCase
from django.urls import reverse


User = get_user_model()


class RegistrationTests(TestCase):
    def test_registration_page_is_available(
        self,
    ):
        response = self.client.get(
            reverse("game:register")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertContains(
            response,
            "Utwórz konto",
        )

    def test_user_can_register(
        self,
    ):
        response = self.client.post(
            reverse("game:register"),
            {
                "username": "new-player",
                "email": "player@example.com",
                "password1": (
                    "SafePassword-2026!"
                ),
                "password2": (
                    "SafePassword-2026!"
                ),
            },
        )

        self.assertRedirects(
            response,
            reverse("game:character_list"),
        )

        user = User.objects.get(
            username="new-player",
        )

        self.assertEqual(
            user.email,
            "player@example.com",
        )

        self.assertTrue(
            response.wsgi_request
            .user
            .is_authenticated
        )

    def test_registration_rejects_duplicate_username(
        self,
    ):
        User.objects.create_user(
            username="existing-player",
            email="first@example.com",
            password="SafePassword-2026!",
        )

        response = self.client.post(
            reverse("game:register"),
            {
                "username": "existing-player",
                "email": "second@example.com",
                "password1": (
                    "SafePassword-2026!"
                ),
                "password2": (
                    "SafePassword-2026!"
                ),
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            User.objects.filter(
                username="existing-player",
            ).count(),
            1,
        )

    def test_logged_in_user_is_redirected(
        self,
    ):
        user = User.objects.create_user(
            username="logged-player",
            password="SafePassword-2026!",
        )

        self.client.force_login(user)

        response = self.client.get(
            reverse("game:register")
        )

        self.assertRedirects(
            response,
            reverse("game:character_list"),
        )