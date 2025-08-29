from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.text import slugify

from commissions.models import Commission
from journal.models import validate_taille_fichier


class ConseilVille(models.Model):
    class Sexe(models.TextChoices):
        Madame = "Mme."
        Monsieur = "M."

    city_name = models.CharField(max_length=30, unique=True)
    slug = models.SlugField(max_length=50, unique=True, blank=True)
    mayor_sex = models.CharField(max_length=7, choices=Sexe, default=Sexe.Monsieur)
    mayor_first_name = models.CharField(max_length=20, null=False, blank=False)
    mayor_last_name = models.CharField(max_length=20, null=False, blank=False)
    address = models.CharField(max_length=50, null=False, blank=False)
    postal_code = models.CharField(max_length=5, null=False, blank=False)
    phone_number = models.CharField(max_length=10, null=False, blank=False)
    website = models.URLField(null=True, blank=True)
    image = models.ImageField(
        upload_to="communes/images/",
        null=False,
        blank=False,
        validators=[
            validate_taille_fichier,
            FileExtensionValidator(allowed_extensions=["png", "jpg", "jpeg"]),
        ],
    )
    slogan = models.CharField(max_length=100, null=True, blank=True)
    nb_habitants = models.IntegerField(null=False, blank=False)

    def save(self, *args, **kwargs):
        if not self.slug and self.city_name:
            self.slug = slugify(self.city_name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.city_name


class ConseilMembre(models.Model):
    class Sexe(models.TextChoices):
        Madame = "Madame"
        Monsieur = "Monsieur"

    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    city = models.ForeignKey(ConseilVille, on_delete=models.CASCADE)
    is_suppleant = models.BooleanField(default=False)
    sexe = models.CharField(max_length=8, choices=Sexe, default=Sexe.Monsieur)
    linked_commission = models.ForeignKey(
        Commission, on_delete=models.CASCADE, null=True, blank=True, default=None
    )

    class Meta:
        unique_together = ("first_name", "last_name", "city")

    def __str__(self):
        return f"{self.first_name} {self.last_name} {self.city} \
            {self.is_suppleant} {self.sexe}"

    def save(self, *args, **kwargs):
        self.last_name = self.last_name.upper()
        super().save(*args, **kwargs)
