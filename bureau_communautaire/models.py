from django.core.validators import FileExtensionValidator
from django.db import models

from app.validators import validate_image_mime
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
        db_index=True,
    )
    function = models.CharField(max_length=200, blank=True, null=True)
    picture = models.ImageField(
        upload_to="bureau_commu/elus/",
        verbose_name="Photo de l'élu",
        validators=[
            validate_taille_fichier,
            validate_image_mime,
            FileExtensionValidator(allowed_extensions=["png", "jpg", "jpeg", "webp"]),
        ],
    )
    city = models.ForeignKey(ConseilVille, on_delete=models.CASCADE)
    profession = models.CharField(max_length=100, blank=True, null=True)
    linked_commission = models.ManyToManyField(
        Commission, blank=True, related_name="elus"
    )

    class Meta:
        ordering = ["role", "rank", "last_name", "first_name"]
        verbose_name = "Élu"
        verbose_name_plural = "Élus"

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.role})"


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


class PageStatus(models.Model):
    """Modèle pour gérer l'état d'activation des pages."""

    PAGE_CHOICES = [
        ("bureau-communautaire", "Bureau Communautaire"),
        ("commissions", "Commissions"),
    ]

    page_name = models.CharField(
        max_length=50, choices=PAGE_CHOICES, unique=True, verbose_name="Page"
    )
    is_active = models.BooleanField(default=True, verbose_name="Page active")
    maintenance_message = models.TextField(
        default="La page est en cours de mise à jour.",
        verbose_name="Message de maintenance",
        help_text="Message affiché lorsque la page est désactivée.",
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Statut de page"
        verbose_name_plural = "Statuts de pages"

    def __str__(self):
        status = "Active" if self.is_active else "En maintenance"
        return f"{self.get_page_name_display()} - {status}"

    @classmethod
    def is_page_active(cls, page_name):
        """Vérifie si une page est active."""
        try:
            page_status = cls.objects.get(page_name=page_name)
            return page_status.is_active, page_status.maintenance_message
        except cls.DoesNotExist:
            # Si le statut n'existe pas, on considère la page comme active
            return True, "La page est en cours de mise à jour."
