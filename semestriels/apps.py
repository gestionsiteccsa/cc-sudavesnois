from django.apps import AppConfig

from watson import search as watson


class SemestrielsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "semestriels"

    def ready(self):
        from django.urls import reverse

        from .models import SemestrielPage

        class SemestrielAdapter(watson.SearchAdapter):
            def get_url(self, obj):
                return reverse("semestriels:semestriel")

        watson.register(SemestrielPage, SemestrielAdapter, fields=("title",))
