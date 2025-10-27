import logging
import os

from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_list_or_404, get_object_or_404, redirect, render

from .forms import DocumentForm, ElusForm
from .models import Document, Elus

logger = logging.getLogger(__name__)


def elus(request):
    """Affiche la page publique des élus."""

    # Récupérer les élus avec le rôle
    if Elus.objects.filter(role="Vice-Président").exists():
        elus = get_list_or_404(Elus, role="Vice-Président")
    # Retourne un élu par défaut si aucun élu n'est trouvé
    # pour éviter une erreur 404
    else:
        elus = None
    if Elus.objects.filter(role="Président").exists():
        president = get_object_or_404(Elus, role="Président")
    else:
        president = None

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
    """Affiche la liste des élus."""
    if Elus.objects.exists():
        elus = Elus.objects.all()
    else:
        elus = []
    return render(request, "bureau_communautaire/admin_elus_list.html", {"elus": elus})


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
        request, "bureau_communautaire/admin_elu_update.html", {"elu_form": elu_form}
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
    """Affiche la liste des documents."""
    # Récupérer les documents
    if Document.objects.exists():
        documents = get_list_or_404(Document)
    else:
        documents = None

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
            # Si un nouveau document est téléchargé, supprimer l'ancien
            if old_document != document.document:
                if os.path.exists(old_document.path):
                    os.remove(old_document.path)
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
