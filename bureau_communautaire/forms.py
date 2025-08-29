from django import forms

from .models import Document, Elus


class ElusForm(forms.ModelForm):
    """Formulaire pour le modèle Elus."""

    class Meta:
        model = Elus
        fields = [
            "first_name",
            "last_name",
            "rank",
            "role",
            "picture",
            "function",
            "city",
            "profession",
            "linked_commission",
        ]
        labels = {
            "first_name": "Nom",
            "last_name": "Prénom",
            "rank": "Rang",
            "role": "Rôle",
            "picture": "Photo de l'élu",
            "function": "Fonction",
            "city": "Ville",
            "profession": "Profession",
        }
        help_texts = {
            "rank": "Pour les Vices-Président (1, 2, 3, ...).",
            "role": "Maire | Vice-Président",
            "picture": "Téléchargez une photo de l'élu.",
            "function": "RH | TRI | ...",
            "profession": "Maire de ... | 1er/2ème/... Adjoint au Maire de ...",
        }


class DocumentForm(forms.ModelForm):
    """Formulaire pour le modèle Document."""

    class Meta:
        model = Document
        fields = ["document", "title", "type"]
        labels = {
            "document": "Document",
            "title": "Titre",
        }
        help_texts = {
            "document": "Téléchargez un document.",
            "title": "Titre du document.",
        }
