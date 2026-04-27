from django.core.validators import FileExtensionValidator, MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.text import slugify

from commissions.models import Commission
from journal.models import validate_taille_fichier


class ConseilVille(models.Model):
    class Sexe(models.TextChoices):
        Madame = "Mme."
        Monsieur = "M."

    city_name = models.CharField(max_length=30, unique=True, db_index=True)
    slug = models.SlugField(max_length=50, unique=True, blank=True, db_index=True)
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

    def get_commune_name_with_article(self):
        """
        Retourne le nom de la commune avec l'article approprié (de/d').
        Utilise 'd'' devant une voyelle ou un h muet.
        """
        if not self.city_name:
            return "Commune"

        first_letter = self.city_name[0].lower()
        voyels = "aeiouh"

        if first_letter in voyels:
            return f"Commune d'{self.city_name}"
        else:
            return f"Commune de {self.city_name}"

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
    linked_commission = models.ManyToManyField(
        Commission, blank=True, related_name="membres",
        help_text="Sélectionnez jusqu'à 5 commissions pour ce membre."
    )
    photo = models.ImageField(
        upload_to="membres/photos/",
        null=True,
        blank=True,
        validators=[
            validate_taille_fichier,
            FileExtensionValidator(allowed_extensions=["png", "jpg", "jpeg", "webp"]),
        ],
    )
    photo_position_x = models.IntegerField(
        default=50,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100),
        ],
        help_text="Position horizontale de la photo (0 = gauche, 50 = centre, 100 = droite)",
        verbose_name="Position X (%)",
    )
    photo_position_y = models.IntegerField(
        default=50,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100),
        ],
        help_text="Position verticale de la photo (0 = haut, 50 = centre, 100 = bas)",
        verbose_name="Position Y (%)",
    )
    photo_zoom = models.IntegerField(
        default=100,
        validators=[
            MinValueValidator(50),
            MaxValueValidator(200),
        ],
        help_text="Zoom de la photo (50% = plus petit, 100% = taille normale, 200% = plus grand)",
        verbose_name="Zoom (%)",
    )

    # class Meta:
    #     unique_together = ("first_name", "last_name", "city")

    def __str__(self):
        return f"{self.first_name} {self.last_name} {self.city} \
            {self.is_suppleant} {self.sexe}"

    def save(self, *args, **kwargs):
        self.last_name = self.last_name.upper()
        super().save(*args, **kwargs)
