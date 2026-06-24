from django import forms
from django.db.models import Count

from conseil_communautaire.models import ConseilMembre

from .models import Commission, Document, Mandat


class CommissionForm(forms.ModelForm):
    """
    Formulaire pour la création/modification d'une commission.
    """

    membres = forms.ModelMultipleChoiceField(
        queryset=ConseilMembre.objects.select_related("city").order_by(
            "last_name", "first_name"
        ),
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
        membres_pks = [m.pk for m in membres]

        # 1 seule requête aggregate : nombre de commissions par membre
        # (annotate ne fonctionne pas avec .filter() sans Q sur la M2M,
        # on utilise donc values().annotate()).
        # NB : on compte TOUTES les commissions liées, puis on décrémente
        # la commission en cours (si elle existe et si elle était déjà liée).
        qs = (
            ConseilMembre.objects.filter(pk__in=membres_pks)
            .annotate(nb=Count("linked_commission"))
            .values("pk", "first_name", "last_name", "nb")
        )
        # Pour le cas de la commission en cours, on a besoin de savoir
        # quels membres y sont déjà liés (1 requête supplémentaire unique).
        already_linked_pks = set()
        if commission_en_cours:
            already_linked_pks = set(
                Commission.objects.get(pk=commission_en_cours).membres.values_list(
                    "pk", flat=True
                )
            )

        membres_en_erreur = []
        for row in qs:
            nb = row["nb"]
            if row["pk"] in already_linked_pks:
                nb -= 1  # la commission en cours ne doit pas être comptée
            if nb >= max_commissions:
                membres_en_erreur.append(f"{row['first_name']} {row['last_name']}")

        if membres_en_erreur:
            raise forms.ValidationError(
                f"Les membres suivants sont déjà liés à {max_commissions} "
                f"commissions maximum : {', '.join(membres_en_erreur)}."
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
