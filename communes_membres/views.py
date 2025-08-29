import os

from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_list_or_404, get_object_or_404, redirect, render

from conseil_communautaire.models import ConseilVille

from .forms import ActesLocForm
from .models import ActeLocal


def commune(request, slug):
    """
    Affiche les détails de la commune membre de la communauté de communes.
    """
    # Récupérer la commune à partir du slug
    try:
        commune = ConseilVille.objects.get(slug=slug)
    except ConseilVille.DoesNotExist:
        return render(request, "communes_membres/commune_no_ville.html", status=200)

    if ActeLocal.objects.filter(commune=commune).exists():
        acte = get_object_or_404(ActeLocal, commune=commune)
    else:
        acte = ActeLocal(
            id="0", title=None, date=None, description=None, commune=commune, file="/"
        )

    context = {
        "commune": commune,
        "acte": acte,
    }

    return render(request, "communes_membres/commune.html", context)


@permission_required("communes_membres.add_actelocal")
def add_acte_local(request):
    """
    Affiche le formulaire pour ajouter un acte local.
    """
    if request.method == "POST":
        form = ActesLocForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("communes-membres:admin_acte_list")
    else:
        form = ActesLocForm()

    return render(request, "communes_membres/admin_acte_add.html", {"form_acte": form})


@permission_required("communes_membres.view_actelocal")
def list_acte_local(request):
    """
    Affiche la liste des actes locaux.
    """
    # Récupérer tous les actes locaux
    if ActeLocal.objects.exists():
        actes_locaux = get_list_or_404(ActeLocal)
    else:
        actes_locaux = [
            ActeLocal(id="-1", date=None, description=None, commune=None, file="/")
        ]

    return render(
        request, "communes_membres/admin_acte_list.html", {"actes_locaux": actes_locaux}
    )


@permission_required("communes_membres.delete_actelocal")
def delete_acte_local(request, id):
    """
    Supprime un acte local.
    """
    # Récupérer l'acte local à partir de l'ID
    acte_local = get_object_or_404(ActeLocal, id=id)

    if request.method == "POST":
        acte_local.delete()
        return redirect("communes-membres:admin_acte_list")

    return render(
        request, "communes_membres/admin_acte_delete.html", {"acte_local": acte_local}
    )


@permission_required("communes_membres.change_actelocal")
def update_acte_local(request, id):
    """
    Modifie un acte local.
    """
    # Récupérer l'acte local à partir de l'ID
    acte_local = get_object_or_404(ActeLocal, id=id)
    fichier = acte_local.file

    if request.method == "POST":
        form = ActesLocForm(request.POST, request.FILES, instance=acte_local)
        if form.is_valid():
            acte_local = form.save(commit=False)
            # Vérifier si le fichier a été modifié
            if acte_local.file != fichier:
                if os.path.exists(fichier.path):
                    os.remove(fichier.path)
            form.save()

            return redirect("communes-membres:admin_acte_list")
    else:
        form = ActesLocForm(instance=acte_local)

    return render(request, "communes_membres/admin_acte_edit.html", {"form_acte": form})
