import hashlib
import ipaddress
import logging
import os
import unicodedata
from pathlib import Path

from django.conf import settings
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)


def get_client_ip(request):
    """
    Récupère l'adresse IP réelle du client en tenant compte des proxys/CDN.

    Ordre de priorité :
    1. ``HTTP_X_FORWARDED_FOR`` (1ère IP de la liste)
    2. ``X-Real-IP`` (nginx)
    3. ``REMOTE_ADDR`` (fallback WSGI)

    Toutes les IP candidates sont validées via ``ipaddress.ip_address``
    pour éviter l'injection d'en-têtes hostiles. La valeur retournée
    est une string normalisée ou ``"unknown"`` si rien n'est valide.
    """
    candidates = []

    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        # XFF peut être une liste "client, proxy1, proxy2"
        candidates.append(xff.split(",")[0].strip())

    real_ip = request.META.get("HTTP_X_REAL_IP")
    if real_ip:
        candidates.append(real_ip.strip())

    candidates.append(request.META.get("REMOTE_ADDR", ""))

    for raw in candidates:
        if not raw:
            continue
        try:
            ipaddress.ip_address(raw)
            return raw
        except ValueError:
            logger.debug("IP candidate invalide ignoree: %r", raw)
            continue

    return "unknown"


def hash_ip(ip, salt=None):
    """
    Hache une IP (SHA-256 + sel) pour stockage conforme RGPD.
    Le sel par defaut est ``settings.SECRET_KEY`` (rotation manuelle).
    """
    if not ip or ip == "unknown":
        return ""
    actual_salt = salt or settings.SECRET_KEY
    return hashlib.sha256(f"{actual_salt}:{ip}".encode("utf-8")).hexdigest()


def _is_within_media(path_str):
    """
    Vérifie que ``path_str`` est strictement contenu dans ``MEDIA_ROOT``.

    Utilise ``os.path.commonpath`` pour éviter le piège classique du
    ``startswith`` (ex: ``MEDIA_ROOT=/media`` valide à tort ``/media_evil/...``
    sur certains OS).
    """
    media_root = os.fspath(settings.MEDIA_ROOT)
    target = os.path.abspath(os.path.normpath(path_str))
    root = os.path.abspath(os.path.normpath(media_root))
    try:
        return os.path.commonpath([root, target]) == root
    except ValueError:
        # Chemins sur des lecteurs differents sous Windows
        return False


def remove_accents(input_str):
    """
    Supprime les accents d'une chaîne de caractères pour le tri alphabétique.

    Compatible SQLite (Python pur). En PostgreSQL, préférer l'extension
    `unaccent` (django.contrib.postgres.unaccent) qui fait le même travail
    au niveau de la base de données.
    """
    if not input_str:
        return ""
    nfkd_form = unicodedata.normalize("NFKD", input_str)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])


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
        if not file_field:
            return False

        if not hasattr(file_field, "path"):
            logger.warning("Le champ fichier n'a pas d'attribut 'path'")
            return False

        file_path = file_field.path

        if not _is_within_media(file_path):
            error_msg = (
                f"Tentative d'accès à un fichier hors du répertoire autorisé: "
                f"{os.path.abspath(os.path.normpath(file_path))} "
                f"(MEDIA_ROOT: {os.fspath(settings.MEDIA_ROOT)})"
            )
            logger.error(error_msg)
            raise ValidationError(error_msg)

        normalized_abs_path = os.path.abspath(os.path.normpath(file_path))

        if not os.path.exists(normalized_abs_path):
            logger.info(f"Fichier non trouvé (déjà supprimé?): {normalized_abs_path}")
            return False

        os.remove(normalized_abs_path)
        logger.info(f"Fichier supprimé avec succès: {normalized_abs_path}")
        return True

    except ValidationError:
        raise
    except Exception as e:
        logger.error(
            f"Erreur lors de la suppression sécurisée du fichier: {e}", exc_info=True
        )
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
        if not file_path_str:
            return False

        if not _is_within_media(file_path_str):
            error_msg = (
                f"Tentative d'accès à un fichier hors du répertoire autorisé: "
                f"{os.path.abspath(os.path.normpath(file_path_str))}"
            )
            logger.error(error_msg)
            return False

        normalized_abs_path = os.path.abspath(os.path.normpath(file_path_str))

        if not os.path.exists(normalized_abs_path):
            logger.info(f"Fichier non trouvé: {normalized_abs_path}")
            return False

        os.remove(normalized_abs_path)
        logger.info(f"Fichier supprimé avec succès: {normalized_abs_path}")
        return True

    except Exception as e:
        logger.error(f"Erreur lors de la suppression du fichier: {e}", exc_info=True)
        return False


def normalize_filename(text, max_length=100):
    """
    Nettoie un nom de fichier en supprimant tout caractère non sûr.
    Réduit à ``max_length`` (défaut 100) et insère un timestamp.
    """
    import re
    import time

    if not text:
        return f"file_{int(time.time())}"
    cleaned = re.sub(r"[^A-Za-z0-9_-]+", "-", text).strip("-").lower()
    cleaned = cleaned[:max_length] or f"file_{int(time.time())}"
    return cleaned


def rate_limit(request, action, max_calls=5, window=60, key_prefix="rl"):
    """
    Rate limit simple et partageable entre vues.

    Stratégie : ``cache.add`` (atomique) pour initialiser le compteur,
    puis ``cache.incr`` pour incrémenter. Pas de lock distribué, mais
    suffisant pour un hébergement mutualisé mono-process (LocMem).

    Args:
        request: requête Django.
        action: identifiant logique (ex: ``"contact_form"``, ``"pdf_dl"``).
        max_calls: nombre d'appels autorisés dans la fenêtre.
        window: fenêtre en secondes.
        key_prefix: préfixe de la clé de cache.

    Returns:
        tuple ``(allowed: bool, current: int, limit: int)``.
    """
    from django.core.cache import cache

    client_ip = get_client_ip(request)
    rate_key = f"{key_prefix}:{action}:{client_ip}"
    current = 0
    try:
        created = cache.add(rate_key, 1, timeout=window)
        if created:
            current = 1
        else:
            try:
                current = cache.incr(rate_key)
            except ValueError:
                # La clé a expiré entre add et incr
                cache.set(rate_key, 1, timeout=window)
                current = 1
    except Exception as e:
        # En cas de problème cache, on n'empêche pas la requête (fail-open)
        logger.warning("rate_limit: cache indisponible pour %s: %s", action, e)
        return True, 0, max_calls

    if current > max_calls:
        return False, current, max_calls
    return True, current, max_calls
