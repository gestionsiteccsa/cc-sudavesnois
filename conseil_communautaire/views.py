from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_list_or_404, get_object_or_404, redirect, render

from .forms import ConseilMembreForm, ConseilVilleForm
from .models import ConseilMembre, ConseilVille


def conseil(request):
    cities_list = ConseilVille.objects.all().order_by("city_name")
    members_list = ConseilMembre.objects.all()
    city_number = cities_list.count()
    context = {
        "cities_list": cities_list,
        "members_list": members_list,
        "city_number": city_number,
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
    if ConseilVille.objects.exists():
        cities_list = get_list_or_404(ConseilVille)
    else:
        cities_list = None
    if ConseilMembre.objects.exists():
        members_list = get_list_or_404(ConseilMembre)
    else:
        members_list = None
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
        member_form = ConseilMembreForm(request.POST)

        if member_form.is_valid():
            member_form.save()
            return redirect("conseil_communautaire:admin_list_cities")
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
        member_form = ConseilMembreForm(request.POST, instance=member)

        if member_form.is_valid():
            member_form.save()
            return redirect("conseil_communautaire:admin_list_cities")

    else:
        member_form = ConseilMembreForm(instance=member)

    return render(
        request, "conseil_communautaire/admin_member_edit.html", {"member": member_form}
    )


@permission_required("conseil_communautaire.delete_conseilmembre")
def delete_member(request, id):
    member = get_object_or_404(ConseilMembre, id=id)
    if request.method == "POST":
        member.delete()
        return redirect("conseil_communautaire:admin_list_cities")
    return render(
        request, "conseil_communautaire/admin_member_delete.html", {"member": member}
    )


@permission_required("conseil_communautaire.view_conseilmembre")
def admin_list_members(request):
    members_list = (
        ConseilMembre.objects.select_related("city")
        .all()
        .order_by("last_name", "first_name")
    )
    context = {"members_list": members_list}
    return render(request, "conseil_communautaire/admin_members_list.html", context)
