from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models


def validate_taille_fichier(value):
    max_upload_size = settings.DATA_UPLOAD_MAX_MEMORY_SIZE
    if value.size > max_upload_size:
        raise ValidationError(
            "Le fichier dépasse la taille maximale " "autorisée (60 Mo)."
        )


class Journal(models.Model):
    title = models.CharField(max_length=200)
    document = models.FileField(
        validators=[
            validate_taille_fichier,
            FileExtensionValidator(allowed_extensions=["pdf"]),
        ],
        upload_to="MSA/documents",
    )
    # Date de publication
    release_date = models.DateField(verbose_name="Date de publication")

    cover = models.ImageField(
        validators=[
            validate_taille_fichier,
            FileExtensionValidator(allowed_extensions=["png", "jpg", "jpeg"]),
        ],
        upload_to="MSA/couvertures",
    )

    number = models.IntegerField(default=0)  # Numéro du journal
    page_number = models.IntegerField(default=0)  # Nombre de pages du journal

    def __str__(self):
        return self.title

    def get_document_size(self):
        """Retourne la taille du document ou 'Indisponible' si le fichier est absent."""
        try:
            ko_size = self.document.size / 1024
            if ko_size > 1024:
                return f"{ko_size / 1024:.1f} Mo"
            else:
                return f"{ko_size:.1f} Ko"
        except (FileNotFoundError, ValueError, OSError):
            return False

    def get_cover_size(self):
        """Retourne la taille de la couverture ou 'Indisponible' si \
            le fichier est absent."""
        try:
            ko_size = self.cover.size / 1024
            if ko_size > 1024:
                return f"{ko_size / 1024:.1f} Mo"
            else:
                return f"{ko_size:.1f} Ko"
        except (FileNotFoundError, ValueError, OSError):
            return False
