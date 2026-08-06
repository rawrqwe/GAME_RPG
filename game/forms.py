from django import forms
from django.contrib.auth import (
    get_user_model,
)
from django.contrib.auth.forms import (
    UserCreationForm,
)

from .models import Character


User = get_user_model()


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(
        label="Adres e-mail",
        required=True,
    )

    class Meta:
        model = User

        fields = [
            "username",
            "email",
            "password1",
            "password2",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["username"].label = (
            "Nazwa użytkownika"
        )

        self.fields["password1"].label = (
            "Hasło"
        )

        self.fields["password2"].label = (
            "Powtórz hasło"
        )

        for field in self.fields.values():
            field.help_text = ""

            field.widget.attrs.update({
                "class": "auth-input",
            })

    def clean_email(self):
        email = (
            self.cleaned_data["email"]
            .strip()
            .lower()
        )

        email_exists = User.objects.filter(
            email__iexact=email,
        ).exists()

        if email_exists:
            raise forms.ValidationError(
                "Konto z tym adresem e-mail "
                "już istnieje."
            )

        return email


class CharacterCreateForm(forms.ModelForm):
    class Meta:
        model = Character

        fields = [
            "name",
            "race",
            "character_class",
        ]

        labels = {
            "name": "Nazwa postaci",
            "race": "Rasa",
            "character_class": "Klasa postaci",
        }

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "character-form-input",
                    "placeholder": (
                        "Wpisz nazwę bohatera"
                    ),
                    "autocomplete": "off",
                },
            ),
            "race": forms.Select(
                attrs={
                    "class": "character-form-input",
                },
            ),
            "character_class": forms.Select(
                attrs={
                    "class": "character-form-input",
                },
            ),
        }

    def __init__(
        self,
        *args,
        user=None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self.user = user

        self.fields[
            "race"
        ].queryset = (
            self.fields["race"]
            .queryset
            .order_by("name")
        )

        self.fields[
            "character_class"
        ].queryset = (
            self.fields["character_class"]
            .queryset
            .order_by("name")
        )

        self.fields["race"].empty_label = (
            "Wybierz rasę"
        )

        self.fields[
            "character_class"
        ].empty_label = (
            "Wybierz klasę"
        )

    def clean_name(self):
        name = (
            self.cleaned_data["name"]
            .strip()
        )

        if self.user is None:
            return name

        name_is_used = (
            Character.objects.filter(
                owner=self.user,
                name__iexact=name,
            ).exists()
        )

        if name_is_used:
            raise forms.ValidationError(
                "Masz już postać o takiej nazwie."
            )

        return name