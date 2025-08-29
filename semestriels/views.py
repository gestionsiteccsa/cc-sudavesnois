from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import SemestrielForm
from .models import SemestrielPage


def semestriel(request):
    if SemestrielPage.objects.exists():
        content = get_object_or_404(SemestrielPage)
    else:
        content = None

    context = {
        "content": content,
    }

    return render(request, "semestriel/semestriel.html", context)


@permission_required("semestriels.add_semestrielpage")
def add_content(request):
    """
    Fonction de vue pour ajouter un calendrier semestriel
    """
    if request.method == "POST":
        form = SemestrielForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("semestriels:list_content")
    else:
        form = SemestrielForm()

    context = {
        "form": form,
    }

    return render(request, "semestriel/admin_content_add.html", context)


@permission_required("semestriels.change_semestrielpage")
def edit_content(request, pk):
    """
    Fonction de vue pour modifier un calendrier semestriel
    """
    content = get_object_or_404(SemestrielPage, pk=pk)

    if request.method == "POST":
        form = SemestrielForm(request.POST, request.FILES, instance=content)
        if form.is_valid():
            form.save()
            return redirect("semestriels:list_content")
    else:
        form = SemestrielForm(instance=content)

    context = {
        "form": form,
    }

    return render(request, "semestriel/admin_content_edit.html", context)


@permission_required("semestriels.view_event")
def list_content(request):
    """
    Fonction de vue pour lister le contenu de la page Semestriels
    """
    if SemestrielPage.objects.exists():
        content = get_object_or_404(SemestrielPage)
    else:
        content = None

    context = {
        "content": content,
    }

    return render(request, "semestriel/admin_content_list.html", context)
