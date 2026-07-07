from django.contrib import admin

from .models import PLUISettings


@admin.register(PLUISettings)
class PLUISettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            "Visibilité des sections",
            {
                "fields": ("modification_simplifiee_1_visible",),
            },
        ),
    )

    def has_add_permission(self, request):
        return not PLUISettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
