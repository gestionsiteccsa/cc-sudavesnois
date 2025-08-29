import os

from django.contrib import admin

from .models import RapportActivite


def delete_rapports_activite(modeladmin, request, queryset):
    """
    Action pour supprimer les rapports d'activité sélectionnés.
    """
    for object in queryset:
        if os.path.exists(object.file.path):
            os.remove(object.file.path)
        object.delete()


delete_rapports_activite.short_description = "Supprimer les rapports \
    d'activité sélectionnés"


class CustomRapportActiviteAdmin(admin.ModelAdmin):
    """
    Classe d'administration personnalisée pour le modèle RapportActivite.
    """

    list_display = (
        "title",
        "year",
        "description",
        "publish_date",
        "file",
    )
    list_filter = ("year", "publish_date")
    search_fields = ("year", "publish_date")
    ordering = ("-publish_date",)
    date_hierarchy = "publish_date"
    list_per_page = 20
    actions = [delete_rapports_activite]

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
        Surcharge de la méthode delete_model pour
        supprimer le fichier associé au rapport d'activité
        """
        if os.path.exists(obj.file.path):
            os.remove(obj.file.path)
        super().delete_model(request, obj)


admin.site.register(RapportActivite, CustomRapportActiviteAdmin)
