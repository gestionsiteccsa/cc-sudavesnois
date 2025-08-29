from django import forms

from .models import Competence


class CompetenceForm(forms.ModelForm):
    """
    Formulaire pour la création d'une compétence.
    """

    description = forms.CharField(
        widget=forms.Textarea(),
        required=False,
        label="Description",
        help_text="Description de la compétence",
    )

    class Meta:
        model = Competence
        fields = ["title", "icon", "description", "category", "is_big"]
        labels = {
            "title": "Titre de la compétence",
            "icon": "Icone correspondante",
            "description": "Description de la compétence",
            "category": "Catégorie de la compétence",
            "is_big": "Necéssite plus grand format ? (Facultative uniquement)",
        }
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
            "category": forms.Select(attrs={"class": "form-select"}),
            "is_big": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
