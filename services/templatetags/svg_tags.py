"""
Filtres et tags personnalisés pour l'application services.

Le filtre ``render_svg`` permet d'afficher le champ ``Service.icon`` dans
les templates sans ``|safe`` direct. Le contenu est considéré comme sûr
parce qu'il est validé à la saisie par la méthode ``ServiceForm.clean_icon``
(regex stricte ``<svg>...</svg>`` + blacklist de mots-clés dangereux).
"""
import re

from django import template
from django.utils.safestring import mark_safe

register = template.Library()

_SVG_TAG_RE = re.compile(r"^\s*<svg\b[^>]*>.*</svg>\s*$", re.DOTALL | re.IGNORECASE)
_DANGEROUS_RE = re.compile(
    r"(?i)(javascript:|data:|vbscript:|<script\b|on[a-z]+\s*=|<iframe|<object|<embed)"
)


@register.filter(name="render_svg")
def render_svg(value):
    """
    Rend le SVG en mark_safe après une double validation (defense in depth).

    Le contenu du champ ``Service.icon`` est déjà filtré par
    ``ServiceForm.clean_icon`` mais on revérifie ici au cas où des
    données antérieures au déploiement du filtre ne soient pas conformes.
    """
    if not value:
        return ""
    text = str(value).strip()
    if _DANGEROUS_RE.search(text) or not _SVG_TAG_RE.match(text):
        return ""
    return mark_safe(text)
