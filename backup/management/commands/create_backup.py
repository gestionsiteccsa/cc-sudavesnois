"""
Commande Django pour créer une sauvegarde automatique.
À exécuter via cron pour les sauvegardes automatiques hebdomadaires.
"""
from django.core.management.base import BaseCommand

from backup.models import BackupSettings
from backup.utils import cleanup_old_backups, create_backup_zip, send_backup_notification


class Command(BaseCommand):
    help = 'Crée une sauvegarde automatique (BDD + media) et envoie une notification email'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Démarrage de la sauvegarde automatique...'))
        
        try:
            # Créer le backup
            backup_path = create_backup_zip()
            self.stdout.write(self.style.SUCCESS(f'Backup créé : {backup_path}'))
            
            # Nettoyer les anciens backups (garder 4)
            deleted = cleanup_old_backups(retention_count=4)
            if deleted:
                self.stdout.write(self.style.NOTICE(f'Anciens backups supprimés : {", ".join(deleted)}'))
            
            # Envoyer notification
            settings = BackupSettings.get_settings()
            if settings.notification_email:
                send_backup_notification(
                    success=True,
                    email_to=settings.notification_email,
                    backup_name=backup_path.name
                )
                self.stdout.write(self.style.SUCCESS(f'Notification envoyée à {settings.notification_email}'))
            
            self.stdout.write(self.style.SUCCESS('Sauvegarde automatique terminée avec succès !'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erreur lors de la sauvegarde : {str(e)}'))
            
            # Envoyer notification d'échec
            try:
                settings = BackupSettings.get_settings()
                if settings.notification_email:
                    send_backup_notification(
                        success=False,
                        email_to=settings.notification_email,
                        error_message=str(e)
                    )
            except:
                pass
            
            raise
