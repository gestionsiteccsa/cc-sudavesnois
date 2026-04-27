from django import forms

from .models import CompteRendu, Conseil


class MultipleFileInput(forms.FileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result


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

    documents = MultipleFileField(
        widget=MultipleFileInput(
            attrs={"class": "form-control-file", "multiple": True, "accept": ".pdf"}
        ),
        required=False,
        label="Documents PDF",
        help_text="Vous pouvez sélectionner plusieurs fichiers PDF.",
    )

    class Meta:
        model = Conseil
        fields = ["date", "hour", "place"]
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
        }
        labels = {
            "date": "Date",
            "hour": "Heure",
            "place": "Lieu",
        }
