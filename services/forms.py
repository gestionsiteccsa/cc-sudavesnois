import re

from django import forms

from .models import Service

_SVG_TAG_RE = re.compile(r"^\s*<svg\b[^>]*>.*</svg>\s*$", re.DOTALL | re.IGNORECASE)
_DANGEROUS_RE = re.compile(
    r"(?i)(javascript:|data:|vbscript:|<script\b|on[a-z]+\s*=|<iframe|<object|<embed)"
)


class ServiceForm(forms.ModelForm):
    """Formulaire de création/édition d'un service avec validation SVG stricte."""

    content = forms.CharField(
        widget=forms.Textarea(),
        required=False,
        label="Description",
        help_text="Description du service",
    )
    icon = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 6,
                "placeholder": "<svg>...</svg>",
            }
        ),
        max_length=5000,
        label="Icône SVG",
        help_text=(
            "Code SVG inline (ex: <svg>...</svg>). "
            "Pas de JavaScript, pas d'event handlers."
        ),
    )

    class Meta:
        model = Service
        fields = ["title", "content", "icon"]
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Titre du service"}
            ),
        }

    def clean_icon(self):
        icon = (self.cleaned_data.get("icon") or "").strip()
        if not icon:
            raise forms.ValidationError("L'icône SVG est obligatoire.")
        if _DANGEROUS_RE.search(icon):
            raise forms.ValidationError(
                "Contenu interdit détecté (script, javascript:, "
                "event handler, iframe, etc.)."
            )
        if not _SVG_TAG_RE.match(icon):
            raise forms.ValidationError("L'icône doit être un <svg>...</svg> valide.")
        return icon
