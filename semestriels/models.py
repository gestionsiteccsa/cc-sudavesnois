from django.core.validators import FileExtensionValidator
from django.db import models

from app.models import SingletonModel
from journal.models import validate_taille_fichier


class SemestrielPage(SingletonModel):
    """
    Modèle stockant l'image et le calendrier semestriel
    (singleton : une seule instance autorisée via SingletonModel).
    """

    title = models.CharField(
        max_length=200,
        default="Calendrier semestriel",
        verbose_name="Titre",
    )

    picture = models.ImageField(
        upload_to="semestriels/image",
        validators=[
            FileExtensionValidator(
                allowed_extensions=["jpg", "jpeg", "png"],
                message="Le fichier doit être une image au format JPG, JPEG, PNG.",
            ),
            validate_taille_fichier,
        ],
    )

    file = models.FileField(
        upload_to="semestriels/calendrier",
        validators=[
            FileExtensionValidator(
                allowed_extensions=["pdf"], message="Le fichier doit être un PDF."
            ),
            validate_taille_fichier,
        ],
    )
