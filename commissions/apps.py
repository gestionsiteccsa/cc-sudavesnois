from django.apps import AppConfig
from watson import search as watson


class CommissionsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "commissions"

    def ready(self):
        from .models import Commission
        from django.urls import reverse
        
        class CommissionAdapter(watson.SearchAdapter):
            def get_url(self, obj):
                return reverse('commissions:commissions')
        
        watson.register(Commission, CommissionAdapter, fields=("title",))
