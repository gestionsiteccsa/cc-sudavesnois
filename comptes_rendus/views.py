import os
from datetime import timedelta

from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_list_or_404, get_object_or_404, redirect, render
from django.utils import timezone

from .forms import ConseilForm, CRForm
from .models import CompteRendu, Conseil, DocumentConseil


# Partie publique
def comptes_rendus(request):
    if CompteRendu.objects.exists():
        comptes_rendus = get_object_or_404(CompteRendu)
    else:
        comptes_rendus = None

    # Afficher les conseils depuis 2 jours avant aujourd'hui (conservés 2 jours après)
    # et limiter aux 5 prochains
    today = timezone.now().date()
    two_days_ago = today - timedelta(days=2)
    conseils = Conseil.objects.filter(date__gte=two_days_ago).order_by("date")[:5]
    if not conseils:
        conseils = None

    # Déterminer le prochain conseil à venir (date >= aujourd'hui)
    next_conseil = Conseil.objects.filter(date__gte=today).order_by("date").first()

    context = {
        "comptes_rendus": comptes_rendus,
        "conseils": conseils,
        "next_conseil": next_conseil,
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

    # Récupérer tous les conseils triés par date décroissante (plus récent en premier)
    today = timezone.now().date()
    all_conseils = Conseil.objects.all().order_by("-date")
    
    # Statistiques
    total_conseils = all_conseils.count()
    conseils_a_venir = all_conseils.filter(date__gte=today).count()
    conseils_passes = total_conseils - conseils_a_venir
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(all_conseils, 15)  # 15 conseils par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        "comptes_rendus": comptes_rendus,
        "conseils": page_obj,
        "page_obj": page_obj,
        "today": today,
        "total_conseils": total_conseils,
        "conseils_a_venir": conseils_a_venir,
        "conseils_passes": conseils_passes,
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
            conseil = form.save()
            files = request.FILES.getlist("documents")
            for f in files:
                DocumentConseil.objects.create(conseil=conseil, file=f)
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

    if request.method == "POST":
        form = ConseilForm(request.POST, request.FILES, instance=conseil)
        if form.is_valid():
            conseil = form.save()
            # Mettre à jour les titres des documents existants
            for doc in conseil.documents.all():
                title_key = f"doc_title_{doc.id}"
                if title_key in request.POST:
                    new_title = request.POST[title_key].strip()
                    if new_title != doc.title:
                        doc.title = new_title
                        doc.save()
            # Mode écraser/remplacer : supprimer tous les anciens documents
            files = request.FILES.getlist("documents")
            if files:
                for doc in conseil.documents.all():
                    if os.path.exists(doc.file.path):
                        os.remove(doc.file.path)
                    doc.delete()
                for f in files:
                    DocumentConseil.objects.create(conseil=conseil, file=f)
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
        for doc in conseil.documents.all():
            if os.path.exists(doc.file.path):
                os.remove(doc.file.path)
            doc.delete()
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
