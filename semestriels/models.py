from django.core.validators import FileExtensionValidator
from django.db import models

from journal.models import validate_taille_fichier


class SemestrielPage(models.Model):
    """
    Modèle stockant l'image et le calendrier semestriel
    """

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

    def save(self, *args, **kwargs):
        """
        Enregistre le modèle après avoir supprimé
        l'ancien contenu s'il existe déjà
        Permet de limiter à un seul contenu
        """
        if SemestrielPage.objects.exists():
            for obj in SemestrielPage.objects.all():
                if obj != self:
                    if obj.picture and obj.file:
                        obj.picture.delete()
                        obj.file.delete()
                    obj.delete()

        super().save(*args, **kwargs)
