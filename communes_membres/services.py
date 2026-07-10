"""
Service SOLID pour la page publique listant les communes membres.

Single Responsibility : encapsule toute la logique métier de la page
``communes_list`` (requête, cache, transformation en contexte de card,
fallback d'image) afin que la vue reste un contrôleur mince.

Respecte les principes :
- S : une seule raison de changer (formatage de la liste publique).
- O : ajout de filtres (par lettre, par population...) sans modifier la vue.
- I : méthodes publiques fines, indépendantes les unes des autres.
- D : la vue dépend du service, pas de l'ORM directement.
"""

from __future__ import annotations

from typing import Any

from django.conf import settings
from django.core.cache import cache
from django.db.models import QuerySet
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import SafeString

from conseil_communautaire.models import ConseilVille

CACHE_KEY_COMMUNES_LIST = "communes_list_public"
CACHE_TTL_COMMUNES_LIST = 300

SLOGAN_FALLBACK = "Commune membre de la Communauté de Communes Sud-Avesnois."

LISTING_ONLY_FIELDS = (
    "city_name",
    "slug",
    "slogan",
    "nb_habitants",
    "image",
)


class CommuneListingService:
    """Service de listing public des communes membres (SOLID)."""

    @staticmethod
    def get_communes_for_listing() -> QuerySet[ConseilVille]:
        """Retourne les communes triées alphabétiquement, avec cache 5 min.

        Ne charge que les colonnes nécessaires à l'affichage des cards
        (``city_name``, ``slug``, ``slogan``, ``nb_habitants``, ``image``),
        évitant ainsi les problèmes de N+1 et de performance.
        """
        communes = cache.get(CACHE_KEY_COMMUNES_LIST)
        if communes is None:
            communes = list(
                ConseilVille.objects.only(*LISTING_ONLY_FIELDS).order_by("city_name")
            )
            cache.set(CACHE_KEY_COMMUNES_LIST, communes, CACHE_TTL_COMMUNES_LIST)
        return communes

    @staticmethod
    def get_placeholder_image_url() -> str:
        """URL de l'image placeholder (logo CCSA) utilisée si pas d'image."""
        return getattr(
            settings,
            "COMMUNES_PLACEHOLDER_IMAGE_URL",
            "/static/img/logo/Logo_S-A.png",
        )

    @staticmethod
    def get_card_context(commune: ConseilVille) -> dict[str, Any]:
        """Construit le contexte d'une card pour le template.

        Retourne un dictionnaire avec toutes les variables nécessaires à
        l'affichage d'une card accessible (RGAA 1.1, 3.1, 4.1) :

        - ``commune``        : instance ConseilVille
        - ``title``          : nom de la commune (libellé H2)
        - ``image_url``      : URL de l'image (ou placeholder)
        - ``alt_text``       : attribut alt descriptif (RGAA 1.1)
        - ``slogan``         : slogan de la commune ou fallback
        - ``detail_url``     : URL de la fiche détail
        - ``heading_id``     : identifiant ARIA du H2
        """
        has_image = bool(getattr(commune.image, "name", None))
        image_url = (
            commune.image.url
            if has_image
            else CommuneListingService.get_placeholder_image_url()
        )
        slogan = commune.slogan if commune.slogan else SLOGAN_FALLBACK
        slug = commune.slug or "commune"
        return {
            "commune": commune,
            "title": commune.city_name,
            "image_url": image_url,
            "alt_text": f"Vue de la commune de {commune.city_name}",
            "slogan": slogan,
            "detail_url": reverse("communes-membres:commune", args=[slug]),
            "heading_id": f"commune-{slug}",
            "nb_habitants": commune.nb_habitants or 0,
        }

    @staticmethod
    def get_listing_context() -> dict[str, Any]:
        """Construit le contexte complet de la page de listing."""
        communes = CommuneListingService.get_communes_for_listing()
        cards = [CommuneListingService.get_card_context(c) for c in communes]
        return {
            "communes": communes,
            "cards": cards,
            "total": len(cards),
        }

    @staticmethod
    def invalidate_cache() -> None:
        """Invalide le cache (à appeler depuis l'admin lors d'une modification)."""
        cache.delete(CACHE_KEY_COMMUNES_LIST)


def render_card_image_alt(alt_text: str) -> SafeString:
    """Helper exporté pour l'attribut alt dans le template (sécurité échappement)."""
    return format_html("{}", alt_text)
