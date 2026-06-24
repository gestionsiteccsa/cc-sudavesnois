from django.core.validators import FileExtensionValidator
from django.db import models

from app.models import SingletonModel
from journal.models import validate_taille_fichier


class Commission(models.Model):
    title = models.CharField(max_length=255, verbose_name="Title")
    icon = models.TextField(
        verbose_name="Icon SVG", help_text="Code SVG complet de l'icône"
    )

    class Meta:
        verbose_name = "Commission"
        verbose_name_plural = "Commissions"

    def __str__(self):
        return self.title


class Document(SingletonModel):
    file = models.FileField(
        upload_to="commissions/documents/",
        validators=[
            validate_taille_fichier,
            FileExtensionValidator(
                allowed_extensions=[
                    "pdf",
                    "png",
                    "jpg",
                    "jpeg",
                    "webp",
                    "xls",
                    "xlsx",
                    "doc",
                    "docx",
                ]
            ),
        ],
    )

    class Meta:
        verbose_name = "Document"
        verbose_name_plural = "Documents"

    def __str__(self):
        return f"{self.file.name}"


class CommissionCompetence(models.Model):
    commission = models.ForeignKey(
        Commission, on_delete=models.CASCADE, related_name="competences"
    )
    title = models.CharField(max_length=255, verbose_name="Compétence")
    order = models.IntegerField(default=0, verbose_name="Ordre d'affichage")

    class Meta:
        ordering = ["order", "title"]
        verbose_name = "Compétence de commission"
        verbose_name_plural = "Compétences de commission"

    def __str__(self):
        return self.title


class Mandat(models.Model):
    start_year = models.IntegerField(verbose_name="Start Year")
    end_year = models.IntegerField(verbose_name="End Year")

    class Meta:
        verbose_name = "Mandat"
        verbose_name_plural = "Mandats"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(end_year__gt=models.F("start_year")),
                name="mandat_end_year_after_start_year",
            ),
        ]

    def __str__(self):
        return f"{self.start_year} - {self.end_year}"
