from django.contrib import admin

from app.utils import secure_file_removal

from .forms import SemestrielForm
from .models import SemestrielPage


def delete_content(modeladmin, request, queryset):
    """
    Supprime le contenu sélectionné
    """
    for obj in queryset:
        secure_file_removal(obj.picture)
        secure_file_removal(obj.file)
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
        secure_file_removal(obj.picture)
        secure_file_removal(obj.file)

        super().delete_model(request, obj)


admin.site.register(SemestrielPage, CustomContentAdmin)
