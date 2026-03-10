from django.apps import AppConfig
from watson import search as watson


class HomeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "home"

    def ready(self):
        from .models import StaticPage
        from django.core.validators import URLValidator
        from django.core.exceptions import ValidationError
        import re

        class StaticPageAdapter(watson.SearchAdapter):
            def get_url(self, obj):
                url = obj.url
                # Valider l'URL - accepter les URLs relatives Django
                if url:
                    # Vérifier que ce n'est pas une URL malveillante (javascript:, data:, etc.)
                    dangerous_protocols = ['javascript:', 'data:', 'vbscript:', 'file:']
                    url_lower = url.lower().strip()
                    
                    for protocol in dangerous_protocols:
                        if url_lower.startswith(protocol):
                            return ""
                    
                    # Accepter les URLs relatives (/path/) et absolites (http://...)
                    if url.startswith('/'):
                        return url
                    
                    # Valider les URLs absolues
                    try:
                        validator = URLValidator()
                        validator(url)
                    except ValidationError:
                        return ""
                
                return url

        watson.register(StaticPage, StaticPageAdapter, fields=("title", "content", "description"))
