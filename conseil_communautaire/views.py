import json
from collections import defaultdict
from datetime import timedelta

from django.contrib.auth.decorators import permission_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_list_or_404, get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from app.utils import secure_file_removal
from comptes_rendus.models import Conseil

from .forms import ConseilMembreForm, ConseilVilleForm
from .models import ConseilMembre, ConseilVille


def conseil(request):
    # Récupérer les villes (évaluation paresseuse)
    cities_list = ConseilVille.objects.all().order_by("city_name")
    city_number = cities_list.count()

    # Pré-grouper les membres par ville pour éviter O(n×m) dans le template
    members_by_city = defaultdict(lambda: {"titulaires": [], "suppleants": []})
    for member in ConseilMembre.objects.select_related("city"):
        key = "suppleants" if member.is_suppleant else "titulaires"
        members_by_city[member.city_id][key].append(member)

    # Afficher les conseils depuis 2 jours avant aujourd'hui
    today = timezone.now().date()
    two_days_ago = today - timedelta(days=2)
    conseils = list(Conseil.objects.filter(date__gte=two_days_ago).order_by("date"))

    # Déterminer le prochain conseil à venir depuis la liste déjà chargée
    next_conseil = next((c for c in conseils if c.date >= today), None)

    context = {
        "cities_list": cities_list,
        "members_by_city": dict(members_by_city),
        "city_number": city_number,
        "conseils": conseils if conseils else None,
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
    Optimisé avec prefetch des commissions et groupement des membres.
    """
    cities_list = list(ConseilVille.objects.all().order_by("city_name"))
    cities_list = cities_list if cities_list else None

    members_qs = (
        ConseilMembre.objects.select_related("city")
        .prefetch_related("linked_commission")
        .all()
        .order_by("last_name", "first_name")
    )

    members_list = list(members_qs)

    member_counts = {}
    for m in members_list:
        member_counts[m.city_id] = member_counts.get(m.city_id, 0) + 1

    total_cities = len(cities_list) if cities_list else 0
    total_members = len(members_list)
    total_population = sum(c.nb_habitants for c in cities_list) if cities_list else 0

    context = {
        "cities_list": cities_list,
        "members_list": members_list,
        "member_counts": member_counts,
        "total_cities": total_cities,
        "total_members": total_members,
        "total_population": total_population,
    }
    return render(request, "conseil_communautaire/admin_cities_list.html", context)


@permission_required("conseil_communautaire.delete_conseilville")
@transaction.atomic
def delete_city(request, city_id):
    city = get_object_or_404(ConseilVille, id=city_id)
    if request.method == "POST":
        image = city.image
        city.delete()
        if image:
            transaction.on_commit(lambda img=image: secure_file_removal(img))
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
@transaction.atomic
def edit_member(request, id):
    member = get_object_or_404(ConseilMembre, id=id)

    if request.method == "POST":
        member_form = ConseilMembreForm(request.POST, request.FILES, instance=member)

        if member_form.is_valid():
            if member_form.cleaned_data.get("clear_photo") and member.photo:
                photo_to_remove = member.photo
                member.photo = None
                transaction.on_commit(lambda p=photo_to_remove: secure_file_removal(p))
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
@transaction.atomic
def delete_member(request, id):
    member = get_object_or_404(ConseilMembre, id=id)
    if request.method == "POST":
        photo = member.photo
        member.delete()
        if photo:
            transaction.on_commit(lambda p=photo: secure_file_removal(p))
        return redirect("conseil_communautaire:admin_membres_list")
    return render(
        request, "conseil_communautaire/admin_member_delete.html", {"member": member}
    )


@permission_required("conseil_communautaire.change_conseilmembre")
@csrf_exempt
@require_http_methods(["POST"])
def update_photo_position(request, id):
    """
    API endpoint pour mettre à jour la position et le zoom de la photo d'un membre.
    Accepte un JSON avec photo_position_x, photo_position_y et photo_zoom.
    """
    member = get_object_or_404(ConseilMembre, id=id)

    try:
        data = json.loads(request.body)
        position_x = data.get("photo_position_x")
        position_y = data.get("photo_position_y")
        zoom = data.get("photo_zoom")

        if position_x is not None:
            position_x = max(0, min(100, int(position_x)))
            member.photo_position_x = position_x

        if position_y is not None:
            position_y = max(0, min(100, int(position_y)))
            member.photo_position_y = position_y

        if zoom is not None:
            zoom = max(50, min(200, int(zoom)))
            member.photo_zoom = zoom

        member.save(
            update_fields=["photo_position_x", "photo_position_y", "photo_zoom"]
        )

        return JsonResponse(
            {
                "success": True,
                "photo_position_x": member.photo_position_x,
                "photo_position_y": member.photo_position_y,
                "photo_zoom": member.photo_zoom,
            }
        )
    except (ValueError, TypeError) as e:
        return JsonResponse(
            {"success": False, "error": f"Valeur invalide: {str(e)}"}, status=400
        )
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "JSON invalide"}, status=400)


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
