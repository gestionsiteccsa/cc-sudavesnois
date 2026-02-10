from django import forms
from .models import Lien


class IconSelectWidget(forms.Select):
    """Widget personnalisé pour afficher les icônes dans le select"""
    template_name = 'linktree/widgets/icon_select.html'

    def __init__(self, attrs=None, choices=()):
        super().__init__(attrs)
        self.choices = list(choices)


class LienForm(forms.ModelForm):
    """Formulaire pour créer/modifier un lien"""

    # Définir explicitement le champ icone avec les choix du modèle
    icone = forms.ChoiceField(
        choices=Lien.ICON_CHOICES,
        widget=IconSelectWidget(attrs={
            'class': (
                'w-full px-4 py-2 border border-gray-300 dark:border-gray-600 '
                'rounded-lg focus:ring-2 focus:ring-primary-500 '
                'focus:border-primary-500 dark:bg-gray-700 dark:text-white'
            )
        }),
        label="Icône"
    )

    class Meta:
        model = Lien
        fields = ['titre', 'url', 'icone', 'ordre', 'actif']
        widgets = {
            'titre': forms.TextInput(attrs={
                'class': (
                    'w-full px-4 py-2 border border-gray-300 dark:border-gray-600 '
                    'rounded-lg focus:ring-2 focus:ring-primary-500 '
                    'focus:border-primary-500 dark:bg-gray-700 dark:text-white'
                ),
                'placeholder': 'Ex: Notre page Facebook'
            }),
            'url': forms.URLInput(attrs={
                'class': (
                    'w-full px-4 py-2 border border-gray-300 dark:border-gray-600 '
                    'rounded-lg focus:ring-2 focus:ring-primary-500 '
                    'focus:border-primary-500 dark:bg-gray-700 dark:text-white'
                ),
                'placeholder': 'https://...'
            }),
            'ordre': forms.NumberInput(attrs={
                'class': (
                    'w-full px-4 py-2 border border-gray-300 dark:border-gray-600 '
                    'rounded-lg focus:ring-2 focus:ring-primary-500 '
                    'focus:border-primary-500 dark:bg-gray-700 dark:text-white'
                ),
                'min': '0'
            }),
            'actif': forms.CheckboxInput(attrs={
                'class': (
                    'w-4 h-4 text-primary-600 border-gray-300 rounded '
                    'focus:ring-primary-500 dark:focus:ring-primary-600 '
                    'dark:ring-offset-gray-800'
                )
            }),
        }
        labels = {
            'titre': 'Titre du lien',
            'url': 'URL',
            'ordre': 'Ordre d\'affichage',
            'actif': 'Actif',
        }
        help_texts = {
            'titre': 'Texte affiché sur le bouton',
            'url': 'Adresse complète du lien (https://...)',
            'ordre': 'Les liens sont affichés par ordre croissant',
        }
