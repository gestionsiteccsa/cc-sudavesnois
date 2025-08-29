from django.core.validators import FileExtensionValidator
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver

from conseil_communautaire.models import ConseilVille
from journal.models import validate_taille_fichier


class ActeLocal(models.Model):
    """
    Modèle pour représenter un acte local.
    """

    title = models.CharField(max_length=200, blank=False, null=False)
    date = models.DateField(blank=False, null=False)
    description = models.TextField(max_length=500, blank=False, null=False)
    commune = models.OneToOneField(
        ConseilVille,
        on_delete=models.CASCADE,
        related_name="acte_local",
        blank=False,
        null=False,
    )
    file = models.FileField(
        upload_to="communes/actes_locaux/",
        blank=False,
        null=False,
        validators=[
            validate_taille_fichier,
            FileExtensionValidator(allowed_extensions=["pdf"]),
        ],
    )

    def __str__(self):
        return f"Acte local du {self.date} pour {self.commune.city_name}"


@receiver(post_delete, sender=ActeLocal)
def post_delete_receiver(sender, **kwargs):
    """
    Signal qui supprime le fichier associé à l'acte local lors de sa suppression.
    """
    instance = kwargs["instance"]
    if instance.file:
        instance.file.delete(save=False)
