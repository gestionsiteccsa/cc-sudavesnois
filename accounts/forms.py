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
    """Formulaire personnalisé de création d'utilisateur"""

    email = forms.EmailField(
        label=_("Adresse email"),
        max_length=254,
        widget=forms.EmailInput(attrs={"autocomplete": "email"}),
    )

    class Meta:
        model = User
        fields = ("email", "username")


class CustomUserChangeForm(UserChangeForm):
    """Formulaire personnalisé de modification d'utilisateur"""

    password = None  # Supprimer le champ password du formulaire

    class Meta:
        model = User
        fields = ("email", "username")
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
        }


class CustomAuthenticationForm(AuthenticationForm):
    """
    Formulaire de connexion personnalisé utilisant l'email
    """

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
    """
    Formulaire de réinitialisation de mot de passe personnalisé
    """

    email = forms.EmailField(
        label=_("Adresse email"),
        max_length=254,
        widget=forms.EmailInput(attrs={"autocomplete": "email"}),
    )

    def clean_email(self):
        email = self.cleaned_data.get("email")
        User = get_user_model()
        try:
            User.objects.get(email=email)
        except User.DoesNotExist:
            raise ValidationError(
                _("Aucun utilisateur n'est enregistré avec cette " "adresse email.")
            )
        return email


class CustomSetPasswordForm(SetPasswordForm):
    """
    Formulaire pour définir un nouveau mot de passe
    """

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


class ProfileUpdateForm(forms.ModelForm):
    """
    Formulaire pour mettre à jour le profil utilisateur
    """

    class Meta:
        model = User
        fields = ["username", "email"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
        }


class AdminUserCreationForm(forms.ModelForm):
    """
    Formulaire pour que l'administrateur crée un utilisateur
    """

    email = forms.EmailField(
        label=_("Adresse email"),
        required=True,
        widget=forms.EmailInput(attrs={"class": "form-control"}),
    )
    username = forms.CharField(
        label=_("Nom d'utilisateur"),
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    password = forms.CharField(
        label=_("Mot de passe"),
        required=False,
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
    )
    generate_password = forms.BooleanField(
        label=_("Générer un mot de passe temporaire"),
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    class Meta:
        model = User
        fields = ["email", "username", "password", "generate_password"]

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

        return cleaned_data
