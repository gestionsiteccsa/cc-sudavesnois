from django.apps import AppConfig
from watson import search as watson


class ConseilCommunautaireConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "conseil_communautaire"
    
    def ready(self):
        from .models import ConseilVille
        watson.register(ConseilVille, fields=("city_name", "slogan"), store=("postal_code",))
