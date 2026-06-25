import re

from django import forms
from django.core.exceptions import ValidationError


# Regex téléphone: 10 chiffres FR, espaces/tirets/points/parentheses/+ tolérés
TELEPHONE_REGEX = re.compile(r"^[\d\s\-().+]+$")
TELEPHONE_DIGITS_MIN = 8
TELEPHONE_DIGITS_MAX = 15


def _get_communes_choices():
    """Construit dynamiquement la liste des communes depuis ``collecte_data``."""
    try:
        from .data.collecte_data import get_available_cities

        cities = get_available_cities()
    except Exception:
        # Fallback en cas d'erreur d'import
        cities = [
            "Anor",
            "Baives",
            "Eppe-Sauvage",
            "Féron",
            "Fourmies",
            "Glageon",
            "Moustier-en-Fagne",
            "Ohain",
            "Trelon",
            "Wallers-en-Fagne",
            "Wignehies",
            "Willies",
        ]
    return [("", "Sélectionnez une commune")] + [(c, c) for c in cities]


class PLUiModificationForm(forms.Form):
    """Formulaire pour les demandes de modification PLUi."""

    # Classes CSS communes pour éviter la duplication
    INPUT_CSS_CLASS = (
        "w-full px-4 py-3 border border-gray-300 dark:border-gray-600 "
        "rounded-md focus:ring-2 focus:ring-primary focus:border-transparent "
        "dark:bg-gray-700 dark:text-white"
    )

    nom_prenom = forms.CharField(
        max_length=100,
        label="Nom et Prénom",
        widget=forms.TextInput(
            attrs={
                "class": INPUT_CSS_CLASS,
                "placeholder": "Votre nom et prénom",
                "autocomplete": "name",
            }
        ),
        error_messages={
            "required": "Le nom et prénom sont obligatoires.",
            "max_length": "Le nom ne peut pas dépasser 100 caractères.",
        },
    )

    adresse = forms.CharField(
        max_length=200,
        label="Adresse complète",
        widget=forms.Textarea(
            attrs={
                "class": INPUT_CSS_CLASS,
                "placeholder": "Votre adresse complète (rue, code postal, ville)",
                "rows": 3,
                "autocomplete": "street-address",
            }
        ),
        error_messages={
            "required": "L'adresse est obligatoire.",
            "max_length": "L'adresse ne peut pas dépasser 200 caractères.",
        },
    )

    email = forms.EmailField(
        label="Adresse email",
        widget=forms.EmailInput(
            attrs={
                "class": INPUT_CSS_CLASS,
                "placeholder": "votre.email@exemple.com",
                "autocomplete": "email",
            }
        ),
        error_messages={
            "required": "L'adresse email est obligatoire.",
            "invalid": "Veuillez saisir une adresse email valide.",
        },
    )

    telephone = forms.CharField(
        max_length=20,
        label="Téléphone",
        widget=forms.TextInput(
            attrs={
                "class": INPUT_CSS_CLASS,
                "placeholder": "01 23 45 67 89",
                "autocomplete": "tel",
            }
        ),
        error_messages={
            "required": "Le numéro de téléphone est obligatoire.",
            "max_length": "Le numéro de téléphone ne peut pas dépasser 20 caractères.",
        },
    )

    parcelles = forms.CharField(
        max_length=100,
        label="Numéros de parcelles cadastrales",
        widget=forms.TextInput(
            attrs={
                "class": INPUT_CSS_CLASS,
                "placeholder": "Ex: 123, 124, 125",
            }
        ),
        error_messages={
            "required": "Les numéros de parcelles sont obligatoires.",
            "max_length": "Les numéros de parcelles ne peuvent pas dépasser "
            "100 caractères.",
        },
    )

    commune = forms.ChoiceField(
        choices=_get_communes_choices,
        label="Commune",
        widget=forms.Select(
            attrs={
                "class": INPUT_CSS_CLASS,
            }
        ),
        error_messages={
            "required": "La commune est obligatoire.",
            "invalid_choice": "Veuillez sélectionner une commune valide.",
        },
    )

    demande = forms.CharField(
        max_length=2000,
        label="Description de votre demande",
        widget=forms.Textarea(
            attrs={
                "class": INPUT_CSS_CLASS,
                "placeholder": (
                    "Décrivez précisément votre demande de modification du PLUi..."
                ),
                "rows": 6,
            }
        ),
        error_messages={
            "required": "La description de la demande est obligatoire.",
            "max_length": "La description ne peut pas dépasser 2000 caractères.",
        },
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Appliquer les classes CSS et les attributs ARIA à tous les champs
        for name, field in self.fields.items():
            css_class = field.widget.attrs.get("class", "")
            if css_class and INPUT_CSS_CLASS not in css_class:
                field.widget.attrs["class"] = f"{css_class} {INPUT_CSS_CLASS}".strip()
            # Attribut aria-required implicite via required=True
            if field.required:
                field.widget.attrs.setdefault("aria-required", "true")

    def clean_telephone(self):
        """Validation du numéro de téléphone: 8 à 15 chiffres après nettoyage."""
        telephone = self.cleaned_data.get("telephone")
        if telephone:
            clean_phone = re.sub(r"[\s\-().+]", "", telephone)
            if not TELEPHONE_REGEX.match(telephone):
                raise ValidationError(
                    "Le numéro de téléphone contient des caractères non autorisés."
                )
            digits = sum(c.isdigit() for c in clean_phone)
            if digits < TELEPHONE_DIGITS_MIN or digits > TELEPHONE_DIGITS_MAX:
                raise ValidationError(
                    f"Le numéro de téléphone doit contenir entre "
                    f"{TELEPHONE_DIGITS_MIN} et {TELEPHONE_DIGITS_MAX} chiffres."
                )
        return telephone

    def clean_demande(self):
        """Validation de la demande: longueur minimale 10 caractères."""
        demande = self.cleaned_data.get("demande")
        if demande and len(demande.strip()) < 10:
            raise ValidationError(
                "La description de votre demande doit contenir au moins "
                "10 caractères (exemple: 'Modifier le zonage')."
            )
        return demande
