from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.core.cache import cache
from django.db import transaction
from django.db.models import Prefetch
from django.shortcuts import get_list_or_404, get_object_or_404, redirect, render

from app.utils import secure_file_removal
from bureau_communautaire.models import Elus, PageStatus
from conseil_communautaire.models import ConseilMembre

from .forms import CommissionDocForm, CommissionForm, MandatForm
from .models import Commission, CommissionCompetence, Document, Mandat


def commissions(request):
    """
    Affiche la page des commissions.
    Optimisé avec prefetch_related et select_related pour éviter les N+1 queries.
    """
    # Vérifier si la page est active
    is_active, maintenance_message = PageStatus.is_page_active("commissions")

    if not is_active:
        return render(
            request,
            "commissions/maintenance.html",
            {"maintenance_message": maintenance_message},
        )

    # Récupération optimisée avec prefetch_related pour les relations ManyToMany
    elus_prefetch = Prefetch(
        "elus", queryset=Elus.objects.order_by("last_name", "first_name")
    )
    membres_prefetch = Prefetch(
        "membres", queryset=ConseilMembre.objects.order_by("last_name", "first_name")
    )
    commissions_qs = Commission.objects.order_by("title").prefetch_related(
        elus_prefetch, "elus__city", membres_prefetch, "membres__city"
    )
    commissions_list = list(commissions_qs)
    nb_commissions = len(commissions_list) if commissions_list else 0

    # Document et mandat (avec cache de 5 minutes)
    document = cache.get("commissions_document")
    if document is None:
        document = Document.get_solo()
        cache.set("commissions_document", document, 300)

    mandat = cache.get("commissions_mandat")
    if mandat is None:
        mandat = Mandat.objects.first()
        if not mandat:
            # Crée un mandat par défaut si aucun n'existe
            mandat = Mandat(start_year=2020, end_year=2026)
            mandat.save()
        cache.set("commissions_mandat", mandat, 300)

    context = {
        "commissions": commissions_list if commissions_list else None,
        "document": document,
        "nb_commissions": nb_commissions,
        "mandat": mandat,
    }

    return render(request, "commissions/commissions.html", context)


# Partie commission
@permission_required("commissions.add_commission")
def add_commission(request):
    """
    Ajoute une commission à la base de données.
    """
    if request.method == "POST":
        form = CommissionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("commissions:admin_list_commissions")
    else:
        form = CommissionForm()
    return render(request, "commissions/admin_commission_add.html", {"form": form})


@permission_required("commissions.view_commission")
def list_commission(request):
    """
    Affiche la liste des commissions.
    Optimisé pour éviter le double pattern .exists() + requête.
    """
    commissions = list(Commission.objects.all())
    commissions = commissions if commissions else None

    document = Document.get_solo()

    mandat = Mandat.objects.first()
    if not mandat:
        # Crée un mandat par défaut si aucun n'existe
        mandat = Mandat(start_year=2020, end_year=2026)
        mandat.save()

    context = {
        "commissions": commissions,
        "document": document,
        "mandat": mandat,
    }

    return render(request, "commissions/admin_commissions_list.html", context)


@permission_required("commissions.change_commission")
def edit_commission(request, commission_id):
    """
    Modifie une commission existante.
    """
    commission = get_object_or_404(Commission, id=commission_id)
    if request.method == "POST":
        form = CommissionForm(request.POST, instance=commission)
        if form.is_valid():
            form.save()
            return redirect("commissions:admin_list_commissions")
    else:
        form = CommissionForm(instance=commission)
    return render(request, "commissions/admin_commission_edit.html", {"form": form})


# Partie document
@permission_required("commissions.delete_commission")
def delete_commission(request, commission_id):
    """
    Supprime une commission existante.
    """
    commission = get_object_or_404(Commission, id=commission_id)
    if request.method == "POST":
        commission.delete()
        return redirect("commissions:admin_list_commissions")
    return render(
        request, "commissions/admin_commission_delete.html", {"commission": commission}
    )


@permission_required("commissions.add_document")
@transaction.atomic
def add_document(request):
    """
    Ajoute un document à la page de commissions.
    """
    # Revoie vers la liste si un document est déjà présent
    if Document.objects.exists():
        return redirect("commissions:admin_list_commissions")
    else:
        if request.method == "POST":
            form = CommissionDocForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                return redirect("commissions:admin_list_commissions")
        else:
            form = CommissionDocForm()
    return render(request, "commissions/admin_commission_add_doc.html", {"form": form})


@permission_required("commissions.change_document")
@transaction.atomic
def edit_document(request, document_id):
    """
    Modifie un document existant.
    """
    document = get_object_or_404(Document, id=document_id)
    last_document = document.file
    if request.method == "POST":
        form = CommissionDocForm(request.POST, request.FILES, instance=document)
        if form.is_valid():
            form.save(commit=False)
            new_file = document.file
            if last_document != new_file:
                # Suppression effective après commit
                transaction.on_commit(lambda: secure_file_removal(last_document))
            form.save()

            return redirect("commissions:admin_list_commissions")
    else:
        form = CommissionDocForm(instance=document)
    return render(request, "commissions/admin_commission_edit_doc.html", {"form": form})


@permission_required("commissions.delete_document")
@transaction.atomic
def delete_document(request, document_id):
    """
    Supprime une commission existante.
    """
    document = get_object_or_404(Document, id=document_id)
    if request.method == "POST":
        file_to_remove = document.file
        document.delete()
        # Suppression effective du fichier après commit
        transaction.on_commit(lambda: secure_file_removal(file_to_remove))
        return redirect("commissions:admin_list_commissions")
    return render(
        request, "commissions/admin_commission_delete_doc.html", {"document": document}
    )


# Partie mandat
@permission_required("commissions.change_mandat")
def edit_mandat(request, mandat_id):
    """
    Modifie un document existant.
    """
    mandat = get_object_or_404(Mandat, id=mandat_id)
    if request.method == "POST":
        form = MandatForm(request.POST, request.FILES, instance=mandat)
        if form.is_valid() and (
            form.cleaned_data["start_year"] < form.cleaned_data["end_year"]
        ):
            form.save()
            return redirect("commissions:admin_list_commissions")
    else:
        form = MandatForm(instance=mandat)
    return render(
        request, "commissions/admin_commission_edit_mandat.html", {"form": form}
    )


# Partie gestion du statut de page
@permission_required("commissions.view_commission")
def manage_page_status(request):
    """
    Gère le statut de la page commissions.
    Permet d'activer/désactiver la page et de personnaliser le message de maintenance.
    """
    # Récupérer ou créer le statut de la page
    page_status, created = PageStatus.objects.get_or_create(
        page_name="commissions",
        defaults={
            "is_active": True,
            "maintenance_message": "La page est en cours de mise à jour.",
        },
    )

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "toggle":
            # Inverser le statut actif/inactif
            page_status.is_active = not page_status.is_active
            page_status.save()
            messages.success(
                request,
                f"La page a été {'activée' if page_status.is_active else 'mise en maintenance'}.",
            )
            return redirect("commissions:admin_page_status")

        elif action == "update_message":
            # Mettre à jour le message de maintenance
            new_message = request.POST.get("maintenance_message", "").strip()
            if new_message:
                page_status.maintenance_message = new_message
                page_status.save()
                messages.success(request, "Le message de maintenance a été mis à jour.")
            else:
                messages.error(request, "Le message ne peut pas être vide.")
            return redirect("commissions:admin_page_status")

    context = {
        "page_status": page_status,
        "page_name_display": page_status.get_page_name_display(),
    }

    return render(request, "commissions/admin_page_status.html", context)


@permission_required("commissions.view_commission")
def list_commission_competences(request):
    """Affiche la liste des commissions avec leurs compétences."""
    commissions_qs = Commission.objects.order_by("title").prefetch_related(
        "competences"
    )
    commissions = list(commissions_qs)
    commissions = commissions if commissions else None

    context = {
        "commissions": commissions,
    }
    return render(request, "commissions/admin_competences_list.html", context)


@permission_required("commissions.add_commission")
def add_competence(request):
    """Ajoute une compétence à une commission."""
    if request.method == "POST":
        commission_id = request.POST.get("commission")
        title = request.POST.get("title", "").strip()
        order = request.POST.get("order", 0)
        if commission_id and title:
            CommissionCompetence.objects.create(
                commission_id=commission_id,
                title=title,
                order=int(order) if str(order).isdigit() else 0,
            )
            messages.success(request, "Compétence ajoutée avec succès.")
        else:
            messages.error(request, "Veuillez remplir tous les champs obligatoires.")
    return redirect("commissions:admin_competences")


@permission_required("commissions.delete_commission")
def delete_competence(request, pk):
    """Supprime une compétence."""
    competence = get_object_or_404(CommissionCompetence, pk=pk)
    if request.method == "POST":
        competence.delete()
        messages.success(request, "Compétence supprimée.")
    return redirect("commissions:admin_competences")
