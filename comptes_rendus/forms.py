from django import forms

from .models import CompteRendu, Conseil


class CRForm(forms.ModelForm):
    """
    Formulaire pour ajouter un compte-rendu
    """

    class Meta:
        model = CompteRendu
        fields = ["link"]
        labels = {
            "link": "Lien vers le stockage en ligne",
        }
        widgets = {
            "link": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "https://drive.google.com/...",
                }
            ),
        }


class ConseilForm(forms.ModelForm):
    """
    Formulaire pour ajouter un conseil
    """

    class Meta:
        model = Conseil
        fields = ["date", "hour", "place", "day_order"]
        widgets = {
            "date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}, format="%Y-%m-%d"
            ),
            "hour": forms.TimeInput(
                attrs={"class": "form-control", "type": "time"}, format="%H:%M"
            ),
            "place": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Lieu de la réunion"}
            ),
            "day_order": forms.ClearableFileInput(attrs={"class": "form-control-file"}),
        }
        labels = {
            "date": "Date",
            "hour": "Heure",
            "place": "Lieu",
            "day_order": "Ordre du jour",
        }
