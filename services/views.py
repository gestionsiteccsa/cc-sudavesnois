import json

from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import ServiceForm
from .models import Service


@permission_required("services.add_service")
def add_service(request):
    if request.method == "POST":
        service_form = ServiceForm(request.POST)
        if service_form.is_valid():
            service = service_form.save(commit=False)
            last = Service.objects.order_by("-order").first()
            service.order = (last.order + 1) if last else 0
            service.save()
            messages.success(request, f"Le service « {service.title} » a été ajouté.")
            return redirect("services:admin_services_list")
    else:
        service_form = ServiceForm()

    return render(
        request, "services/ajout-service.html", {"service_form": service_form}
    )


@permission_required("services.change_service")
def update_service(request, id):
    service = get_object_or_404(Service, id=id)
    if request.method == "POST":
        service_form = ServiceForm(request.POST, instance=service)
        if service_form.is_valid():
            service_form.save()
            messages.success(request, f"Le service « {service.title} » a été modifié.")
            return redirect("services:admin_services_list")
    else:
        service_form = ServiceForm(instance=service)

    return render(
        request, "services/modifier-service.html", {"service_form": service_form}
    )


@permission_required("services.delete_service")
def delete_service(request, id):
    service = get_object_or_404(Service, id=id)
    if request.method == "POST":
        title = service.title
        service.delete()
        messages.success(request, f"Le service « {title} » a été supprimé.")
        return redirect("services:admin_services_list")
    return render(request, "services/supprimer-service.html", {"service": service})


@permission_required("services.view_service")
def service_list(request):
    """View to list all services with management options."""
    services = Service.objects.all()
    total = services.count()
    with_desc = services.exclude(content="").count()
    context = {
        "services": services,
        "total": total,
        "with_desc": with_desc,
        "without_desc": total - with_desc,
    }
    return render(request, "services/service-list.html", context)


@permission_required("services.change_service")
@require_POST
def reorder_services(request):
    """AJAX endpoint to save the new order after drag & drop."""
    try:
        data = json.loads(request.body)
        ordered_ids = data.get("order", [])
        for idx, pk in enumerate(ordered_ids):
            Service.objects.filter(pk=pk).update(order=idx)
        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=400)
