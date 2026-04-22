from django import forms

from conseil_communautaire.models import ConseilMembre

from .models import Commission, Document, Mandat


class CommissionForm(forms.ModelForm):
    """
    Formulaire pour la création/modification d'une commission.
    """

    membres = forms.ModelMultipleChoiceField(
        queryset=ConseilMembre.objects.select_related("city").order_by("last_name", "first_name"),
        required=False,
        label="Membres liés à cette commission",
        help_text="Sélectionnez les membres du conseil communautaire à lier à cette commission. Chaque membre ne peut être lié qu'à 5 commissions maximum.",
        widget=forms.CheckboxSelectMultiple,
    )

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            # Pré-sélectionner les membres déjà liés
            self.fields["membres"].initial = self.instance.membres.all()

    def clean_membres(self):
        membres = self.cleaned_data.get("membres", [])
        if not membres:
            return membres

        commission_en_cours = self.instance.pk
        max_commissions = 5
        membres_en_erreur = []

        for membre in membres:
            # Compter les commissions déjà liées au membre
            nb_commissions = membre.linked_commission.count()
            # Si on modifie une commission existante et que le membre y est déjà lié,
            # on ne compte pas cette commission
            if commission_en_cours and membre.linked_commission.filter(pk=commission_en_cours).exists():
                nb_commissions -= 1

            if nb_commissions >= max_commissions:
                membres_en_erreur.append(f"{membre.first_name} {membre.last_name}")

        if membres_en_erreur:
            raise forms.ValidationError(
                f"Les membres suivants sont déjà liés à {max_commissions} commissions maximum : "
                f"{', '.join(membres_en_erreur)}."
            )

        return membres

    def save(self, commit=True):
        commission = super().save(commit=commit)
        if commit:
            commission.membres.set(self.cleaned_data.get("membres", []))
        return commission


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
