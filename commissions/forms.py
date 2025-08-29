from django import forms

from .models import Commission, Document, Mandat


class CommissionForm(forms.ModelForm):
    """
    Formulaire pour la création d'un acte local.
    """

    class Meta:
        # Modèle à utiliser pour le formulaire
        model = Commission
        # Champs à afficher dans le formulaire
        fields = ["title", "icon"]
        # Nom d'affichage pour chaque champ
        labels = {
            "title": "Titre de la commission",
            "icon": "Icone correspondante",
        }
        # Texte d'aide pour chaque champ
        widgets = {
            "title": forms.TextInput(
                attrs={"placeholder": "Développement économique," " santé, réseau..."}
            ),
            "icon": forms.TextInput(
                attrs={
                    "placeholder": '<svg xmlns="http://..." [...] viewBox="..."'
                    "/></svg>"
                }
            ),
        }


class CommissionDocForm(forms.ModelForm):
    """
    Formulaire permettant d'uploader un documen
    """

    class Meta:
        model = Document
        fields = ["file"]
        labels = {
            "file": "Document à uploader",
        }
        widgets = {
            "file": forms.ClearableFileInput(),
        }


class MandatForm(forms.ModelForm):
    """
    Formulaire pour la création d'un mandat.
    """

    class Meta:
        model = Mandat
        fields = ["start_year", "end_year"]
        labels = {
            "start_year": "Année de début",
            "end_year": "Année de fin",
        }
        widgets = {
            "start_year": forms.TextInput(attrs={"placeholder": "2020"}),
            "end_year": forms.TextInput(attrs={"placeholder": "2026"}),
        }
