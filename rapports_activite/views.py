import os

from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_list_or_404, get_object_or_404, redirect, render

from .forms import RapportActiviteForm
from .models import RapportActivite

accueil = "rapports_activite/rapports-activite.html"
ajout_rapport = "rapports_activite/admin-rapport-add.html"
gestion_rapport = "rapports_activite/admin-manage-rapports-activite.html"
modifier_rapport = "rapports_activite/admin-rapport-edit.html"
supprimer_rapport = "rapports_activite/admin-rapport-delete.html"


def rapports_activite(request):
    """
    View function to render the 'rapports_activite' page.
    """
    if RapportActivite.objects.exists():
        rapports = get_list_or_404(RapportActivite.objects.all().order_by("-year"))
        rapport_recents = rapports[:4]
        archive = rapports[4:]
    else:
        rapport_recents = None
        archive = None

    context = {
        "rapport_recents": rapport_recents,
        "archive": archive,
    }

    return render(request, accueil, context)


@permission_required("rapports_activite.view_rapportactivite")
def manage_rapports_activite(request):
    """
    View function to render the 'manage_rapports_activite' page.
    """
    if RapportActivite.objects.exists():
        rapports = get_list_or_404(RapportActivite.objects.all().order_by("-year"))
    else:
        rapports = None

    context = {
        "rapports": rapports,
    }

    return render(request, gestion_rapport, context)


@permission_required("rapports_activite.add_rapportactivite")
def add_rapport_activite(request):
    """
    View function to render the 'add_rapport_activite' page.
    """
    if request.method == "POST":
        form = RapportActiviteForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("rapports_activite:gestion_rapports_activite")
    else:
        form = RapportActiviteForm()
    return render(request, ajout_rapport, {"form": form})


@permission_required("rapports_activite.change_rapportactivite")
def edit_rapport_activite(request, id):
    """
    View function to render the 'edit_rapport_activite' page.
    """
    rapport = get_object_or_404(RapportActivite, pk=id)
    last_file = rapport.file

    if request.method == "POST":
        form = RapportActiviteForm(request.POST, request.FILES, instance=rapport)
        if form.is_valid():
            rapport = form.save(commit=False)
            if rapport.file != last_file:
                if os.path.exists(last_file.path):
                    os.remove(last_file.path)
            rapport.save()
            return redirect("rapports_activite:gestion_rapports_activite")
    else:
        form = RapportActiviteForm(instance=rapport)
    return render(request, modifier_rapport, {"form": form})


@permission_required("rapports_activite.delete_rapportactivite")
def delete_rapport_activite(request, id):
    """
    View function to delete a 'rapport_activite' instance.
    """
    rapport = get_object_or_404(RapportActivite, pk=id)
    if request.method == "POST":
        if os.path.exists(rapport.file.path):
            os.remove(rapport.file.path)
        rapport.delete()
        return redirect("rapports_activite:gestion_rapports_activite")
    return render(request, supprimer_rapport, {"form": rapport})
