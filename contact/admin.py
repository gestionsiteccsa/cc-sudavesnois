from django.contrib import admin

from .models import ContactEmail


class CustomContactAdmin(admin.ModelAdmin):
    """
    Administration personnalisée pour les mails de contact
    """

    # form = ElusForm
    model = ContactEmail
    list_display = ("email", "is_active")
    list_filter = ("email", "is_active")
    search_fields = ("email", "is_active")
    ordering = ("email",)
    list_editable = ("is_active",)


admin.site.register(ContactEmail, CustomContactAdmin)
