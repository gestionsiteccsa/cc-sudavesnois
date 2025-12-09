from django.core.validators import FileExtensionValidator
from django.db import models

from conseil_communautaire.models import Commission, ConseilVille
from journal.models import validate_taille_fichier


class Elus(models.Model):
    """Modèle représentant un élu."""

    class Role(models.TextChoices):
        """Enumération des rôles possibles pour un élu."""

        VICE_PRESIDENT = "Vice-Président", "Vice-Président"
        PRESIDENT = "Président", "Président"

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    rank = models.IntegerField(default=0)  # Rang d'un vice-président
    role = models.CharField(
        max_length=50,
        choices=Role.choices,
        default=Role.VICE_PRESIDENT,
        verbose_name="Rôle",
    )
    function = models.CharField(max_length=100)
    picture = models.ImageField(
        upload_to="bureau_commu/elus/",
        verbose_name="Photo de l'élu",
        validators=[
            validate_taille_fichier,
            FileExtensionValidator(allowed_extensions=["png", "jpg", "jpeg"]),
        ],
    )
    city = models.ForeignKey(ConseilVille, on_delete=models.CASCADE)
    profession = models.CharField(max_length=100, blank=True, null=True)
    linked_commission = models.ManyToManyField(
        Commission, blank=True, related_name="elus"
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name} {self.rank} {self.role} \
            {self.function} {self.city} {self.profession}"


class Document(models.Model):
    """Modèle représentant un document."""

    class Meta:
        verbose_name = "Document"
        verbose_name_plural = "Documents"

    document = models.FileField(
        upload_to="bureau_commu/documents/",
        validators=[
            validate_taille_fichier,
            FileExtensionValidator(allowed_extensions=["pdf"]),
        ],
    )
    title = models.CharField(max_length=100, blank=False, null=False)
    type = models.CharField(
        choices=[
            ("organigramme", "Organigramme"),
            ("calendrier", "Calendrier"),
        ],
        max_length=12,
        default="organigramme",
        blank=False,
        null=False,
    )

    def get_document_size(self):
        """Retourne la taille du document en Ko."""
        return self.document.size / 1024

    def __str__(self):
        return f"{self.title} {self.document} {self.type} {self.get_document_size()} Ko"
