import os

from django.contrib import admin

from .forms import SemestrielForm
from .models import SemestrielPage


def delete_content(modeladmin, request, queryset):
    """
    Supprime le contenu sélectionné
    """
    for obj in queryset:
        if os.path.exists(obj.picture.path):
            os.remove(obj.picture.path)
        if os.path.exists(obj.file.path):
            os.remove(obj.file.path)
    queryset.delete()


delete_content.short_description = "Supprimer le contenu sélectionné et ses fichiers"


class CustomContentAdmin(admin.ModelAdmin):
    """
    Administration personnalisée pour le modèle membre
    """

    form = SemestrielForm
    model = SemestrielPage
    list_display = ("picture", "file")
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
        if os.path.exists(obj.picture.path):
            os.remove(obj.picture.path)
        if os.path.exists(obj.file.path):
            os.remove(obj.file.path)

        super().delete_model(request, obj)


admin.site.register(SemestrielPage, CustomContentAdmin)
