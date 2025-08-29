import os

from django.contrib import admin

from .forms import ConseilForm, CRForm
from .models import CompteRendu, Conseil


def delete_content(modeladmin, request, queryset):
    """
    Supprime le contenu sélectionné
    """
    for obj in queryset:
        if obj.day_order:
            if os.path.exists(obj.day_order.path):
                os.remove(obj.day_order.path)
    queryset.delete()


delete_content.short_description = "Supprimer le contenu sélectionné et ses fichiers"


class CustomConseilAdmin(admin.ModelAdmin):
    """
    Administration personnalisée pour le modèle Conseil
    """

    form = ConseilForm
    model = Conseil
    list_display = ("date", "hour", "place", "day_order")
    search_fields = ("place", "date")
    list_filter = ("date", "hour")
    ordering = ("date", "hour")
    actions = [delete_content]

    def delete_model(self, request, obj):
        """
        Surcharge pour la suppression du modèle
        ET de son contenu
        (Supp individuelle)
        """
        if obj.day_order:
            if os.path.exists(obj.day_order.path):
                os.remove(obj.day_order.path)

        super().delete_model(request, obj)

    def get_actions(self, request):
        """
        Surcharge de la méthode get_actions pour
        supprimer l'action par défaut de suppression
        """
        actions = super().get_actions(request)
        if "delete_selected" in actions:
            del actions["delete_selected"]
        return actions


class CustomCRAdmin(admin.ModelAdmin):
    """
    Administration personnalisée pour le modèle Conseil
    """

    form = CRForm
    model = CompteRendu
    list_display = ("link",)


admin.site.register(Conseil, CustomConseilAdmin)
admin.site.register(CompteRendu, CustomCRAdmin)
