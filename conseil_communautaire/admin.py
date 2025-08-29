import os

from django.contrib import admin

from .forms import ConseilMembreForm, ConseilVilleForm
from .models import ConseilMembre, ConseilVille


class CustomMemberAdmin(admin.ModelAdmin):
    """
    Administration personnalisée pour le modèle membre
    """

    form = ConseilMembreForm
    model = ConseilMembre
    list_display = ("sexe", "first_name", "last_name", "is_suppleant", "city_id")
    list_filter = ("first_name", "last_name", "is_suppleant", "city_id")
    search_fields = ("first_name", "last_name", "is_suppleant")
    ordering = ("first_name",)


def delete_content(modeladmin, request, queryset):
    """
    Supprime le contenu sélectionné
    """
    for obj in queryset:
        if os.path.exists(obj.image.path):
            os.remove(obj.image.path)
    queryset.delete()


delete_content.short_description = "Supprimer la/les commune(s) sélectionnée(s)"


class CustomCityAdmin(admin.ModelAdmin):
    """
    Administration personnalisée pour le modèle city
    """

    form = ConseilVilleForm
    model = ConseilVille
    ordering = ("city_name",)
    list_display = [
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
    actions = [delete_content]

    def get_actions(self, request):
        """
        Surcharge de la méthode get_actions pour
        supprimer l'action par défaut de suppression
        """
        actions = super().get_actions(request)
        if "delete_selected" in actions:
            del actions["delete_selected"]
        return actions

    def delete_model(self, request, obj):
        """
        Surcharge pour la suppression du modèle
        ET de son contenu
        (Supp individuelle)
        """
        if os.path.exists(obj.image.path):
            os.remove(obj.image.path)

        super().delete_model(request, obj)


admin.site.register(ConseilMembre, CustomMemberAdmin)
admin.site.register(ConseilVille, CustomCityAdmin)
