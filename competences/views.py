from collections import Counter

from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_list_or_404, get_object_or_404, redirect, render

from .forms import CompetenceForm
from .models import Competence


def competences(request):
    toutes = Competence.objects.all()
    c_obligatoires = [
        c for c in toutes if c.category == Competence.Category.OBLIGATOIRE
    ] or None
    c_optionnelles = [
        c for c in toutes if c.category == Competence.Category.OPTIONNELLE
    ] or None
    c_facultatives = [
        c for c in toutes if c.category == Competence.Category.FACULTATIVE
    ] or None
    c_transferees = [
        c for c in toutes if c.category == Competence.Category.TRANSFEREE
    ] or None

    context = {
        "c_obligatoires": c_obligatoires,
        "c_optionnelles": c_optionnelles,
        "c_facultatives": c_facultatives,
        "c_transferees": c_transferees,
    }

    return render(request, "competences/competences.html", context)


@permission_required("competences.view_competence")
def competences_list(request):
    """
    Affiche la liste des compétences avec statistiques.
    """
    competences = Competence.objects.all().order_by("category", "title")
    compteurs = dict(Counter(competences.values_list("category", flat=True)))
    stats = {
        "total": len(competences),
        "obligatoire": compteurs.get(Competence.Category.OBLIGATOIRE, 0),
        "optionnelle": compteurs.get(Competence.Category.OPTIONNELLE, 0),
        "facultative": compteurs.get(Competence.Category.FACULTATIVE, 0),
        "transferee": compteurs.get(Competence.Category.TRANSFEREE, 0),
    }

    context = {
        "competences": competences,
        "stats": stats,
    }
    return render(request, "competences/admin_competences_list.html", context)


@permission_required("competences.add_competence")
def add_competence(request):
    """
    Affiche le formulaire pour ajouter une compétence.
    """
    if request.method == "POST":
        form = CompetenceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("competences:admin_competences_list")
    else:
        form = CompetenceForm()

    return render(request, "competences/admin_competence_add.html", {"form": form})


@permission_required("competences.change_competence")
def edit_competence(request, competence_id):
    """
    Affiche le formulaire pour modifier une compétence.
    """
    competence = get_object_or_404(Competence, id=competence_id)
    if request.method == "POST":
        form = CompetenceForm(request.POST, instance=competence)
        if form.is_valid():
            form.save()
            return redirect("competences:admin_competences_list")
    else:
        form = CompetenceForm(instance=competence)

    return render(request, "competences/admin_competence_edit.html", {"form": form})


@permission_required("competences.delete_competence")
def delete_competence(request, competence_id):
    """
    Supprime une compétence.
    """
    form = get_object_or_404(Competence, id=competence_id)
    if request.method == "POST":
        form.delete()
        return redirect("competences:admin_competences_list")

    return render(request, "competences/admin_competence_delete.html", {"form": form})
