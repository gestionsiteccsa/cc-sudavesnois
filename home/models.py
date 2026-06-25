from django.db import models
from django.urls import reverse
from django.utils import timezone


class StaticPage(models.Model):
    """Pages statiques indexables pour la recherche et le sitemap."""

    title = models.CharField(max_length=200, verbose_name="Titre")
    slug = models.SlugField(unique=True, verbose_name="Slug", db_index=True)
    url = models.CharField(
        max_length=200,
        verbose_name="URL",
        db_index=True,
        help_text="URL relative (/chemin/) ou nom d'URL Django (namespace:name).",
    )
    content = models.TextField(
        help_text="Contenu textuel de la page",
        verbose_name="Contenu",
    )
    description = models.TextField(blank=True, verbose_name="Description")
    is_published = models.BooleanField(
        default=True,
        verbose_name="Publié",
        help_text="Dépublier exclut la page du sitemap et de la recherche.",
    )
    created_at = models.DateTimeField(
        default=timezone.now, verbose_name="Créé le"
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")

    class Meta:
        ordering = ["title"]
        verbose_name = "Page statique"
        verbose_name_plural = "Pages statiques"
        constraints = [
            models.UniqueConstraint(
                fields=["url"], name="home_staticpage_url_unique"
            ),
        ]
        indexes = [
            models.Index(fields=["is_published", "title"]),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        # Si l'url est un nom d'URL Django (contient ':'), on tente reverse()
        if ":" in self.url:
            try:
                return reverse(self.url)
            except Exception:
                return self.url
        return self.url
