"""Validateurs partagés pour les fichiers téléversés (images, PDF, etc.)."""

from django.core.exceptions import ValidationError

from PIL import Image, UnidentifiedImageError


def validate_image_mime(value):
    """
    Vérifie que le fichier téléversé est une image authentique.

    ``FileExtensionValidator`` se base uniquement sur le nom de fichier,
    ce qui permet de téléverser un script PHP renommé ``shell.jpg``.
    Cette validation ouvre le contenu avec Pillow pour s'assurer qu'il
    s'agit d'une vraie image (PNG, JPEG, WEBP, GIF, BMP, TIFF...).
    """
    try:
        value.seek(0)
        with Image.open(value) as img:
            img.verify()
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        raise ValidationError("Le fichier n'est pas une image valide.") from exc
    finally:
        try:
            value.seek(0)
        except (AttributeError, ValueError):
            pass
