from django.contrib.auth.decorators import permission_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from app.utils import secure_file_removal

from .forms import SemestrielForm
from .models import SemestrielPage


def semestriel(request):
    content = SemestrielPage.get_solo()

    context = {
        "content": content,
    }

    return render(request, "semestriel/semestriel.html", context)


@permission_required("semestriels.add_semestrielpage")
@transaction.atomic
def add_content(request):
    """
    Fonction de vue pour ajouter un calendrier semestriel
    """
    if SemestrielPage.objects.exists():
        return redirect("semestriels:list_content")
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
@transaction.atomic
def edit_content(request, pk):
    """
    Fonction de vue pour modifier un calendrier semestriel
    """
    content = get_object_or_404(SemestrielPage, pk=pk)
    last_picture = content.picture
    last_file = content.file

    if request.method == "POST":
        form = SemestrielForm(request.POST, request.FILES, instance=content)
        if form.is_valid():
            form.save(commit=False)
            new_picture = content.picture
            new_file = content.file
            if last_picture and last_picture != new_picture:
                transaction.on_commit(lambda p=last_picture: secure_file_removal(p))
            if last_file and last_file != new_file:
                transaction.on_commit(lambda f=last_file: secure_file_removal(f))
            form.save()
            return redirect("semestriels:list_content")
    else:
        form = SemestrielForm(instance=content)

    context = {
        "form": form,
        "content": content,
    }

    return render(request, "semestriel/admin_content_edit.html", context)


@permission_required("semestriels.view_event")
def list_content(request):
    content = SemestrielPage.get_solo()

    context = {
        "content": content,
    }

    return render(request, "semestriel/admin_content_list.html", context)
