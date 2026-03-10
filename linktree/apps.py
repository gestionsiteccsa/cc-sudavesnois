from django.apps import AppConfig
from watson import search as watson


class LinktreeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'linktree'
    verbose_name = 'Liens LinkTree'

    def ready(self):
        from .models import Lien
        from django.urls import reverse
        
        class LienAdapter(watson.SearchAdapter):
            def get_url(self, obj):
                return reverse('linktree:linktree_page')
        
        watson.register(Lien, LienAdapter, fields=("titre",))
