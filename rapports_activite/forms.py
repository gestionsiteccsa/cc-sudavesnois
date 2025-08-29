from django import forms

from .models import RapportActivite


class RapportActiviteForm(forms.ModelForm):
    class Meta:
        model = RapportActivite
        fields = ["year", "file"]
        widgets = {
            "year": forms.NumberInput(attrs={"class": "form-control"}),
            "file": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }
