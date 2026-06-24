from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from app.utils import secure_file_removal_by_path

from .forms import JournalForm
from .models import Journal


def journal(request):
    journals = Journal.objects.all().order_by("-number")
    paginator = Paginator(journals, 3)
    page = request.GET.get("page")

    try:
        journals = paginator.page(page)
    except PageNotAnInteger:
        journals = paginator.page(1)
    except EmptyPage:
        journals = paginator.page(paginator.num_pages)
    context = {"journals": journals}
    return render(request, "journal/journal.html", context)


def journal_detail(request, id):
    journal_obj = get_object_or_404(Journal, id=id)
    if not journal_obj.get_document_size():
        messages.error(request, "Le document PDF de ce journal est indisponible.")
        return redirect("journal:journal")
    context = {
        "journal": journal_obj,
        "pdf_url": journal_obj.document.url,
    }
    return render(request, "journal/viewer.html", context)


@permission_required("journal.view_journal")
def list_journals(request):
    """Vue de la liste des journaux pour l'administrateur"""
    journaux = Journal.objects.all().order_by("-number")
    pdf_count = sum(1 for j in journaux if j.document)
    cover_count = sum(1 for j in journaux if j.cover)
    return render(
        request,
        "journal/list_journals.html",
        {
            "journaux": journaux,
            "pdf_count": pdf_count,
            "cover_count": cover_count,
        },
    )


@permission_required("journal.add_journal")
def add_journal(request):
    """Vue d'ajout de journal pour l'administrateur"""
    if request.method == "POST":
        journal_form = JournalForm(request.POST, request.FILES)
        if journal_form.is_valid():
            journal_form.save()
            messages.success(request, "Le journal a été ajouté avec succès.")
            return redirect("journal:admin_journaux_list")
        else:
            messages.error(request, "Merci de corriger les erreurs dans le formulaire.")
    else:
        journal_form = JournalForm()

    return render(request, "journal/add_journal.html", {"form": journal_form})


@permission_required("journal.delete_journal")
@transaction.atomic
def delete_journal(request, id):
    """Vue de suppression de journal pour l'administrateur"""
    journal = get_object_or_404(Journal, id=id)
    if request.method == "POST":
        if request.POST.get("confirm") == "yes":
            # Snapshot des chemins avant suppression
            doc_path = journal.document.path if journal.document else None
            cover_path = journal.cover.path if journal.cover else None
            journal.delete()
            # Suppression effective des fichiers après commit
            if doc_path:
                transaction.on_commit(lambda p=doc_path: secure_file_removal_by_path(p))
            if cover_path:
                transaction.on_commit(
                    lambda p=cover_path: secure_file_removal_by_path(p)
                )
            messages.success(request, "Le journal a été supprimé avec succès.")
            return redirect("journal:admin_journaux_list")
        else:
            messages.error(request, "La suppression a été annulée.")
            return redirect("journal:admin_journaux_list")
    else:
        return render(request, "journal/delete_journal.html", {"journal": journal})


@permission_required("journal.change_journal")
@transaction.atomic
def edit_journal(request, id):
    """Vue d'édition de journal pour l'administrateur"""
    journal = get_object_or_404(Journal, id=id)

    # On garde documents actuels en mémoire
    # pour les supprimer si ils sont remplacés
    last_document = journal.document
    last_cover = journal.cover

    if request.method == "POST":
        journal_form = JournalForm(request.POST, request.FILES, instance=journal)

        if journal_form.is_valid():
            journal = journal_form.save(commit=False)
            # Vérifier si les fichiers ont changé ; suppression après commit
            indisponible = False
            indisponible_files = []
            if (
                journal.document != last_document
                and last_document
                and hasattr(last_document, "path")
            ):
                doc_path = last_document.path
                transaction.on_commit(lambda p=doc_path: secure_file_removal_by_path(p))
            if (
                journal.cover != last_cover
                and last_cover
                and hasattr(last_cover, "path")
            ):
                cover_path = last_cover.path
                transaction.on_commit(
                    lambda p=cover_path: secure_file_removal_by_path(p)
                )
            journal.save()
            messages.success(request, "Le journal a été modifié avec succès.")
            return redirect("journal:admin_journaux_list")
        else:
            messages.error(request, "Merci de corriger les erreurs dans le formulaire.")
    else:
        journal_form = JournalForm(instance=journal)

    return render(
        request,
        "journal/edit_journal.html",
        {
            "form": journal_form,
            "journal": journal,
        },
    )
