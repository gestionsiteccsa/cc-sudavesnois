from django.db import models


class Service(models.Model):
    title = models.CharField(
        max_length=100, verbose_name="Titre", help_text="Titre affiché du service"
    )
    content = models.TextField(
        verbose_name="Description",
        blank=True,
        help_text="Description longue du service",
    )
    icon = models.TextField(
        verbose_name="Icône SVG",
        help_text="Code SVG inline validé côté serveur (max 5000 caractères).",
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Ordre d'affichage",
        help_text="Position dans la liste (gérée automatiquement).",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "title"]
        verbose_name = "Service"
        verbose_name_plural = "Services"
        indexes = [
            models.Index(fields=["order", "title"], name="service_order_title_idx"),
        ]

    def __str__(self):
        return f"{self.title} - {self.content[:50]}"
