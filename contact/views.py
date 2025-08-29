from django.shortcuts import get_list_or_404, get_object_or_404, redirect, render

from .forms import ContactEmailForm
from .models import ContactEmail


def list_contact_emails(request):
    """View to list all contact emails."""
    if ContactEmail.objects.exists():
        contact_emails = get_list_or_404(ContactEmail.objects.order_by("-is_active"))
    else:
        contact_emails = None
    return render(
        request, "contact/list_contacts.html", {"contact_emails": contact_emails}
    )


def edit_contact_email(request, id):
    """View to edit a contact email."""
    if ContactEmail.objects.filter(id=id).exists():
        contact_email = get_object_or_404(ContactEmail, id=id)
    else:
        return redirect("contact:list_contacts")

    if request.method == "POST":
        form = ContactEmailForm(request.POST, instance=contact_email)
        if form.is_valid():
            form.save()
            return redirect("contact:list_contacts")
    else:
        form = ContactEmailForm(instance=contact_email)

    return render(request, "contact/edit_contact.html", {"form": form})


def delete_contact_email(request, id):
    """View to delete a contact email."""
    if ContactEmail.objects.filter(id=id).exists():
        contact_email = get_object_or_404(ContactEmail, id=id)
    else:
        return redirect("contact:list_contacts")

    if request.method == "POST":
        contact_email.delete()
        return redirect("contact:list_contacts")

    return render(
        request, "contact/delete_contact.html", {"contact_email": contact_email}
    )


def add_contact_email(request):
    """View to add a new contact email."""
    if request.method == "POST":
        form = ContactEmailForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("contact:list_contacts")
    else:
        form = ContactEmailForm()

    return render(request, "contact/add_contact.html", {"form": form})
