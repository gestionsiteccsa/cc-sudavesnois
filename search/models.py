from django.db import models


class SearchConfig(models.Model):
    """Configuration pour le système de recherche"""
    
    min_query_length = models.PositiveIntegerField(
        default=2,
        verbose_name="Longueur minimale de recherche",
        help_text="Nombre minimum de caractères pour une recherche"
    )
    
    max_query_length = models.PositiveIntegerField(
        default=200,
        verbose_name="Longueur maximale de recherche",
        help_text="Nombre maximum de caractères pour une recherche"
    )
    
    results_per_page = models.PositiveIntegerField(
        default=10,
        verbose_name="Résultats par page",
        help_text="Nombre de résultats affichés par page"
    )
    
    highlight_search_terms = models.BooleanField(
        default=True,
        verbose_name="Surligner les termes",
        help_text="Mettre en évidence les termes recherchés dans les résultats"
    )
    
    class Meta:
        verbose_name = "Configuration de recherche"
        verbose_name_plural = "Configuration de recherche"
    
    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        self.pk = 1
        super().save(*args, **kwargs)
    
    @classmethod
    def get_config(cls):
        """Get or create the singleton config instance"""
        config, created = cls.objects.get_or_create(pk=1)
        return config
    
    def __str__(self):
        return "Configuration de recherche"
