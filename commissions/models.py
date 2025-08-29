from django.db import models


class Commission(models.Model):
    title = models.CharField(max_length=255, verbose_name="Title")
    icon = models.CharField(max_length=255, verbose_name="Icon")

    class Meta:
        verbose_name = "Commission"
        verbose_name_plural = "Commissions"

    def __str__(self):
        return self.title


class Document(models.Model):
    file = models.FileField(upload_to="commissions/documents/")

    class Meta:
        verbose_name = "Document"
        verbose_name_plural = "Documents"

    def __str__(self):
        return f"{self.file.name}"

    def save(self, *args, **kwargs):
        """
        La fonction save() est redéfinie pour s'assurer qu'il
        n'y ait qu'une seule instance de Document.
        Elle supprime l'instance précédente si elle existe.
        """
        if Document.objects.exists():
            Document.objects.all().delete()
        super().save(*args, **kwargs)


class Mandat(models.Model):
    start_year = models.IntegerField(verbose_name="Start Year")
    end_year = models.IntegerField(verbose_name="End Year")

    class Meta:
        verbose_name = "Mandat"
        verbose_name_plural = "Mandats"

    def __str__(self):
        return f"{self.start_year} - {self.end_year}"
