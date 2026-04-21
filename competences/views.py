from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_list_or_404, get_object_or_404, redirect, render

from .forms import CompetenceForm
from .models import Competence


def competences(request):
    if Competence.objects.filter(category=Competence.Category.OBLIGATOIRE).exists():
        c_obligatoires = Competence.objects.filter(
            category=Competence.Category.OBLIGATOIRE
        )
    else:
        c_obligatoires = None

    if Competence.objects.filter(category=Competence.Category.OPTIONNELLE).exists():
        c_optionnelles = Competence.objects.filter(
            category=Competence.Category.OPTIONNELLE
        )
    else:
        c_optionnelles = None

    if Competence.objects.filter(category=Competence.Category.FACULTATIVE).exists():
        c_facultatives = Competence.objects.filter(
            category=Competence.Category.FACULTATIVE
        )
    else:
        c_facultatives = None

    if Competence.objects.filter(category=Competence.Category.TRANSFEREE).exists():
        c_transferees = Competence.objects.filter(
            category=Competence.Category.TRANSFEREE
        )
    else:
        c_transferees = None

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

    stats = {
        "total": competences.count(),
        "obligatoire": competences.filter(category=Competence.Category.OBLIGATOIRE).count(),
        "optionnelle": competences.filter(category=Competence.Category.OPTIONNELLE).count(),
        "facultative": competences.filter(category=Competence.Category.FACULTATIVE).count(),
        "transferee": competences.filter(category=Competence.Category.TRANSFEREE).count(),
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
