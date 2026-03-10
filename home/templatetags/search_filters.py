from django import template
from django.utils.safestring import mark_safe
import re

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
    
    # Remplacer les termes trouvés par leur version en gras (insensible à la casse)
    highlighted = re.sub(
        f'({escaped_query})',
        r'<mark class="bg-yellow-200 dark:bg-yellow-700 px-1 rounded">\1</mark>',
        str(text),
        flags=re.IGNORECASE
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
