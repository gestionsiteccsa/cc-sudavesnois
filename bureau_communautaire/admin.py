import os

from django.contrib import admin

from .forms import DocumentForm, ElusForm
from .models import Document, Elus


def delete_elus_image(modeladmin, request, queryset):
    """
    Supprime le contenu sélectionné
    """
    for obj in queryset:
        if os.path.exists(obj.picture.path):
            os.remove(obj.picture.path)
    queryset.delete()


delete_elus_image.short_description = "Supprimer le/les élu(s) sélectionné(s)"


def delete_document(modeladmin, request, queryset):
    """
    Supprime le contenu sélectionné
    """
    for obj in queryset:
        if os.path.exists(obj.document.path):
            os.remove(obj.document.path)
    queryset.delete()


delete_document.short_description = "Supprimer le/les document(s) sélectionné(s)"


class CustomElusAdmin(admin.ModelAdmin):
    """
    Administration personnalisée pour le modèle Elu
    """

    form = ElusForm
    model = Elus
    list_display = [
        "first_name",
        "last_name",
        "rank",
        "role",
        "picture",
        "function",
        "city",
        "profession",
    ]
    list_filter = ("first_name", "last_name", "profession", "function", "city_id")
    search_fields = ("first_name", "last_name", "function", "profession", "city_id")
    ordering = ("first_name",)
    actions = [delete_elus_image]

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

        super().delete_model(request, obj)


class CustomDocumentAdmin(admin.ModelAdmin):
    """
    Administration personnalisée pour le modèle Document
    """

    form = DocumentForm
    model = Document
    list_display = ("document", "title", "type")
    list_filter = ("title", "type")
    search_fields = ("title",)
    ordering = ("title",)
    actions = [delete_document]

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

        super().delete_model(request, obj)


admin.site.register(Elus, CustomElusAdmin)
admin.site.register(Document, CustomDocumentAdmin)
