import logging
import os
from django.conf import settings
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)


def secure_file_removal(file_field):
    """
    Supprime un fichier de manière sécurisée en vérifiant le chemin.
    
    Cette fonction protège contre les attaques d'injection de chemin (Path Traversal)
    en s'assurant que le fichier est bien dans le répertoire MEDIA autorisé.
    
    Args:
        file_field: Le champ FileField ou ImageField de Django
        
    Returns:
        bool: True si le fichier a été supprimé, False sinon
        
    Raises:
        ValidationError: Si le chemin du fichier est suspect ou invalide
    """
    try:
        # Vérifier que le champ existe
        if not file_field:
            return False
        
        # Obtenir le chemin du fichier de manière sécurisée
        if not hasattr(file_field, 'path'):
            logger.warning("Le champ fichier n'a pas d'attribut 'path'")
            return False
            
        file_path = file_field.path
        
        # Normaliser le chemin pour éviter les attaques de traversal (../)
        normalized_path = os.path.normpath(file_path)
        
        # Obtenir le répertoire MEDIA_ROOT normalisé
        media_root = str(settings.MEDIA_ROOT)
        if isinstance(media_root, os.PathLike):
            media_root = os.fspath(media_root)
        normalized_media_root = os.path.normpath(os.path.abspath(media_root))
        
        # Vérifier que le fichier est bien dans le répertoire MEDIA
        normalized_abs_path = os.path.abspath(normalized_path)
        
        if not normalized_abs_path.startswith(normalized_media_root):
            error_msg = (
                f"Tentative d'accès à un fichier hors du répertoire autorisé: "
                f"{normalized_abs_path} (MEDIA_ROOT: {normalized_media_root})"
            )
            logger.error(error_msg)
            raise ValidationError(error_msg)
        
        # Vérifier que le fichier existe avant de le supprimer
        if not os.path.exists(normalized_abs_path):
            logger.info(f"Fichier non trouvé (déjà supprimé?): {normalized_abs_path}")
            return False
        
        # Supprimer le fichier de manière sécurisée
        os.remove(normalized_abs_path)
        logger.info(f"Fichier supprimé avec succès: {normalized_abs_path}")
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de la suppression sécurisée du fichier: {e}", exc_info=True)
        # Ne pas faire échouer toute la requête à cause d'une erreur de fichier
        return False


def secure_file_removal_by_path(file_path_str):
    """
    Supprime un fichier par son chemin de manière sécurisée.
    
    Cette fonction protège contre les attaques d'injection de chemin (Path Traversal)
    en s'assurant que le fichier est bien dans le répertoire MEDIA autorisé.
    
    Args:
        file_path_str: Le chemin du fichier à supprimer (str)
        
    Returns:
        bool: True si le fichier a été supprimé, False sinon
    """
    try:
        # Normaliser le chemin
        normalized_path = os.path.normpath(file_path_str)
        
        # Obtenir le répertoire MEDIA_ROOT
        media_root = str(settings.MEDIA_ROOT)
        if isinstance(media_root, os.PathLike):
            media_root = os.fspath(media_root)
        normalized_media_root = os.path.normpath(os.path.abspath(media_root))
        
        # Vérifier que le fichier est bien dans le répertoire MEDIA
        normalized_abs_path = os.path.abspath(normalized_path)
        
        if not normalized_abs_path.startswith(normalized_media_root):
            error_msg = (
                f"Tentative d'accès à un fichier hors du répertoire autorisé: "
                f"{normalized_abs_path}"
            )
            logger.error(error_msg)
            return False
        
        # Vérifier que le fichier existe avant de le supprimer
        if not os.path.exists(normalized_abs_path):
            logger.info(f"Fichier non trouvé: {normalized_abs_path}")
            return False
        
        # Supprimer le fichier
        os.remove(normalized_abs_path)
        logger.info(f"Fichier supprimé avec succès: {normalized_abs_path}")
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de la suppression du fichier: {e}", exc_info=True)
        return False

