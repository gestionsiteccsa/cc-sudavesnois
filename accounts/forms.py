import secrets
import string

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordResetForm,
    SetPasswordForm,
    UserChangeForm,
    UserCreationForm,
)
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    """Formulaire personnalisé de création d'utilisateur."""

    email = forms.EmailField(
        label=_("Adresse email"),
        max_length=254,
        widget=forms.EmailInput(attrs={"autocomplete": "email"}),
    )

    class Meta:
        model = User
        fields = ("email", "username")


class CustomUserChangeForm(UserChangeForm):
    """Formulaire personnalisé de modification d'utilisateur."""

    password = None

    class Meta:
        model = User
        fields = ("email", "username")
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
        }


class CustomAuthenticationForm(AuthenticationForm):
    """Formulaire de connexion personnalisé utilisant l'email."""

    username = forms.EmailField(
        label=_("Adresse email"),
        max_length=254,
        widget=forms.EmailInput(attrs={"autofocus": True, "autocomplete": "email"}),
    )

    error_messages = {
        "invalid_login": _(
            "Veuillez saisir une adresse email et un mot de passe valides. "
            "Notez que les deux champs peuvent être sensibles à la casse."
        ),
        "inactive": _("Ce compte est inactif."),
    }


class CustomPasswordResetForm(PasswordResetForm):
    """Formulaire de réinitialisation de mot de passe personnalisé."""

    email = forms.EmailField(
        label=_("Adresse email"),
        max_length=254,
        widget=forms.EmailInput(attrs={"autocomplete": "email"}),
    )

    def clean_email(self):
        email = self.cleaned_data.get("email")
        user_model = get_user_model()
        try:
            user_model.objects.get(email=email)
        except user_model.DoesNotExist as exc:
            raise ValidationError(
                _("Aucun utilisateur n'est enregistré avec cette adresse email.")
            ) from exc
        return email


class CustomSetPasswordForm(SetPasswordForm):
    """Formulaire pour définir un nouveau mot de passe."""

    new_password1 = forms.CharField(
        label=_("Nouveau mot de passe"),
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        strip=False,
    )
    new_password2 = forms.CharField(
        label=_("Confirmation du nouveau mot de passe"),
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )


def _generate_temporary_password(length: int = 14) -> str:
    """
    Génère un mot de passe temporaire cryptographiquement sûr.

    Utilise ``secrets`` (CSPRNG du module Python) et garantit la présence
    d'au moins un caractère de chaque classe.
    """
    if length < 8:
        raise ValueError("length must be >= 8 to satisfy password policy")

    alphabet_lowercase = string.ascii_lowercase
    alphabet_uppercase = string.ascii_uppercase
    alphabet_digits = string.digits
    alphabet_symbols = "!@#$%^&*_+-=?"

    required = [
        secrets.choice(alphabet_lowercase),
        secrets.choice(alphabet_uppercase),
        secrets.choice(alphabet_digits),
        secrets.choice(alphabet_symbols),
    ]
    remaining_pool = (
        alphabet_lowercase + alphabet_uppercase + alphabet_digits + alphabet_symbols
    )
    required.extend(
        secrets.choice(remaining_pool) for _ in range(length - len(required))
    )

    password_list = required
    secrets.SystemRandom().shuffle(password_list)
    return "".join(password_list)


class AdminUserCreationForm(forms.ModelForm):
    """
    Formulaire de création d'utilisateur réservé aux administrateurs.

    - L'administrateur saisit l'email et (optionnellement) un nom d'utilisateur.
    - Le mot de passe est soit fourni explicitement, soit généré côté serveur
      via :func:`_generate_temporary_password` (CSPRNG).
    - Le mot de passe généré est exposé via ``form.generated_password`` après
      l'appel à ``is_valid()`` pour permettre son affichage à l'administrateur.
    """

    email = forms.EmailField(
        label=_("Adresse email"),
        required=True,
        widget=forms.EmailInput(attrs={"autocomplete": "email"}),
    )
    username = forms.CharField(
        label=_("Nom d'utilisateur"),
        required=False,
        max_length=150,
    )
    is_staff = forms.BooleanField(
        label=_("Donner l'accès à l'administration"),
        required=False,
        initial=False,
    )
    password = forms.CharField(
        label=_("Mot de passe"),
        required=False,
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )
    generate_password = forms.BooleanField(
        label=_("Générer un mot de passe temporaire sécurisé"),
        required=False,
        initial=True,
    )

    class Meta:
        model = User
        fields = ["email", "username", "is_staff", "password", "generate_password"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.generated_password: str | None = None

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        generate_password = cleaned_data.get("generate_password")

        if not generate_password and not password:
            raise ValidationError(
                _(
                    "Vous devez soit saisir un mot de passe, soit cocher "
                    "l'option pour en générer un."
                )
            )
        if generate_password and password:
            cleaned_data["generate_password"] = False

        return cleaned_data

    def _resolve_password(self) -> str:
        if self.cleaned_data.get("generate_password"):
            password = _generate_temporary_password()
            self.generated_password = password
            return password
        return self.cleaned_data["password"]

    def save(self, commit: bool = True):
        user = super().save(commit=False)
        user.set_password(self._resolve_password())
        if commit:
            user.save()
            self.save_m2m()
        return user
