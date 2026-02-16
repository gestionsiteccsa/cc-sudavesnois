from django.contrib import admin

from .models import BackupSettings


@admin.register(BackupSettings)
class BackupSettingsAdmin(admin.ModelAdmin):
    list_display = ['notification_email', 'updated_at']
    readonly_fields = ['created_at', 'updated_at']
