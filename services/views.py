from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_list_or_404, get_object_or_404, redirect, render

from .forms import ServiceForm
from .models import Service


@permission_required("services.add_service")
def add_service(request):
    if request.method == "POST":
        service_form = ServiceForm(request.POST)
        if service_form.is_valid():
            service_form.save()
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
            service.save()
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
        service.delete()
        return redirect("services:admin_services_list")
    return render(request, "services/supprimer-service.html", {"service": service})


@permission_required("services.view_service")
def service_list(request):
    """View to list all services with management options."""
    if Service.objects.exists():
        services = get_list_or_404(Service.objects.order_by("title"))
    else:
        services = None
    return render(request, "services/service-list.html", {"services": services})
