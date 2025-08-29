from django import forms

from .models import ConseilMembre, ConseilVille


class ConseilVilleForm(forms.ModelForm):
    class Meta:
        # Modèle à utiliser pour le formulaire
        model = ConseilVille
        # Champs à afficher dans le formulaire
        fields = [
            "city_name",
            "postal_code",
            "address",
            "phone_number",
            "website",
            "mayor_sex",
            "mayor_first_name",
            "mayor_last_name",
            "image",
            "slogan",
            "nb_habitants",
        ]
        # Nom d'affichage pour chaque champ
        labels = {
            "city_name": "Nom de la commune",
            "mayor_sex": "Sexe du maire",
            "address": "Adresse de la mairie",
            "postal_code": "Code postal",
            "meeting_place": "Lieu de réunion (Mairie ? Salle des fêtes ?)",
            "phone_number": "Numéro de téléphone",
            "website": "Site internet",
            "mayor_first_name": "Prénom du maire",
            "mayor_last_name": "Nom du maire",
            "image": "Image représentant la commune",
            "slogan": "Slogan de la commune",
            "nb_habitants": "Nombre d'habitants",
        }
        # Texte d'aide pour chaque champ
        widgets = {
            "city_name": forms.TextInput(attrs={"placeholder": "Fourmies"}),
            "address": forms.TextInput(attrs={"placeholder": "1 Rue de la Mairie"}),
            "postal_code": forms.TextInput(attrs={"placeholder": "59610"}),
            "meeting_place": forms.TextInput(attrs={"placeholder": "Mairie"}),
            "phone_number": forms.TextInput(attrs={"placeholder": "0123456789"}),
            "website": forms.TextInput(attrs={"placeholder": "https://www.maville.fr"}),
            "mayor_first_name": forms.TextInput(attrs={"placeholder": "Jean"}),
            "mayor_last_name": forms.TextInput(attrs={"placeholder": "Pierre"}),
            "slogan": forms.Textarea(
                attrs={"placeholder": "Slogan de la commune", "rows": 3}
            ),
            "nb_habitants": forms.TextInput(attrs={"placeholder": "10000"}),
        }


class ConseilMembreForm(forms.ModelForm):
    class Meta:
        model = ConseilMembre
        fields = [
            "first_name",
            "last_name",
            "is_suppleant",
            "sexe",
            "city",
            "linked_commission",
        ]

    def clean_last_name(self):
        return self.cleaned_data["last_name"].upper()
