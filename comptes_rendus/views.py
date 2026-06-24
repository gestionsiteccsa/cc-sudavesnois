from datetime import timedelta

from django.contrib.auth.decorators import permission_required
from django.db import transaction
from django.db.models import Count, Q
from django.shortcuts import get_list_or_404, get_object_or_404, redirect, render
from django.utils import timezone

from app.utils import secure_file_removal

from .forms import ConseilForm, CRForm
from .models import CompteRendu, Conseil, DocumentConseil


# Partie publique
def comptes_rendus(request):
    comptes_rendus = CompteRendu.get_solo()

    # Afficher les conseils depuis 2 jours avant aujourd'hui (conservés 2 jours après)
    # et limiter aux 5 prochains
    today = timezone.now().date()
    two_days_ago = today - timedelta(days=2)
    conseils = list(Conseil.objects.filter(date__gte=two_days_ago).order_by("date")[:5])

    # Déterminer le prochain conseil à venir (date >= aujourd'hui)
    # Extrait de la liste déjà chargée pour éviter une requête supplémentaire
    next_conseil = next((c for c in conseils if c.date >= today), None)

    context = {
        "comptes_rendus": comptes_rendus,
        "conseils": conseils or None,
        "next_conseil": next_conseil,
    }

    return render(request, "comptes_rendus/comptes-rendus.html", context)


def proces_verbaux(request):
    proces_verbaux = CompteRendu.get_solo()

    context = {
        "proces_verbaux": proces_verbaux,
    }

    return render(request, "comptes_rendus/proces-verbaux.html", context)


# Partie gestion des conseils
@permission_required("comptes_rendus.view_conseil")
def admin_page(request):
    comptes_rendus = CompteRendu.get_solo()

    # Récupérer tous les conseils triés par date décroissante (plus récent en premier)
    today = timezone.now().date()
    all_conseils = Conseil.objects.all().order_by("-date")

    # Statistiques : 1 seule requête aggregate au lieu de 3 count()
    from django.core.paginator import Paginator

    stats = all_conseils.aggregate(
        total=Count("id"),
        a_venir=Count("id", filter=Q(date__gte=today)),
    )
    total_conseils = stats["total"]
    conseils_a_venir = stats["a_venir"]
    conseils_passes = total_conseils - conseils_a_venir

    # Pagination
    paginator = Paginator(all_conseils, 15)  # 15 conseils par page
    page_number = request.GET.get("page")
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
@transaction.atomic
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
                # Snapshot des fichiers à supprimer APRÈS le commit pour ne pas
                # perdre les fichiers si la transaction est annulée
                old_files = []
                for doc in conseil.documents.all():
                    old_files.append(doc.file)
                    doc.delete()
                for f in files:
                    DocumentConseil.objects.create(conseil=conseil, file=f)
                # La suppression effective des fichiers est faite après le
                # commit (on_transaction_commit)
                from django.db import transaction as _tx

                for old_file in old_files:
                    _tx.on_commit(lambda f=old_file: secure_file_removal(f))
            return redirect("comptes_rendus:admin_cr_list")
    else:
        form = ConseilForm(instance=conseil)

    context = {
        "form": form,
        "conseil": conseil,
    }

    return render(request, "comptes_rendus/admin_conseil_edit.html", context)


@permission_required("comptes_rendus.delete_conseil")
@transaction.atomic
def delete_conseil(request, conseil_id):
    """
    Fonction pour supprimer un conseil
    """
    conseil = get_object_or_404(Conseil, id=conseil_id)

    if request.method == "POST":
        # Snapshot des fichiers avant suppression
        files_to_remove = [doc.file for doc in conseil.documents.all()]
        for doc in list(conseil.documents.all()):
            doc.delete()
        conseil.delete()
        # Suppression effective des fichiers après commit
        for f in files_to_remove:
            transaction.on_commit(lambda fl=f: secure_file_removal(fl))

        return redirect("comptes_rendus:admin_cr_list")

    context = {
        "conseil": conseil,
    }

    return render(request, "comptes_rendus/admin_conseil_delete.html", context)


# Partie pour le lien vers les comptes rendus
@permission_required("comptes_rendus.add_compterendu")
@transaction.atomic
def add_cr_link(request):
    """
    Fonction pour ajouter un lien de compte rendu.

    La suppression de l'ancien CompteRendu et la création du nouveau sont
    encapsulées dans une transaction atomique pour éviter la perte de données
    en cas d'échec de form.save().
    """
    if request.method == "POST":
        form = CRForm(request.POST)
        if form.is_valid():
            # Mise à jour atomique du singleton (pk=1) plutôt que
            # delete-all + save (évite la fenêtre sans données)
            CompteRendu.update_or_create(defaults={"link": form.cleaned_data["link"]})
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
