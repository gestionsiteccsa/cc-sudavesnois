from django.contrib import admin

from .forms import ActesLocForm
from .models import ActeLocal


class CustomCommuneMAdmin(admin.ModelAdmin):
    """
    Administration personnalisée pour le modèle membre
    """

    form = ActesLocForm
    model = ActeLocal
    list_display = ("title", "date", "description", "commune", "file")
    list_filter = ("title", "date", "description", "commune", "file")
    search_fields = ("title", "date", "description", "commune", "file")
    ordering = ("date",)


admin.site.register(ActeLocal, CustomCommuneMAdmin)
