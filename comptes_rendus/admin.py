import os

from django.contrib import admin

from .forms import ConseilForm, CRForm
from .models import CompteRendu, Conseil, DocumentConseil


def delete_content(modeladmin, request, queryset):
    """
    Supprime le contenu sélectionné et ses fichiers associés
    """
    for obj in queryset:
        for doc in obj.documents.all():
            if os.path.exists(doc.file.path):
                os.remove(doc.file.path)
            doc.delete()
    queryset.delete()


delete_content.short_description = "Supprimer le contenu sélectionné et ses fichiers"


class DocumentConseilInline(admin.TabularInline):
    model = DocumentConseil
    extra = 1


class CustomConseilAdmin(admin.ModelAdmin):
    """
    Administration personnalisée pour le modèle Conseil
    """

    form = ConseilForm
    model = Conseil
    inlines = [DocumentConseilInline]
    list_display = ("date", "hour", "place")
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
        for doc in obj.documents.all():
            if os.path.exists(doc.file.path):
                os.remove(doc.file.path)
            doc.delete()

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
    Administration personnalisée pour le modèle CompteRendu
    """

    form = CRForm
    model = CompteRendu
    list_display = ("link",)


class DocumentConseilAdmin(admin.ModelAdmin):
    """
    Administration pour les documents de conseil
    """

    list_display = ("conseil", "file", "title", "uploaded_at")
    list_filter = ("conseil", "uploaded_at")
    search_fields = ("title", "file")


admin.site.register(Conseil, CustomConseilAdmin)
admin.site.register(CompteRendu, CustomCRAdmin)
admin.site.register(DocumentConseil, DocumentConseilAdmin)
