from django import forms

from .models import Service


class ServiceForm(forms.ModelForm):
    content = forms.CharField(
        widget=forms.Textarea(),
        required=False,
        label="Description",
        help_text="Description du service",
    )

    class Meta:
        model = Service
        fields = ["title", "content", "icon"]
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Titre du service"}
            ),
            "icon": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": '<svg xmlns="[...]" height="X" width="auto" '
                    'viewBox="[...]"></svg>',
                }
            ),
        }
