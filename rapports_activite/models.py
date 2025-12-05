from django.core.validators import FileExtensionValidator
from django.db import models

from journal.models import validate_taille_fichier


class RapportActivite(models.Model):
    """
    Modèle représentant un rapport d'activité.
    """

    title = models.CharField(
        verbose_name="Titre du rapport",
        max_length=255,
        blank=True,
        null=True,
    )
    year = models.IntegerField(verbose_name="Année du rapport", unique=True)
    description = models.TextField(
        verbose_name="Description du rapport", blank=True, null=True
    )
    publish_date = models.DateTimeField(
        verbose_name="Date de publication du rapport", auto_now_add=True
    )
    file = models.FileField(
        verbose_name="Fichier du rapport",
        upload_to="rapports_activite/rapports/",
        validators=[
            FileExtensionValidator(
                allowed_extensions=["pdf", "docx", "doc", "txt"],
                message="Le fichier doit être au format PDF, DOCX, DOC ou TXT.",
            ),
            validate_taille_fichier,
        ],
    )

    def save(self, *args, **kwargs):
        """
        Override de la méthode save pour définir le titre du rapport
        en fonction de l'année.
        """
        if not self.title:
            self.title = f"Rapport d'activité {self.year}"
        if not self.description:
            self.description = f"Bilan des actions menées en {self.year}."
        super(RapportActivite, self).save(*args, **kwargs)

    def __str__(self):
        return f"Rapport d'activité {self.year}"

    def get_document_size(self):
        """Retourne la taille du document ou 'Indisponible' si le fichier est absent."""
        try:
            ko_size = self.file.size / 1024
            if ko_size > 1024:
                return f"{ko_size / 1024:.1f} Mo"
            else:
                return f"{ko_size:.1f} Ko"
        except (FileNotFoundError, ValueError, OSError):
            return "Indisponible"
