import os

from django.core.validators import FileExtensionValidator
from django.db import models

from app.models import SingletonModel
from journal.models import validate_taille_fichier


class CompteRendu(SingletonModel):
    link = models.URLField(max_length=200, blank=False, null=False)

    def __str__(self):
        return self.link


class Conseil(models.Model):
    date = models.DateField(db_index=True)
    hour = models.TimeField()
    place = models.CharField(max_length=100, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["date", "hour"], name="conseil_date_hour_idx"),
        ]

    def __str__(self):
        place_display = self.place if self.place else "Lieu à communiquer"
        return f"Conseil du {self.date} - {self.hour} - {place_display}"


class DocumentConseil(models.Model):
    conseil = models.ForeignKey(
        Conseil,
        on_delete=models.CASCADE,
        related_name="documents",
    )
    file = models.FileField(
        upload_to="comptes-rendus/documents/",
        validators=[
            FileExtensionValidator(allowed_extensions=["pdf"]),
            validate_taille_fichier,
        ],
    )
    title = models.CharField(
        max_length=255,
        blank=True,
        help_text="Titre personnalisé (laisser vide pour utiliser le nom du fichier)",
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["file"]

    @property
    def display_name(self):
        if self.title:
            return self.title
        # Nettoyer le nom du fichier automatiquement
        filename = self.file.name.split("/")[-1]
        filename = os.path.splitext(filename)[0]  # Enlever .pdf
        filename = filename.replace("_", " ")  # Remplacer _ par espaces
        filename = " ".join(filename.split())  # Nettoyer espaces multiples
        return filename

    def __str__(self):
        return self.display_name
