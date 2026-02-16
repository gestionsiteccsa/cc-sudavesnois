from django.db import models


class BackupSettings(models.Model):
    """Paramètres de configuration pour les sauvegardes."""
    
    notification_email = models.EmailField(
        verbose_name="Email de notification",
        help_text="Email qui recevra les notifications de sauvegarde (succès et échec)",
        default="j.brechoire@gmail.com"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Paramètre de backup"
        verbose_name_plural = "Paramètres de backup"
    
    def __str__(self):
        return f"Settings - {self.notification_email}"
    
    @classmethod
    def get_settings(cls):
        """Retourne les paramètres (singleton pattern)."""
        settings, created = cls.objects.get_or_create(
            pk=1,
            defaults={'notification_email': 'j.brechoire@gmail.com'}
        )
        return settings
