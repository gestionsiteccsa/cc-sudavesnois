import unicodedata
from collections import defaultdict

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CategoriePartenaireForm, PartenaireForm
from .models import CategoriePartenaire, Partenaire


def remove_accents(input_str):
    """Supprime les accents d'une chaîne de caractères pour le tri alphabétique."""
    if not input_str:
        return ""
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])


# ==================== VUES PUBLIQUES ====================

def partenaires(request):
    """Vue publique affichant tous les partenaires actifs groupés par catégorie"""
    all_partenaires = list(Partenaire.objects.filter(active=True).select_related('categorie'))

    # Grouper en Python pour eviter N+1 requetes
    by_cat = defaultdict(list)
    for p in all_partenaires:
        by_cat[p.categorie_id].append(p)

    # Partenaires par categorie normale
    categories_normales = CategoriePartenaire.objects.filter(
        active=True,
        type_section='normal',
        partenaire__active=True
    ).distinct().order_by('ordre', 'nom')

    partenaires_par_categorie = {}
    for cat in categories_normales:
        lst = by_cat.get(cat.id, [])
        lst.sort(key=lambda p: remove_accents(p.nom).lower())
        partenaires_par_categorie[cat] = lst

    # Partenaires par categorie subvention
    categories_subventions = CategoriePartenaire.objects.filter(
        active=True,
        type_section='subvention',
        partenaire__active=True
    ).distinct().order_by('ordre', 'nom')

    partenaires_subventions = {}
    for cat in categories_subventions:
        lst = by_cat.get(cat.id, [])
        lst.sort(key=lambda p: remove_accents(p.nom).lower())
        partenaires_subventions[cat] = lst

    # Partenaires sans categorie
    partenaires_sans_categorie = sorted(
        by_cat.get(None, []),
        key=lambda p: remove_accents(p.nom).lower()
    )

    context = {
        "partenaires_par_categorie": partenaires_par_categorie,
        "partenaires_subventions": partenaires_subventions,
        "partenaires_sans_categorie": partenaires_sans_categorie,
    }

    return render(request, "partenaires/partenaires.html", context)


# ==================== VUES ADMIN - CATÉGORIES ====================

@login_required
def list_categories(request):
    """Liste des catégories de partenaires"""
    categories = CategoriePartenaire.objects.all().order_by('ordre', 'nom')
    total = categories.count()
    actives = categories.filter(active=True).count()
    inactives = total - actives

    return render(request, "partenaires/list_categories.html", {
        "categories": categories,
        "total": total,
        "actives": actives,
        "inactives": inactives,
    })


@login_required
def add_categorie(request):
    """Ajouter une catégorie de partenaire"""
    if request.method == "POST":
        form = CategoriePartenaireForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "La catégorie a été ajoutée avec succès.")
            return redirect("partenaires:admin_categories_list")
        else:
            messages.error(request, "Merci de corriger les erreurs dans le formulaire.")
    else:
        form = CategoriePartenaireForm()

    return render(request, "partenaires/add_categorie.html", {"form": form})


@login_required
def edit_categorie(request, id):
    """Modifier une catégorie de partenaire"""
    categorie = get_object_or_404(CategoriePartenaire, id=id)

    if request.method == "POST":
        form = CategoriePartenaireForm(request.POST, instance=categorie)
        if form.is_valid():
            form.save()
            messages.success(request, "La catégorie a été modifiée avec succès.")
            return redirect("partenaires:admin_categories_list")
        else:
            messages.error(request, "Merci de corriger les erreurs dans le formulaire.")
    else:
        form = CategoriePartenaireForm(instance=categorie)

    return render(request, "partenaires/edit_categorie.html", {
        "form": form,
        "categorie": categorie
    })


@login_required
def delete_categorie(request, id):
    """Supprimer une catégorie de partenaire"""
    categorie = get_object_or_404(CategoriePartenaire, id=id)

    if request.method == "POST":
        if request.POST.get("confirm") == "yes":
            # Vérifier si des partenaires utilisent cette catégorie
            partenaires_count = Partenaire.objects.filter(categorie=categorie).count()
            if partenaires_count > 0:
                messages.error(
                    request,
                    f"Impossible de supprimer cette catégorie : elle est utilisée par {partenaires_count} partenaire(s)."
                )
            else:
                categorie.delete()
                messages.success(request, "La catégorie a été supprimée avec succès.")
            return redirect("partenaires:admin_categories_list")

    return render(request, "partenaires/delete_categorie.html", {"categorie": categorie})


# ==================== VUES ADMIN - PARTENAIRES ====================

@login_required
def list_partenaires(request):
    """Liste des partenaires"""
    partenaires_list = Partenaire.objects.all().select_related('categorie').order_by(
        'categorie__ordre', 'ordre', 'nom'
    )
    total = partenaires_list.count()
    actifs = partenaires_list.filter(active=True).count()
    inactifs = total - actifs

    return render(request, "partenaires/list_partenaires.html", {
        "partenaires": partenaires_list,
        "total": total,
        "actifs": actifs,
        "inactifs": inactifs,
    })


@login_required
def add_partenaire(request):
    """Ajouter un partenaire"""
    if request.method == "POST":
        form = PartenaireForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Le partenaire a été ajouté avec succès.")
            return redirect("partenaires:admin_partenaires_list")
        else:
            messages.error(request, "Merci de corriger les erreurs dans le formulaire.")
    else:
        form = PartenaireForm()

    return render(request, "partenaires/add_partenaire.html", {"form": form})


@login_required
def edit_partenaire(request, id):
    """Modifier un partenaire"""
    partenaire = get_object_or_404(Partenaire, id=id)

    if request.method == "POST":
        form = PartenaireForm(request.POST, request.FILES, instance=partenaire)
        if form.is_valid():
            form.save()
            messages.success(request, "Le partenaire a été modifié avec succès.")
            return redirect("partenaires:admin_partenaires_list")
        else:
            messages.error(request, "Merci de corriger les erreurs dans le formulaire.")
    else:
        form = PartenaireForm(instance=partenaire)

    return render(request, "partenaires/edit_partenaire.html", {
        "form": form,
        "partenaire": partenaire
    })


@login_required
def delete_partenaire(request, id):
    """Supprimer un partenaire"""
    partenaire = get_object_or_404(Partenaire, id=id)

    if request.method == "POST":
        if request.POST.get("confirm") == "yes":
            partenaire.delete()
            messages.success(request, "Le partenaire a été supprimé avec succès.")
            return redirect("partenaires:admin_partenaires_list")

    return render(request, "partenaires/delete_partenaire.html", {"partenaire": partenaire})
