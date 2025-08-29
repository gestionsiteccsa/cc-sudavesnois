from django.shortcuts import get_list_or_404

from conseil_communautaire.models import ConseilVille


def get_cities(request):
    """
    Context processor to add the list of cities to the context.
    """
    if ConseilVille.objects.exists():
        cities = get_list_or_404(ConseilVille)
    else:
        cities = None
    return {"cities": cities}
