import os

from django.contrib import admin

from .forms import CommissionDocForm, CommissionForm, MandatForm
from .models import Commission, Document, Mandat


class CustomCommissionAdmin(admin.ModelAdmin):
    """
    Administration personnalisée pour le modèle commission
    """

    form = CommissionForm
    model = Commission
    list_display = ("title", "icon")
    list_filter = ("title", "icon")
    search_fields = ("title", "icon")
    ordering = ("title",)


def delete_content(modeladmin, request, queryset):
    """
    Supprime le contenu sélectionné
    """
    for obj in queryset:
        if os.path.exists(obj.file.path):
            os.remove(obj.file.path)
    queryset.delete()


delete_content.short_description = "Supprimer le contenu sélectionné et ses fichiers"


class CustomDocumentAdmin(admin.ModelAdmin):
    """
    Administration personnalisée pour le modèle document
    """

    form = CommissionDocForm
    model = Document
    list_display = ("file",)
    search_fields = ("file",)
    ordering = ("file",)
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
        if os.path.exists(obj.file.path):
            os.remove(obj.file.path)
        super().delete_model(request, obj)


class CustomMandatAdmin(admin.ModelAdmin):
    """
    Administration personnalisée pour le modèle mandat
    """

    form = MandatForm
    model = Mandat
    list_display = ("start_year", "end_year")
    search_fields = ("start_year", "end_year")
    ordering = ("start_year",)


admin.site.register(Commission, CustomCommissionAdmin)
admin.site.register(Document, CustomDocumentAdmin)
admin.site.register(Mandat, CustomMandatAdmin)
