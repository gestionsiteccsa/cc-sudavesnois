from django.apps import AppConfig
from watson import search as watson


class LinktreeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'linktree'
    verbose_name = 'Liens LinkTree'

    def ready(self):
        from .models import Lien
        watson.register(Lien, fields=("titre",))
