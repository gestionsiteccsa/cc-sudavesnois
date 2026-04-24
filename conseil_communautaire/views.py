from datetime import timedelta

from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_list_or_404, get_object_or_404, redirect, render
from django.utils import timezone

from app.utils import secure_file_removal
from comptes_rendus.models import Conseil
from .forms import ConseilMembreForm, ConseilVilleForm
from .models import ConseilMembre, ConseilVille


def conseil(request):
    # Optimisé avec select_related pour éviter les N+1 queries
    cities_list = list(ConseilVille.objects.all().order_by("city_name"))
    members_list = list(ConseilMembre.objects.select_related('city'))
    city_number = len(cities_list)

    # Afficher les conseils depuis 2 jours avant aujourd'hui (conservés 2 jours après)
    today = timezone.now().date()
    two_days_ago = today - timedelta(days=2)
    conseils = Conseil.objects.filter(date__gte=two_days_ago).order_by("date")
    if not conseils.exists():
        conseils = None

    # Déterminer le prochain conseil à venir (date >= aujourd'hui)
    next_conseil = Conseil.objects.filter(date__gte=today).order_by("date").first()

    context = {
        "cities_list": cities_list,
        "members_list": members_list,
        "city_number": city_number,
        "conseils": conseils,
        "next_conseil": next_conseil,
    }

    return render(request, "conseil_communautaire/conseil.html", context)


# Partie ville
@permission_required("conseil_communautaire.add_conseilville")
def add_city(request):
    if request.method == "POST":
        city_form = ConseilVilleForm(request.POST, request.FILES)

        if city_form.is_valid():
            city_form.save()
            return redirect("conseil_communautaire:admin_list_cities")
    else:
        city_form = ConseilVilleForm()

    return render(
        request, "conseil_communautaire/admin_city_add.html", {"city_form": city_form}
    )


@permission_required("conseil_communautaire.view_conseilville")
def list_cities(request):
    """
    Affiche la liste des villes.
    Optimisé pour éviter le double pattern .exists() + requête.
    """
    cities_list = list(ConseilVille.objects.all())
    cities_list = cities_list if cities_list else None
    
    members_list = list(ConseilMembre.objects.all())
    members_list = members_list if members_list else None
    
    context = {"cities_list": cities_list, "members_list": members_list}
    return render(request, "conseil_communautaire/admin_cities_list.html", context)


@permission_required("conseil_communautaire.delete_conseilville")
def delete_city(request, city_id):
    city = get_object_or_404(ConseilVille, id=city_id)
    if request.method == "POST":
        if city.image:
            city.image.delete(save=False)  # Supprimer l'image du modèle
        city.delete()
        return redirect("conseil_communautaire:admin_list_cities")
    return render(
        request, "conseil_communautaire/admin_city_delete.html", {"city": city}
    )


@permission_required("conseil_communautaire.change_conseilville")
def edit_city(request, city_id):
    city = get_object_or_404(ConseilVille, id=city_id)

    if request.method == "POST":
        city_form = ConseilVilleForm(request.POST, request.FILES, instance=city)

        if city_form.is_valid():
            city.save()
            return redirect("conseil_communautaire:admin_list_cities")

    else:
        city_form = ConseilVilleForm(instance=city)

    return render(
        request, "conseil_communautaire/admin_city_edit.html", {"city": city_form}
    )


# Partie membre
@permission_required("conseil_communautaire.add_conseilmembre")
def add_member(request):
    if request.method == "POST":
        member_form = ConseilMembreForm(request.POST, request.FILES)

        if member_form.is_valid():
            member_form.save()
            return redirect("conseil_communautaire:admin_membres_list")
    else:
        member_form = ConseilMembreForm()

    return render(
        request,
        "conseil_communautaire/admin_member_add.html",
        {"member_form": member_form},
    )


@permission_required("conseil_communautaire.change_conseilmembre")
def edit_member(request, id):
    member = get_object_or_404(ConseilMembre, id=id)

    if request.method == "POST":
        member_form = ConseilMembreForm(request.POST, request.FILES, instance=member)

        if member_form.is_valid():
            if member_form.cleaned_data.get("clear_photo") and member.photo:
                secure_file_removal(member.photo)
                member.photo = None
            member_form.save()
            return redirect("conseil_communautaire:admin_membres_list")

    else:
        member_form = ConseilMembreForm(instance=member)

    return render(
        request,
        "conseil_communautaire/admin_member_edit.html",
        {"member_form": member_form, "member_obj": member},
    )


@permission_required("conseil_communautaire.delete_conseilmembre")
def delete_member(request, id):
    member = get_object_or_404(ConseilMembre, id=id)
    if request.method == "POST":
        if member.photo:
            secure_file_removal(member.photo)
        member.delete()
        return redirect("conseil_communautaire:admin_membres_list")
    return render(
        request, "conseil_communautaire/admin_member_delete.html", {"member": member}
    )


@permission_required("conseil_communautaire.view_conseilmembre")
def admin_list_members(request):
    members_list = (
        ConseilMembre.objects.select_related("city")
        .prefetch_related("linked_commission")
        .all()
        .order_by("last_name", "first_name")
    )

    total = members_list.count()
    titulaires = members_list.filter(is_suppleant=False).count()
    suppleants = members_list.filter(is_suppleant=True).count()
    cities = ConseilVille.objects.all().order_by("city_name")

    context = {
        "members_list": members_list,
        "stats": {
            "total": total,
            "titulaires": titulaires,
            "suppleants": suppleants,
        },
        "cities": cities,
    }
    return render(request, "conseil_communautaire/admin_members_list.html", context)
