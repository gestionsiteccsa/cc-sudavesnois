from django.db import models

from app.models import SingletonModel


class BackupSettings(SingletonModel):
    """Paramètres de configuration pour les sauvegardes."""

    notification_email = models.EmailField(
        verbose_name="Email de notification",
        help_text="Email qui recevra les notifications de sauvegarde (succès et échec)",
        default="j.brechoire@gmail.com",
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
        return cls.load()
