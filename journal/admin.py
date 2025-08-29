import os

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .forms import JournalForm
from .models import Journal


def delete_content(modeladmin, request, queryset):
    """
    Supprime le contenu sélectionné
    """
    for obj in queryset:
        if os.path.exists(obj.cover.path):
            os.remove(obj.cover.path)
        if os.path.exists(obj.document.path):
            os.remove(obj.document.path)
    queryset.delete()


delete_content.short_description = "Supprimer le contenu sélectionné et ses fichiers"


class CustomJournalAdmin(admin.ModelAdmin):
    """
    Administration personnalisée pour le modèle journal
    """

    form = JournalForm
    model = Journal
    list_display = ("title", "number", "release_date")
    list_filter = ("title", "number", "release_date")
    fieldsets = (
        (None, {"fields": ("title", "number", "release_date")}),
        (_("Média"), {"fields": ("cover", "document")}),
    )
    search_fields = ("title", "number")
    ordering = ("number",)
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
        if os.path.exists(obj.document.path):
            os.remove(obj.document.path)
        if os.path.exists(obj.cover.path):
            os.remove(obj.cover.path)

        super().delete_model(request, obj)


admin.site.register(Journal, CustomJournalAdmin)
