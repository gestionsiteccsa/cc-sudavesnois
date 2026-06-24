from django.db import models

from app.models import SingletonModel


class SearchConfigModel(SingletonModel):
    min_query_length = models.PositiveIntegerField(
        default=2,
        verbose_name="Longueur minimale de recherche",
        help_text="Nombre minimum de caractères pour une recherche",
    )

    max_query_length = models.PositiveIntegerField(
        default=200,
        verbose_name="Longueur maximale de recherche",
        help_text="Nombre maximum de caractères pour une recherche",
    )

    results_per_page = models.PositiveIntegerField(
        default=10,
        verbose_name="Résultats affichés par page",
        help_text="Nombre de résultats affichés par page",
    )

    highlight_search_terms = models.BooleanField(
        default=True,
        verbose_name="Surligner les termes",
        help_text="Mettre en évidence les termes recherchés dans les résultats",
    )

    class Meta:
        verbose_name = "Configuration de recherche"
        verbose_name_plural = "Configuration de recherche"

    @classmethod
    def get_config(cls):
        return cls.load()

    def __str__(self):
        return "Configuration de recherche"
