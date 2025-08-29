from django import forms

from .models import SemestrielPage


class SemestrielForm(forms.ModelForm):
    """
    Formulaire pour le calendrier semestriel
    """

    class Meta:
        model = SemestrielPage
        fields = ["picture", "file"]
        labels = {
            "picture": "Image du calendrier",
            "file": "Calendrier semestriel",
        }
        widgets = {
            "picture": forms.ClearableFileInput(
                attrs={"multiple": False, "placeholder": "Sélectionner une image"}
            ),
            "file": forms.ClearableFileInput(
                attrs={"multiple": False, "placeholder": "Sélectionner un fichier"}
            ),
        }
