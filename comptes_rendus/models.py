from django.core.validators import FileExtensionValidator
from django.db import models

from journal.models import validate_taille_fichier


class CompteRendu(models.Model):
    link = models.URLField(max_length=200, blank=False, null=False)

    def __str__(self):
        return self.link

    def save(self, *args, **kwargs):
        if CompteRendu.objects.exists():
            # Si un objet existe déjà, on le supprime avant d'en créer un nouveau
            # Limiter à un seul objet
            CompteRendu.objects.all().delete()
        super().save(*args, **kwargs)


class Conseil(models.Model):
    date = models.DateField()
    hour = models.TimeField()
    place = models.CharField(max_length=100)
    day_order = models.FileField(
        upload_to="comptes-rendus/ordre-du-jour/",
        validators=[
            FileExtensionValidator(allowed_extensions=["pdf"]),
            validate_taille_fichier,
        ],
        blank=True,
    )

    def __str__(self):
        return f"Conseil du {self.date} - {self.hour} - {self.place} - \
            Ordre du jour: {self.day_order}"
