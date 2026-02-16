import os
import tempfile
import zipfile
from datetime import datetime, timedelta
from io import BytesIO
from pathlib import Path
from unittest.mock import Mock, patch

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import mail
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from backup.forms import BackupSettingsForm
from backup.models import BackupSettings
from backup.utils import (
    cleanup_old_backups,
    create_backup_zip,
    format_size,
    get_backup_dir,
    get_stored_backups,
    send_backup_notification,
)

User = get_user_model()


class BackupSettingsModelTests(TestCase):
    """Tests pour le modèle BackupSettings."""

    def test_get_settings_creates_default(self):
        """Test que get_settings crée les paramètres par défaut."""
        settings_obj = BackupSettings.get_settings()
        self.assertEqual(settings_obj.notification_email, "j.brechoire@gmail.com")
        self.assertEqual(settings_obj.pk, 1)

    def test_get_settings_returns_existing(self):
        """Test que get_settings retourne les paramètres existants."""
        BackupSettings.objects.create(
            pk=1,
            notification_email="test@example.com"
        )
        settings_obj = BackupSettings.get_settings()
        self.assertEqual(settings_obj.notification_email, "test@example.com")

    def test_str_method(self):
        """Test la représentation string du modèle."""
        settings_obj = BackupSettings.get_settings()
        self.assertEqual(str(settings_obj), "Settings - j.brechoire@gmail.com")


class BackupUtilsTests(TestCase):
    """Tests pour les fonctions utilitaires."""

    def setUp(self):
        """Créer un dossier temporaire pour les tests."""
        self.temp_dir = tempfile.mkdtemp()
        self.addCleanup(lambda: os.rmdir(self.temp_dir) if os.path.exists(self.temp_dir) else None)

    @override_settings(BACKUP_ROOT="/tmp/test_backup")
    def test_get_backup_dir(self):
        """Test que get_backup_dir retourne le bon chemin."""
        backup_dir = get_backup_dir()
        self.assertEqual(str(backup_dir), "/tmp/test_backup")

    @override_settings(BACKUP_ROOT="/tmp/test_backup")
    def test_create_backup_zip_creates_file(self):
        """Test que create_backup_zip crée bien un fichier ZIP."""
        with tempfile.TemporaryDirectory() as temp_dir:
            backup_path = Path(temp_dir) / "test_backup.zip"
            result = create_backup_zip(backup_path)
            
            self.assertTrue(result.exists())
            self.assertTrue(zipfile.is_zipfile(result))

    def test_format_size(self):
        """Test le formatage des tailles."""
        self.assertEqual(format_size(512), "512.0 B")
        self.assertEqual(format_size(1024), "1.0 KB")
        self.assertEqual(format_size(1024 * 1024), "1.0 MB")
        self.assertEqual(format_size(1024 * 1024 * 1024), "1.0 GB")

    @override_settings(BACKUP_ROOT=None)
    def test_get_stored_backups_empty_dir(self):
        """Test get_stored_backups avec un dossier vide."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with override_settings(BACKUP_ROOT=temp_dir):
                backups = get_stored_backups()
                self.assertEqual(backups, [])

    @override_settings(BACKUP_ROOT=None)
    def test_get_stored_backups_with_files(self):
        """Test get_stored_backups avec des fichiers existants."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Créer des fichiers backup factices
            backup_file = Path(temp_dir) / "backup_20240115_143000.zip"
            backup_file.write_bytes(b"fake content")
            
            with override_settings(BACKUP_ROOT=temp_dir):
                backups = get_stored_backups()
                self.assertEqual(len(backups), 1)
                self.assertEqual(backups[0]["name"], "backup_20240115_143000.zip")
                self.assertEqual(backups[0]["size_human"], "12.0 B")


class CleanupOldBackupsTests(TestCase):
    """Tests pour la fonction cleanup_old_backups."""

    @override_settings(BACKUP_ROOT=None)
    def test_cleanup_keeps_recent_backups(self):
        """Test que cleanup garde les 4 backups les plus récents."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Créer 6 fichiers backup avec des dates différentes
            for i in range(6):
                backup_file = Path(temp_dir) / f"backup_202401{i+1:02d}_120000.zip"
                backup_file.write_bytes(b"content")
                # Modifier la date de modification
                past_time = datetime.now().timestamp() - (i * 86400)
                os.utime(backup_file, (past_time, past_time))

            with override_settings(BACKUP_ROOT=temp_dir):
                deleted = cleanup_old_backups(retention_count=4)
                
                # Vérifier que 2 fichiers ont été supprimés
                self.assertEqual(len(deleted), 2)
                
                # Vérifier que 4 fichiers restent
                remaining = list(Path(temp_dir).glob("backup_*.zip"))
                self.assertEqual(len(remaining), 4)


class SendBackupNotificationTests(TestCase):
    """Tests pour l'envoi de notifications par email."""

    def test_send_success_notification(self):
        """Test l'envoi d'une notification de succès."""
        send_backup_notification(
            success=True,
            email_to="test@example.com",
            backup_name="backup_test.zip"
        )
        
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "[CCSA] Sauvegarde automatique réussie")
        self.assertIn("test@example.com", mail.outbox[0].to)
        self.assertIn("backup_test.zip", mail.outbox[0].body)

    def test_send_failure_notification(self):
        """Test l'envoi d'une notification d'échec."""
        send_backup_notification(
            success=False,
            email_to="test@example.com",
            error_message="Erreur de test"
        )
        
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "[CCSA] ÉCHEC de la sauvegarde automatique")
        self.assertIn("test@example.com", mail.outbox[0].to)
        self.assertIn("Erreur de test", mail.outbox[0].body)

    def test_no_email_if_empty(self):
        """Test qu'aucun email n'est envoyé si l'adresse est vide."""
        send_backup_notification(
            success=True,
            email_to="",
            backup_name="backup_test.zip"
        )
        
        self.assertEqual(len(mail.outbox), 0)


class BackupSettingsFormTests(TestCase):
    """Tests pour le formulaire BackupSettingsForm."""

    def test_form_valid(self):
        """Test que le formulaire est valide avec un email correct."""
        form_data = {"notification_email": "test@example.com"}
        form = BackupSettingsForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_invalid_email(self):
        """Test que le formulaire est invalide avec un email incorrect."""
        form_data = {"notification_email": "not-an-email"}
        form = BackupSettingsForm(data=form_data)
        self.assertFalse(form.is_valid())


class BackupViewsTests(TestCase):
    """Tests pour les vues de l'app backup."""

    def setUp(self):
        """Créer un utilisateur staff pour les tests."""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            is_staff=True
        )
        self.client = Client()
        self.client.login(username="testuser", password="testpass123")

    def test_list_backups_view_get(self):
        """Test que la vue list_backups fonctionne en GET."""
        response = self.client.get(reverse("backup:list_backups"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "backup/list_backups.html")

    def test_list_backups_view_post_update_settings(self):
        """Test la mise à jour des paramètres via POST."""
        BackupSettings.get_settings()  # Créer les settings par défaut
        
        response = self.client.post(
            reverse("backup:list_backups"),
            {"update_settings": "1", "notification_email": "new@example.com"}
        )
        
        self.assertEqual(response.status_code, 302)
        settings_obj = BackupSettings.get_settings()
        self.assertEqual(settings_obj.notification_email, "new@example.com")

    def test_create_backup_store_view(self):
        """Test la création d'un backup stocké."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with override_settings(BACKUP_ROOT=temp_dir):
                response = self.client.get(reverse("backup:create_backup_store"))
                
                self.assertEqual(response.status_code, 302)
                
                # Vérifier qu'un fichier backup a été créé
                backups = list(Path(temp_dir).glob("backup_*.zip"))
                self.assertEqual(len(backups), 1)

    def test_download_backup_view(self):
        """Test le téléchargement d'un backup existant."""
        with tempfile.TemporaryDirectory() as temp_dir:
            backup_file = Path(temp_dir) / "backup_test.zip"
            backup_file.write_bytes(b"fake zip content")
            
            with override_settings(BACKUP_ROOT=temp_dir):
                response = self.client.get(
                    reverse("backup:download_backup", kwargs={"filename": "backup_test.zip"})
                )
                
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response["Content-Type"], "application/zip")
                self.assertEqual(b"".join(response.streaming_content), b"fake zip content")

    def test_download_backup_not_found(self):
        """Test le téléchargement d'un backup inexistant."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with override_settings(BACKUP_ROOT=temp_dir):
                response = self.client.get(
                    reverse("backup:download_backup", kwargs={"filename": "nonexistent.zip"})
                )
                
                self.assertEqual(response.status_code, 404)

    def test_delete_backup_view(self):
        """Test la suppression d'un backup."""
        with tempfile.TemporaryDirectory() as temp_dir:
            backup_file = Path(temp_dir) / "backup_to_delete.zip"
            backup_file.write_bytes(b"content")
            
            with override_settings(BACKUP_ROOT=temp_dir):
                response = self.client.get(
                    reverse("backup:delete_backup", kwargs={"filename": "backup_to_delete.zip"})
                )
                
                self.assertEqual(response.status_code, 302)
                self.assertFalse(backup_file.exists())

    def test_delete_backup_not_found(self):
        """Test la suppression d'un backup inexistant."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with override_settings(BACKUP_ROOT=temp_dir):
                response = self.client.get(
                    reverse("backup:delete_backup", kwargs={"filename": "nonexistent.zip"})
                )
                
                self.assertEqual(response.status_code, 404)

    def test_unauthorized_access_redirects(self):
        """Test qu'un utilisateur non staff est redirigé."""
        self.client.logout()
        response = self.client.get(reverse("backup:list_backups"))
        self.assertEqual(response.status_code, 302)  # Redirection vers login


class BackupViewsNonStaffTests(TestCase):
    """Tests pour vérifier l'accès refusé aux non-staff."""

    def setUp(self):
        """Créer un utilisateur non staff."""
        self.user = User.objects.create_user(
            username="normaluser",
            email="normal@example.com",
            password="testpass123",
            is_staff=False
        )
        self.client = Client()
        self.client.login(username="normaluser", password="testpass123")

    def test_list_backups_redirects_for_non_staff(self):
        """Test qu'un utilisateur non staff est redirigé."""
        response = self.client.get(reverse("backup:list_backups"))
        self.assertEqual(response.status_code, 302)
