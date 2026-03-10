from django.db import models


class StaticPage(models.Model):
    """Pages statiques indexables pour la recherche"""
    title = models.CharField(max_length=200, verbose_name="Titre")
    slug = models.SlugField(unique=True, verbose_name="Slug")
    url = models.CharField(max_length=200, verbose_name="URL")
    content = models.TextField(help_text="Contenu textuel de la page", verbose_name="Contenu")
    description = models.TextField(blank=True, verbose_name="Description")
    
    class Meta:
        ordering = ['title']
        verbose_name = "Page statique"
        verbose_name_plural = "Pages statiques"
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return self.url
