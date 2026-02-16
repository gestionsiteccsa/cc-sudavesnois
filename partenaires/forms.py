from django import forms
from .models import CategoriePartenaire, Partenaire


class CategoriePartenaireForm(forms.ModelForm):
    """Formulaire pour les catégories de partenaires"""

    class Meta:
        model = CategoriePartenaire
        fields = ["nom", "type_section", "ordre", "active"]
        widgets = {
            "nom": forms.TextInput(attrs={
                "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white",
                "placeholder": "Nom de la catégorie"
            }),
            "type_section": forms.Select(attrs={
                "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            }),
            "ordre": forms.NumberInput(attrs={
                "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white",
                "min": 0
            }),
            "active": forms.CheckboxInput(attrs={
                "class": "h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded dark:bg-gray-700 dark:border-gray-600"
            }),
        }


class PartenaireForm(forms.ModelForm):
    """Formulaire pour les partenaires"""

    class Meta:
        model = Partenaire
        fields = [
            "nom", "categorie", "description",
            "type_lien", "site_web", "lien_interne", "logo", "couleur_fond", "ordre", "active"
        ]
        widgets = {
            "nom": forms.TextInput(attrs={
                "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white",
                "placeholder": "Nom du partenaire"
            }),
            "categorie": forms.Select(attrs={
                "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            }),
            "description": forms.Textarea(attrs={
                "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white",
                "rows": 4,
                "placeholder": "Description du partenaire"
            }),
            "type_lien": forms.Select(attrs={
                "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white",
                "onchange": "toggleLienFields()"
            }),
            "site_web": forms.URLInput(attrs={
                "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white",
                "placeholder": "https://www.exemple.com"
            }),
            "lien_interne": forms.Select(attrs={
                "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            }),
            "logo": forms.ClearableFileInput(attrs={
                "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white",
                "accept": ".png,.jpg,.jpeg,.webp,.svg"
            }),
            "couleur_fond": forms.Select(attrs={
                "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            }),
            "ordre": forms.NumberInput(attrs={
                "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white",
                "min": 0
            }),
            "active": forms.CheckboxInput(attrs={
                "class": "h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded dark:bg-gray-700 dark:border-gray-600"
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrer les catégories actives
        self.fields["categorie"].queryset = CategoriePartenaire.objects.filter(active=True)
        self.fields["categorie"].required = False
        
        # Rendre les champs de lien conditionnels
        self.fields["site_web"].required = False
        self.fields["lien_interne"].required = False
        
        # Ajouter des help texts
        self.fields["type_lien"].help_text = "Choisissez si le lien pointe vers un site externe ou une page interne du site"
        self.fields["site_web"].help_text = "Obligatoire si 'Lien externe' est sélectionné"
        self.fields["lien_interne"].help_text = "Obligatoire si 'Lien interne' est sélectionné"
        
        # Aide pour la syntaxe markdown dans la description
        self.fields["description"].help_text = """Vous pouvez ajouter des liens dans le texte :
        <br>• <strong>Lien avec texte personnalisé :</strong> [cliquez ici](https://www.exemple.com)
        <br>• <strong>URL directe :</strong> https://www.exemple.com (sera automatiquement convertie en lien)
        <br>• <strong>Retour à la ligne :</strong> Appuyez sur Entrée"""

    def clean(self):
        cleaned_data = super().clean()
        type_lien = cleaned_data.get("type_lien")
        site_web = cleaned_data.get("site_web")
        lien_interne = cleaned_data.get("lien_interne")
        
        if type_lien == "externe" and not site_web:
            self.add_error("site_web", "Le site web est obligatoire pour un lien externe.")
        
        if type_lien == "interne" and not lien_interne:
            self.add_error("lien_interne", "La page interne est obligatoire pour un lien interne.")
        
        return cleaned_data
