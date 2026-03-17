from django.core.cache import cache

from conseil_communautaire.models import ConseilVille


def get_cities(request):
    """
    Context processor to add the list of cities to the context.
    Optimisé avec cache pour éviter les requêtes sur chaque page.
    """
    # Utilisation du cache pour éviter les requêtes sur chaque page
    cities = cache.get('all_cities')
    if cities is None:
        cities = list(ConseilVille.objects.all().order_by('city_name'))
        cache.set('all_cities', cities, 300)  # Cache pour 5 minutes
    return {"cities": cities if cities else None}
