from django import forms
from django.core.exceptions import ValidationError
import re


class PLUiModificationForm(forms.Form):
    """Formulaire pour les demandes de modification PLUi."""

    # Liste des communes de la Communauté de Communes Sud-Avesnois
    COMMUNES_CHOICES = [
        ('', 'Sélectionnez une commune'),
        ('Anor', 'Anor'),
        ('Baives', 'Baives'),
        ('Eppe-Sauvage', 'Eppe-Sauvage'),
        ('Féron', 'Féron'),
        ('Fourmies', 'Fourmies'),
        ('Glageon', 'Glageon'),
        ('Moustier-en-Fagne', 'Moustier-en-Fagne'),
        ('Ohain', 'Ohain'),
        ('Trelon', 'Trelon'),
        ('Wallers-en-Fagne', 'Wallers-en-Fagne'),
        ('Wignehies', 'Wignehies'),
        ('Willies', 'Willies'),
    ]

    # Classes CSS communes pour éviter la duplication
    INPUT_CSS_CLASS = (
        'w-full px-4 py-3 border border-gray-300 dark:border-gray-600 '
        'rounded-md focus:ring-2 focus:ring-primary focus:border-transparent '
        'dark:bg-gray-700 dark:text-white'
    )

    nom_prenom = forms.CharField(
        max_length=100,
        label="Nom et Prénom",
        widget=forms.TextInput(attrs={
            'class': INPUT_CSS_CLASS,
            'placeholder': 'Votre nom et prénom',
            'required': True,
        }),
        error_messages={
            'required': 'Le nom et prénom sont obligatoires.',
            'max_length': 'Le nom ne peut pas dépasser 100 caractères.',
        }
    )

    adresse = forms.CharField(
        max_length=200,
        label="Adresse complète",
        widget=forms.Textarea(attrs={
            'class': INPUT_CSS_CLASS,
            'placeholder': 'Votre adresse complète (rue, code postal, ville)',
            'rows': 3,
            'required': True,
        }),
        error_messages={
            'required': 'L\'adresse est obligatoire.',
            'max_length': 'L\'adresse ne peut pas dépasser 200 caractères.',
        }
    )

    email = forms.EmailField(
        label="Adresse email",
        widget=forms.EmailInput(attrs={
            'class': INPUT_CSS_CLASS,
            'placeholder': 'votre.email@exemple.com',
            'required': True,
        }),
        error_messages={
            'required': 'L\'adresse email est obligatoire.',
            'invalid': 'Veuillez saisir une adresse email valide.',
        }
    )

    telephone = forms.CharField(
        max_length=20,
        label="Téléphone",
        widget=forms.TextInput(attrs={
            'class': INPUT_CSS_CLASS,
            'placeholder': 'Votre numéro de téléphone',
            'required': True,
        }),
        error_messages={
            'required': 'Le numéro de téléphone est obligatoire.',
            'max_length': 'Le numéro de téléphone ne peut pas dépasser 20 caractères.',
        }
    )

    parcelles = forms.CharField(
        max_length=100,
        label="Numéros de parcelles cadastrales",
        widget=forms.TextInput(attrs={
            'class': INPUT_CSS_CLASS,
            'placeholder': 'Ex: 123, 124, 125',
            'required': True,
        }),
        error_messages={
            'required': 'Les numéros de parcelles sont obligatoires.',
            'max_length': 'Les numéros de parcelles ne peuvent pas dépasser '
                          '100 caractères.',
        }
    )

    commune = forms.ChoiceField(
        choices=COMMUNES_CHOICES,
        label="Commune",
        widget=forms.Select(attrs={
            'class': INPUT_CSS_CLASS,
            'required': True,
        }),
        error_messages={
            'required': 'La commune est obligatoire.',
            'invalid_choice': 'Veuillez sélectionner une commune valide.',
        }
    )

    demande = forms.CharField(
        max_length=2000,
        label="Description de votre demande",
        widget=forms.Textarea(attrs={
            'class': INPUT_CSS_CLASS,
            'placeholder': 'Décrivez précisément votre demande de modification '
                           'du PLUi...',
            'rows': 6,
            'required': True,
        }),
        error_messages={
            'required': 'La description de la demande est obligatoire.',
            'max_length': 'La description ne peut pas dépasser 2000 caractères.',
        }
    )

    def clean_telephone(self):
        """Validation du numéro de téléphone."""
        telephone = self.cleaned_data.get('telephone')
        if telephone:
            # Nettoyer le numéro (supprimer espaces, tirets, points)
            clean_phone = re.sub(r'[\s\-\.]', '', telephone)
            # Vérifier que c'est un numéro valide (chiffres, +, (), espaces)
            if not re.match(r'^[\d\+\s\(\)]+$', clean_phone):
                raise ValidationError(
                    'Veuillez saisir un numéro de téléphone valide.'
                )
        return telephone

    def clean_parcelles(self):
        """Validation des numéros de parcelles."""
        parcelles = self.cleaned_data.get('parcelles')
        if parcelles:
            # Vérifier que les parcelles contiennent des caractères valides
            if not re.match(r'^[\d\s,\.\-]+$', parcelles):
                raise ValidationError(
                    'Les numéros de parcelles ne peuvent contenir que des '
                    'chiffres, espaces, virgules, points et tirets.'
                )
        return parcelles

    def clean_demande(self):
        """Validation de la demande."""
        demande = self.cleaned_data.get('demande')
        if demande:
            # Vérifier la longueur minimale
            if len(demande.strip()) < 10:
                raise ValidationError(
                    'La description de votre demande doit contenir au moins '
                    '10 caractères.'
                )
        return demande