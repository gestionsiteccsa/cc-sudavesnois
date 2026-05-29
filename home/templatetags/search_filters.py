import re

from django import template
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def highlight(text, query):
    """
    Met en gras les termes de la recherche dans le texte.
    """
    if not text or not query:
        return text

    # Échapper les caractères spéciaux de regex
    escaped_query = re.escape(query)

    # Remplacer les termes trouvés par leur version surlignée (insensible à la casse)
    # On utilise une fonction de remplacement pour préserver la casse originale
    # tout en échappant le HTML potentiel dans le texte
    def _wrap_match(m):
        return f'<mark class="bg-yellow-200 dark:bg-yellow-700 px-1 rounded">{conditional_escape(m.group(1))}</mark>'

    highlighted = re.sub(
        f"({escaped_query})", _wrap_match, str(text), flags=re.IGNORECASE
    )

    return mark_safe(highlighted)


@register.filter
def split_words(query):
    """
    Divise la requête en mots pour la recherche de suggestions.
    """
    if not query:
        return []
    return query.split()
