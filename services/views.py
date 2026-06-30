import json
import logging

from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.db import transaction
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST

from .forms import ServiceForm
from .models import Service

logger = logging.getLogger(__name__)

REORDER_MAX_ITEMS = 1000


@permission_required("services.add_service")
def add_service(request):
    """Vue d'ajout d'un service avec calcul atomique de l'ordre."""
    if request.method == "POST":
        service_form = ServiceForm(request.POST)
        if service_form.is_valid():
            with transaction.atomic():
                service = service_form.save(commit=False)
                last = Service.objects.select_for_update().order_by("-order").first()
                service.order = (last.order + 1) if last else 0
                service.save()
            messages.success(
                request,
                _("Le service « %(title)s » a été ajouté.") % {"title": service.title},
            )
            return redirect("services:admin_services_list")
    else:
        service_form = ServiceForm()

    return render(
        request, "services/ajout-service.html", {"service_form": service_form}
    )


@permission_required("services.change_service")
def update_service(request, id):
    """Vue de modification d'un service."""
    service = get_object_or_404(Service, id=id)
    if request.method == "POST":
        service_form = ServiceForm(request.POST, instance=service)
        if service_form.is_valid():
            service_form.save()
            messages.success(
                request,
                _("Le service « %(title)s » a été modifié.")
                % {"title": service_form.instance.title},
            )
            return redirect("services:admin_services_list")
    else:
        service_form = ServiceForm(instance=service)

    return render(
        request,
        "services/modifier-service.html",
        {"service_form": service_form, "service": service},
    )


@permission_required("services.delete_service")
@require_POST
def delete_service(request, id):
    """Suppression d'un service (POST uniquement, appelé par le modal)."""
    service = get_object_or_404(Service, id=id)
    title = service.title
    service.delete()
    messages.success(
        request,
        _("Le service « %(title)s » a été supprimé.") % {"title": title},
    )
    return redirect("services:admin_services_list")


@permission_required("services.view_service")
def service_list(request):
    """Vue de liste des services avec stats en 1 aggregate."""
    stats = Service.objects.aggregate(
        total=Count("id"),
        with_desc=Count("id", filter=~Q(content="")),
    )
    total = stats["total"]
    with_desc = stats["with_desc"]
    return render(
        request,
        "services/service-list.html",
        {
            "services": Service.objects.all(),
            "total": total,
            "with_desc": with_desc,
            "without_desc": total - with_desc,
        },
    )


@permission_required("services.change_service")
@require_POST
def reorder_services(request):
    """
    Endpoint AJAX pour sauvegarder le nouvel ordre après drag & drop.

    Valide strictement le payload (liste non-vide d'IDs positifs existants,
    taille bornée) et applique l'ordre en 1 SELECT + 1 UPDATE groupé
    via ``bulk_update``.

    Les erreurs internes sont journalisées et un message générique est
    retourné (jamais ``str(exception)``).
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)

    ordered_ids = data.get("order", [])
    if not isinstance(ordered_ids, list) or not ordered_ids:
        return JsonResponse({"success": False, "error": "Invalid payload"}, status=400)
    if len(ordered_ids) > REORDER_MAX_ITEMS:
        return JsonResponse({"success": False, "error": "Invalid payload"}, status=400)

    for pk in ordered_ids:
        if not isinstance(pk, int) or pk <= 0:
            return JsonResponse({"success": False, "error": "Invalid ID"}, status=400)

    services_by_pk = {s.pk: s for s in Service.objects.filter(pk__in=ordered_ids)}
    if len(services_by_pk) != len(ordered_ids):
        return JsonResponse({"success": False, "error": "Invalid ID"}, status=400)

    for idx, pk in enumerate(ordered_ids):
        services_by_pk[pk].order = idx

    try:
        Service.objects.bulk_update(services_by_pk.values(), ["order"])
    except Exception:
        logger.exception("reorder_services: bulk_update failed")
        return JsonResponse({"success": False, "error": "Internal error"}, status=500)
    return JsonResponse({"success": True})
