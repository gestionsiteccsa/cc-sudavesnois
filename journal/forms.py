from django import forms

from .models import Journal


class JournalForm(forms.ModelForm):
    class Meta:
        model = Journal
        fields = ["title", "document", "cover", "number", "release_date", "page_number"]
        widgets = {
            "release_date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
        }
