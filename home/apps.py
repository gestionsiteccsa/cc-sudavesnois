from django.apps import AppConfig
from watson import search as watson


class HomeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "home"
    
    def ready(self):
        from .models import StaticPage
        
        class StaticPageAdapter(watson.SearchAdapter):
            def get_url(self, obj):
                return obj.url
        
        watson.register(StaticPage, StaticPageAdapter, fields=("title", "content", "description"))
