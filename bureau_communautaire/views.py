import logging
import os

from django.contrib.auth.decorators import permission_required
from django.db.models import Prefetch
from django.shortcuts import get_list_or_404, get_object_or_404, redirect, render

from app.utils import secure_file_removal
from conseil_communautaire.models import Commission
from .forms import DocumentForm, ElusForm
from .models import Document, Elus, PageStatus

logger = logging.getLogger(__name__)


def elus(request):
    """Affiche la page publique des élus."""
    # Vérifier si la page est active
    is_active, maintenance_message = PageStatus.is_page_active("bureau-communautaire")

    if not is_active:
        return render(
            request,
            "bureau_communautaire/maintenance.html",
            {"maintenance_message": maintenance_message},
        )

    # Récupérer les élus avec select_related pour city et prefetch_related pour linked_commission + competences
    commission_prefetch = Prefetch(
        "linked_commission",
        queryset=Commission.objects.prefetch_related("competences"),
    )
    elus_qs = Elus.objects.select_related("city").prefetch_related(commission_prefetch)

    vice_presidents = list(elus_qs.filter(role="Vice-Président"))
    elus = vice_presidents if vice_presidents else None

    president = elus_qs.filter(role="Président").first()

    # Récupérer les documents
    import os

    if Document.objects.exists():
        documents_raw = get_list_or_404(Document)
        documents = []
        for doc in documents_raw:
            # Vérifie l'existence physique du fichier
            try:
                file_path = doc.document.path
            except ValueError:
                file_path = None
            disponible = file_path and os.path.exists(file_path)
            # On ajoute une propriété dynamique pour le template
            doc.disponible = disponible
            documents.append(doc)
    else:
        documents = None
    context = {
        "elus": elus,
        "president": president,
        "documents": documents,
    }
    return render(request, "bureau_communautaire/elus.html", context)


@permission_required("bureau_communautaire.view_elus")
def add_elu(request):
    """Ajoute un élu à la base de données."""
    if request.method == "POST":
        elu_form = ElusForm(request.POST, request.FILES)
        if elu_form.is_valid():
            elu_form.save()
            logger.info("Élu ajouté avec succès")
            return redirect("bureau-communautaire:admin_elus_list")
    else:
        elu_form = ElusForm()
    return render(
        request, "bureau_communautaire/admin_elu_add.html", {"elu_form": elu_form}
    )


@permission_required("bureau_communautaire.view_elus")
def list_elus(request):
    """
    Affiche la liste des élus.
    Optimisé avec select_related pour city et prefetch_related pour linked_commission.
    """
    queryset = Elus.objects.select_related("city").prefetch_related("linked_commission")
    elus = list(queryset)
    stats = {
        "total": queryset.count(),
        "presidents": queryset.filter(role=Elus.Role.PRESIDENT).count(),
        "vice_presidents": queryset.filter(role=Elus.Role.VICE_PRESIDENT).count(),
    }
    return render(
        request,
        "bureau_communautaire/admin_elus_list.html",
        {"elus": elus, "stats": stats},
    )


@permission_required("bureau_communautaire.change_elus")
def update_elu(request, id):
    """Met à jour les informations d'un élu."""
    elu = get_object_or_404(Elus, id=id)
    if request.method == "POST":
        elu_form = ElusForm(request.POST, request.FILES, instance=elu)
        if elu_form.is_valid():
            elu_form.save()
            return redirect("bureau-communautaire:admin_elus_list")
    else:
        elu_form = ElusForm(instance=elu)
    return render(
        request,
        "bureau_communautaire/admin_elu_update.html",
        {"elu": elu, "elu_form": elu_form},
    )


@permission_required("bureau_communautaire.delete_elus")
def delete_elu(request, id):
    """Supprime un élu de la base de données."""
    elu = get_object_or_404(Elus, id=id)
    if request.method == "POST":
        if elu.picture:
            elu.picture.delete(save=False)
        elu.delete()
        return redirect("bureau-communautaire:admin_elus_list")
    return render(request, "bureau_communautaire/admin_elu_delete.html", {"elu": elu})


@permission_required("bureau_communautaire.add_document")
def add_document(request):
    """Ajoute un document à la base de données."""
    if request.method == "POST":
        document_form = DocumentForm(request.POST, request.FILES)
        if document_form.is_valid():
            document_form.save()
            logger.info("Document ajouté avec succès")
            return redirect("bureau-communautaire:admin_documents_list")
        else:
            logger.warning(f"Formulaire de document invalide: {document_form.errors}")
            return render(
                request,
                "bureau_communautaire/admin_document_add.html",
                {"document_form": document_form},
            )
    else:
        document_form = DocumentForm()
    return render(
        request,
        "bureau_communautaire/admin_document_add.html",
        {"document_form": document_form},
    )


@permission_required("bureau_communautaire.view_document")
def list_documents(request):
    """
    Affiche la liste des documents.
    Optimisé pour éviter le double pattern .exists() + requête.
    """
    documents = list(Document.objects.all())
    documents = documents if documents else None

    return render(
        request,
        "bureau_communautaire/admin_document_list.html",
        {"documents": documents},
    )


@permission_required("bureau_communautaire.change_document")
def update_document(request, id):
    """Met à jour les informations d'un document."""
    document = get_object_or_404(Document, id=id)
    old_document = document.document
    if request.method == "POST":
        document_form = DocumentForm(request.POST, request.FILES, instance=document)
        if document_form.is_valid():
            document = document_form.save(commit=False)
            # Si un nouveau document est téléchargé, supprimer l'ancien de manière sécurisée
            if old_document != document.document:
                secure_file_removal(old_document)
            document_form.save()
            logger.info("Document mis à jour avec succès")
            return redirect("bureau-communautaire:admin_documents_list")
        else:
            logger.warning(f"Formulaire de document invalide: {document_form.errors}")
            return render(
                request,
                "bureau_communautaire/admin_document_update.html",
                {"document_form": document_form},
            )
    else:
        document_form = DocumentForm(instance=document)
    return render(
        request,
        "bureau_communautaire/admin_document_update.html",
        {"document_form": document_form},
    )


@permission_required("bureau_communautaire.delete_document")
def delete_document(request, id):
    """Supprime un document de la base de données."""
    document = get_object_or_404(Document, id=id)
    if request.method == "POST":
        if document.document:
            document.document.delete(save=False)
        document.delete()
        return redirect("bureau-communautaire:admin_documents_list")
    return render(
        request,
        "bureau_communautaire/admin_document_delete.html",
        {"document": document},
    )


@permission_required("bureau_communautaire.view_elus")
def manage_page_status(request):
    """
    Gère le statut de la page bureau-communautaire.
    Permet d'activer/désactiver la page et de personnaliser le message de maintenance.
    """
    # Récupérer ou créer le statut de la page
    page_status, created = PageStatus.objects.get_or_create(
        page_name="bureau-communautaire",
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
            status_text = "activée" if page_status.is_active else "désactivée"
            logger.info(f"Page bureau-communautaire {status_text}")
            return redirect("bureau-communautaire:admin_page_status")

        elif action == "update_message":
            # Mettre à jour le message de maintenance
            new_message = request.POST.get("maintenance_message", "").strip()
            if new_message:
                page_status.maintenance_message = new_message
                page_status.save()
                logger.info("Message de maintenance mis à jour")
            return redirect("bureau-communautaire:admin_page_status")

    context = {
        "page_status": page_status,
        "is_active": page_status.is_active,
        "maintenance_message": page_status.maintenance_message,
    }
    return render(request, "bureau_communautaire/admin_page_status.html", context)
