import os

from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_list_or_404, get_object_or_404, redirect, render

from bureau_communautaire.models import Elus
from conseil_communautaire.models import ConseilMembre

from .forms import CommissionDocForm, CommissionForm, MandatForm
from .models import Commission, Document, Mandat


def commissions(request):
    """
    Affiche la page des commissions.
    Optimisé avec prefetch_related et select_related pour éviter les N+1 queries.
    """
    # Récupération optimisée avec prefetch_related pour la relation ManyToMany Elus
    # Le related_name est "elus" (défini dans le modèle Elus)
    commissions_qs = Commission.objects.prefetch_related('elus')
    commissions_list = list(commissions_qs)
    nb_commissions = len(commissions_list) if commissions_list else 0
    
    # Récupération optimisée des élus avec select_related pour city
    elus_qs = Elus.objects.select_related('city')
    elus_list = list(elus_qs)
    
    # Récupération optimisée des membres avec select_related pour city et linked_commission
    # linked_commission est une ForeignKey vers Commission
    membres_qs = ConseilMembre.objects.select_related('city', 'linked_commission')
    membres_list = list(membres_qs)
    
    # Document et mandat
    document = Document.objects.first()
    
    mandat = Mandat.objects.first()
    if not mandat:
        # Crée un mandat par défaut si aucun n'existe
        mandat = Mandat(start_year=2020, end_year=2026)
        mandat.save()

    context = {
        "commissions": commissions_list if commissions_list else None,
        "document": document,
        "nb_commissions": nb_commissions,
        "mandat": mandat,
        "elus": elus_list if elus_list else None,
        "membres": membres_list if membres_list else None,
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
    
    document = Document.objects.first()
    
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
def add_document(request):
    """
    Ajoute un document à la page de commissions.
    """
    # Revoie vers la liste si un document est déjà présent
    if Document.objects.count() >= 1:
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
            if last_document != document.file:
                # Supprime l'ancien fichier
                os.remove(last_document.path)
            form.save()

            return redirect("commissions:admin_list_commissions")
    else:
        form = CommissionDocForm(instance=document)
    return render(request, "commissions/admin_commission_edit_doc.html", {"form": form})


@permission_required("commissions.delete_document")
def delete_document(request, document_id):
    """
    Supprime une commission existante.
    """
    document = get_object_or_404(Document, id=document_id)
    if request.method == "POST":
        os.remove(document.file.path)  # Supprime le fichier
        document.delete()
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
