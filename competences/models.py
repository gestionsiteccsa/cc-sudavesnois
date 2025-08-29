from django.db import models


class Competence(models.Model):
    class Category(models.TextChoices):
        OBLIGATOIRE = "OBLIGATOIRE", "Obligatoire"
        OPTIONNELLE = "OPTIONNELLE", "Optionnelle"
        FACULTATIVE = "FACULTATIVE", "Facultative"

    title = models.CharField(max_length=255, verbose_name="Title")
    icon = models.CharField(max_length=1000, verbose_name="Icon")
    description = models.TextField(verbose_name="Description", blank=False, null=False)
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.FACULTATIVE,
        verbose_name="Category",
    )
    is_big = models.BooleanField(default=False, verbose_name="Is Big")

    class Meta:
        verbose_name = "Compétence"
        verbose_name_plural = "Compétences"

    def __str__(self):
        return f"{self.title} ({self.category}) - {self.description}) - {self.is_big}"
