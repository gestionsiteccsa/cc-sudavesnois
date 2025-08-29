from django import forms

from .models import ActeLocal


class ActesLocForm(forms.ModelForm):
    """
    Formulaire pour la création d'un acte local.
    """

    class Meta:
        # Modèle à utiliser pour le formulaire
        model = ActeLocal
        # Champs à afficher dans le formulaire
        fields = ["title", "date", "description", "commune", "file"]
        # Nom d'affichage pour chaque champ
        labels = {
            "title": "Titre de l'acte",
            "date": "Date de l'acte",
            "description": "Description de l'acte",
            "commune": "Commune concernée",
        }
        # Texte d'aide pour chaque champ
        widgets = {
            "title": forms.TextInput(
                attrs={"placeholder": "Délibération du Conseil " "Municipal"}
            ),
            "date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "description": forms.Textarea(
                attrs={
                    "rows": 4,
                    "cols": 40,
                    "placeholder": "Conformément à l'article L. 2131-1 "
                    "du Code général des collectivités "
                    "territoriales, les actes "
                    "réglementaires et les décisions ne "
                    "présentant ni un caractère "
                    "réglementaire ni un caractère "
                    "individuel font l'objet d'une "
                    "publication sous forme électronique",
                }
            ),
            "commune": forms.Select(attrs={"class": "form-control"}),
        }
