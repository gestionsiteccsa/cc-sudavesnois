from django.apps import AppConfig

from watson import search as watson


class ConseilCommunautaireConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "conseil_communautaire"

    def ready(self):
        from django.urls import reverse

        from .models import ConseilVille

        class ConseilVilleAdapter(watson.SearchAdapter):
            def get_url(self, obj):
                return reverse("communes-membres:commune", kwargs={"slug": obj.slug})

        watson.register(
            ConseilVille, ConseilVilleAdapter, fields=("city_name", "slogan")
        )
