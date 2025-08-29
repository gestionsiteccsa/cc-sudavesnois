from django.db import models


class ContactEmail(models.Model):
    """Modèle pour stocker les informations de contact."""

    email = models.EmailField(verbose_name="Email", unique=True)
    is_active = models.BooleanField(default=True, verbose_name="Actif")

    class Meta:
        verbose_name = "Contact Email"
        verbose_name_plural = "Contact Emails"

    def __str__(self):
        return f"{self.email}"
