from django.contrib import admin

from .forms import CompetenceForm
from .models import Competence


class CustomCompetenceAdmin(admin.ModelAdmin):
    """
    Administration personnalisée pour le modèle compétence
    """

    form = CompetenceForm
    model = Competence
    list_display = (
        "title",
        "description",
        "is_big",
        "category",
    )
    list_filter = (
        "title",
        "description",
        "category",
    )
    search_fields = (
        "title",
        "description",
    )
    ordering = ("title",)


admin.site.register(Competence, CustomCompetenceAdmin)
