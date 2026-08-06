from django import forms
from django.contrib.auth import (
    get_user_model,
)
from django.contrib.auth.forms import (
    UserCreationForm,
)


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