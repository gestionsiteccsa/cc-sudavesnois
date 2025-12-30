import os
from datetime import timedelta

from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_list_or_404, get_object_or_404, redirect, render
from django.utils import timezone

from .forms import ConseilForm, CRForm
from .models import CompteRendu, Conseil


# Partie publique
def comptes_rendus(request):
    if CompteRendu.objects.exists():
        comptes_rendus = get_object_or_404(CompteRendu)
    else:
        comptes_rendus = None

    # Filtrer les conseils avec date >= j+1 et trier par date croissante
    tomorrow = timezone.now().date() + timedelta(days=1)
    conseils = Conseil.objects.filter(date__gte=tomorrow).order_by("date")
    if not conseils.exists():
        conseils = None

    context = {
        "comptes_rendus": comptes_rendus,
        "conseils": conseils,
    }

    return render(request, "comptes_rendus/comptes-rendus.html", context)


def proces_verbaux(request):
    if CompteRendu.objects.exists():
        proces_verbaux = get_object_or_404(CompteRendu)
    else:
        proces_verbaux = None

    context = {
        "proces_verbaux": proces_verbaux,
    }

    return render(request, "comptes_rendus/proces-verbaux.html", context)


# Partie gestion des conseils
@permission_required("comptes_rendus.view_conseil")
def admin_page(request):
    if CompteRendu.objects.exists():
        comptes_rendus = get_object_or_404(CompteRendu)
    else:
        comptes_rendus = None

    if Conseil.objects.exists():
        conseils = get_list_or_404(Conseil.objects.order_by("date"))
    else:
        conseils = None

    context = {
        "comptes_rendus": comptes_rendus,
        "conseils": conseils,
    }

    return render(request, "comptes_rendus/admin_page.html", context)


@permission_required("comptes_rendus.add_conseil")
def add_conseil(request):
    """
    Fonction pour ajouter un conseil
    """
    if request.method == "POST":
        form = ConseilForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("comptes_rendus:admin_cr_list")
    else:
        form = ConseilForm()

    context = {
        "form": form,
    }

    return render(request, "comptes_rendus/admin_conseil_add.html", context)


@permission_required("comptes_rendus.change_conseil")
def edit_conseil(request, conseil_id):
    """
    Fonction pour éditer un conseil
    """
    conseil = get_object_or_404(Conseil, id=conseil_id)
    last_day_order = conseil.day_order

    if request.method == "POST":
        form = ConseilForm(request.POST, request.FILES, instance=conseil)
        if form.is_valid():
            conseil = form.save(commit=False)
            if conseil.day_order != last_day_order:
                if os.path.exists(last_day_order.path):
                    os.remove(last_day_order.path)
            form.save()
            return redirect("comptes_rendus:admin_cr_list")
    else:
        form = ConseilForm(instance=conseil)

    context = {
        "form": form,
        "conseil": conseil,
    }

    return render(request, "comptes_rendus/admin_conseil_edit.html", context)


@permission_required("comptes_rendus.delete_conseil")
def delete_conseil(request, conseil_id):
    """
    Fonction pour supprimer un conseil
    """
    conseil = get_object_or_404(Conseil, id=conseil_id)

    if request.method == "POST":
        if conseil.day_order:
            if os.path.exists(conseil.day_order.path):
                os.remove(conseil.day_order.path)
        conseil.delete()

        return redirect("comptes_rendus:admin_cr_list")

    context = {
        "conseil": conseil,
    }

    return render(request, "comptes_rendus/admin_conseil_delete.html", context)


# Partie pour le lien vers les comptes rendus
@permission_required("comptes_rendus.add_compterendu")
def add_cr_link(request):
    """
    Fonction pour ajouter un lien de compte rendu
    """
    if request.method == "POST":
        form = CRForm(request.POST)
        if form.is_valid():
            CompteRendu.objects.all().delete()  # Supprime les anciens liens
            form.save()
            return redirect("comptes_rendus:admin_cr_list")
    else:
        form = CRForm()

    context = {
        "form": form,
    }

    return render(request, "comptes_rendus/admin_cr_link_add.html", context)


@permission_required("comptes_rendus.change_compterendu")
def edit_cr_link(request, cr_id):
    """
    Fonction pour éditer un lien de compte rendu
    """
    cr = get_object_or_404(CompteRendu, id=cr_id)

    if request.method == "POST":
        form = CRForm(request.POST, instance=cr)
        if form.is_valid():
            form.save()
            return redirect("comptes_rendus:admin_cr_list")
    else:
        form = CRForm(instance=cr)

    context = {
        "form": form,
        "cr": cr,
    }

    return render(request, "comptes_rendus/admin_cr_link_edit.html", context)


@permission_required("comptes_rendus.delete_compterendu")
def delete_cr_link(request, cr_id):
    """
    Fonction pour supprimer un lien de compte rendu
    """
    cr = get_object_or_404(CompteRendu, id=cr_id)

    if request.method == "POST":
        cr.delete()

        return redirect("comptes_rendus:admin_cr_list")

    context = {
        "cr": cr,
    }

    return render(request, "comptes_rendus/admin_cr_link_delete.html", context)
