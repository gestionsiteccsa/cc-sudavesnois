import os
import shutil
from datetime import date
from io import BytesIO

from django.contrib import messages
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from PIL import Image

from .admin import CustomJournalAdmin
from .forms import JournalForm
from .models import Journal

User = get_user_model()  # Récupérer le modèle d'utilisateur personnalisé

# Définir un répertoire temporaire pour les médias
MEDIA_ROOT = "test_media"


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class JournalAddJournalViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Créer un superutilisateur personnalisé
        # print("Création du super_user\n")
        cls.superuser = User.objects.create_superuser(
            email="admin@example.com",  # Utiliser l'email comme nom d'utilisateur
            password="password123",
        )

    def setUp(self):
        self.client = Client()
        self.client.login(
            email="admin@example.com", password="password123"
        )  # Se connecter avec l'email
        self.add_journal_url = reverse("journal:add_journal")

        # Créer des fichiers de test (factices)
        self.document_content = b"This is a test document."
        self.document_file = SimpleUploadedFile(
            "test.pdf", self.document_content, content_type="application/pdf"
        )

        self.image = Image.new("RGB", (100, 100), color="red")
        buffer = BytesIO()
        self.image.save(buffer, format="jpeg")
        self.image_content = buffer.getvalue()
        self.cover_file = SimpleUploadedFile(
            "test.jpg", self.image_content, content_type="image/jpeg"
        )

    def tearDown(self):
        # Nettoyer les fichiers uploadés après chaque test
        Journal.objects.all().delete()
        if os.path.exists(MEDIA_ROOT):
            shutil.rmtree(MEDIA_ROOT)  # Supprimer le répertoire et son contenu

    def test_add_journal_get_view(self):
        """
        Test l'affichage du formulaire d'ajout de journal (GET request).
        """
        response = self.client.get(self.add_journal_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "journal/add_journal.html")
        self.assertIsInstance(response.context["journal"], JournalForm)

    def test_add_journal_post_valid_data(self):
        """
        Test la création d'un journal avec des données valides (POST request).
        """
        form_data = {
            "title": "New Valid Journal",
            "document": self.document_file,
            "cover": self.cover_file,
            "number": 10,
            "release_date": date(2024, 1, 1),
            "page_number": 25,
        }

        response = self.client.post(self.add_journal_url, form_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Journal.objects.count(), 1)

        new_journal = Journal.objects.first()
        self.assertEqual(new_journal.title, "New Valid Journal")
        self.assertEqual(new_journal.number, 10)
        self.assertEqual(new_journal.page_number, 25)
        self.assertEqual(new_journal.release_date, date(2024, 1, 1))

        # Vérifier le message de succès
        messages_list = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(str(messages_list[0]), "Le journal a été ajouté avec succès.")
        self.assertRedirects(response, reverse("journal:admin_journaux_list"))

    def test_add_journal_post_invalid_data(self):
        """
        Test la non-création d'un journal avec des données invalides (POST request).
        """
        response = self.client.post(
            self.add_journal_url,
            {
                "title": "",  # Champ requis manquant
                "number": "abc",  # Mauvais type
                "release_date": "invalid-date",
                "page_number": -5,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Journal.objects.count(), 0)
        self.assertTemplateUsed(response, "journal/add_journal.html")

        # Vérifier le message d'erreur
        messages_list = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(
            str(messages_list[0]), "Merci de corriger les erreurs dans le formulaire."
        )

    def test_add_journal_post_missing_files(self):
        """
        Test la non-création si les fichiers 'document' ou 'cover' sont manquants.
        """
        response = self.client.post(
            self.add_journal_url,
            {
                "title": "Missing Files Journal",
                "number": 11,
                "release_date": date(2024, 1, 1),
                "page_number": 26,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Journal.objects.count(), 0)
        self.assertTemplateUsed(response, "journal/add_journal.html")
        self.assertIn("document", response.context["journal"].errors)
        self.assertIn("cover", response.context["journal"].errors)

    def test_add_journal_post_invalid_file_types(self):
        """
        Test la non-création si les types de fichiers sont invalides.
        """
        invalid_document = SimpleUploadedFile(
            "test.txt", b"Invalid content", content_type="text/plain"
        )
        invalid_cover = SimpleUploadedFile(
            "test.gif", b"Invalid content", content_type="image/gif"
        )

        response = self.client.post(
            self.add_journal_url,
            {
                "title": "Invalid Files Journal",
                "number": 12,
                "release_date": date(2024, 1, 1),
                "page_number": 27,
                "document": invalid_document,
                "cover": invalid_cover,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Journal.objects.count(), 0)
        self.assertTemplateUsed(response, "journal/add_journal.html")
        self.assertIn("document", response.context["journal"].errors)
        self.assertIn("cover", response.context["journal"].errors)


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class JournalEditJournalViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Créer un superutilisateur personnalisé
        cls.superuser = User.objects.create_superuser(
            email="admin@example.com", password="password123"
        )

    def setUp(self):
        # print("Connexion avec le compte super_user\n")
        self.client = Client()
        self.client.login(email="admin@example.com", password="password123")
        self.journal = Journal.objects.create(
            title="Original Journal",
            number=1,
            release_date=date(2024, 1, 1),
            page_number=10,
        )
        self.edit_journal_url = reverse("journal:edit_journal", args=[self.journal.id])

        # Créer des fichiers de test (factices) - Réutilisable
        # print("Création de fichiers de test\n")
        self.document_content = b"This is a test document."
        self.document_file = SimpleUploadedFile(
            "test.pdf", self.document_content, content_type="application/pdf"
        )

        # Créer un fichier image de test
        self.image = Image.new("RGB", (100, 100), color="red")
        buffer = BytesIO()
        self.image.save(buffer, format="jpeg")
        self.image_content = buffer.getvalue()
        self.cover_file = SimpleUploadedFile(
            "test.jpg", self.image_content, content_type="image/jpeg"
        )

    def tearDown(self):
        # Nettoyer les fichiers uploadés après chaque test
        # print("Nettoyage des fichiers de test\n")
        Journal.objects.all().delete()
        if os.path.exists(MEDIA_ROOT):
            shutil.rmtree(MEDIA_ROOT)  # Supprimer le répertoire et son contenu

    def test_edit_journal_get_view(self):
        """
        Test l'affichage du formulaire d'édition de journal (GET request).
        """
        # print("Test d'affichage du formulaire d'édition de journal\n")
        response = self.client.get(self.edit_journal_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "journal/edit_journal.html")
        self.assertIsInstance(response.context["journal"], JournalForm)
        self.assertEqual(response.context["journal"].instance, self.journal)

    def test_edit_journal_post_valid_data(self):
        """
        Test la modification d'un journal avec des données valides (POST request).
        """
        # print("Test de modification d'un journal avec données valides\n")
        # Ajouter des fichiers initiaux au journal
        self.journal.document = self.document_file
        self.journal.cover = self.cover_file
        self.journal.save()
        original_document_path = self.journal.document.path
        original_cover_path = self.journal.cover.path

        # Créer de nouveaux fichiers pour la mise à jour
        new_document_content = b"This is an updated document."
        new_document_file = SimpleUploadedFile(
            "updated.pdf", new_document_content, content_type="application/pdf"
        )
        new_image = Image.new("RGB", (50, 50), color="blue")
        new_buffer = BytesIO()
        new_image.save(new_buffer, format="jpeg")
        new_cover_file = SimpleUploadedFile(
            "updated.jpg", new_buffer.getvalue(), content_type="image/jpeg"
        )

        form_data = {
            "title": "Updated Journal",
            "document": new_document_file,
            "cover": new_cover_file,
            "number": 2,
            "release_date": date(2024, 2, 1),
            "page_number": 20,
        }

        response = self.client.post(self.edit_journal_url, form_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("journal:admin_journaux_list"))

        # Vérifier que le journal a été mis à jour
        updated_journal = Journal.objects.get(id=self.journal.id)
        self.assertEqual(updated_journal.title, "Updated Journal")
        self.assertEqual(updated_journal.number, 2)
        self.assertEqual(updated_journal.release_date, date(2024, 2, 1))
        self.assertEqual(updated_journal.page_number, 20)

        # Vérifier que les anciens fichiers ont été supprimés et les nouveaux créés
        self.assertFalse(os.path.exists(original_document_path))
        self.assertFalse(os.path.exists(original_cover_path))
        self.assertTrue(os.path.exists(updated_journal.document.path))
        self.assertTrue(os.path.exists(updated_journal.cover.path))

        # Vérifier le message de succès
        messages_list = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(str(messages_list[0]), "Le journal a été modifié avec succès.")

    def test_edit_journal_post_invalid_data(self):
        """
        Test la non-modification d'un journal avec des données invalides (POST request).
        """
        # print("Test de non modification d'un journal avec données invalides\n")
        response = self.client.post(
            self.edit_journal_url,
            {
                "title": "",  # Champ requis manquant
                "number": "abc",
                "release_date": "invalid-date",
                "page_number": -5,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "journal/edit_journal.html")

        # Vérifier que le journal n'a pas été modifié
        updated_journal = Journal.objects.get(id=self.journal.id)
        self.assertEqual(updated_journal.title, "Original Journal")  # Reste inchangé
        self.assertEqual(updated_journal.number, 1)

        # Vérifier le message d'erreur
        messages_list = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(
            str(messages_list[0]), "Merci de corriger les erreurs dans le formulaire."
        )

    def test_edit_journal_post_no_file_change(self):
        """
        Test la modification d'un journal sans changer les fichiers (POST request).
        """
        # print("Test de modification d'un journal sans changer les fichiers\n")

        # Ajouter des fichiers initiaux au journal
        self.journal.document = self.document_file
        self.journal.cover = self.cover_file
        self.journal.save()

        form_data = {
            "title": "Updated Title Only",
            "number": 2,
            "release_date": date(2024, 2, 1),
            "page_number": 20,
            "document": self.journal.document.name,  # Passer le nom du fichier existant
            "cover": self.journal.cover.name,
        }

        response = self.client.post(self.edit_journal_url, form_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("journal:admin_journaux_list"))

        # Vérifier que le journal a été mis à jour
        updated_journal = Journal.objects.get(id=self.journal.id)
        self.assertEqual(updated_journal.title, "Updated Title Only")
        self.assertEqual(updated_journal.number, 2)

        # Vérifier que les fichiers n'ont pas été modifiés/supprimés
        self.assertTrue(os.path.exists(updated_journal.document.path))
        self.assertTrue(os.path.exists(updated_journal.cover.path))

        # Vérifier le message de succès
        messages_list = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(str(messages_list[0]), "Le journal a été modifié avec succès.")


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class JournalDeleteJournalViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Créer un superutilisateur personnalisé
        # print("Création du super_user\n")
        cls.superuser = User.objects.create_superuser(
            email="admin@example.com", password="password123"
        )

    def setUp(self):
        # print("Connexion avec le compte super_user\n")
        self.client = Client()
        self.client.login(email="admin@example.com", password="password123")
        self.journal = Journal.objects.create(
            title="Journal to Delete",
            number=1,
            release_date=date(2024, 1, 1),
            page_number=10,
        )
        self.delete_journal_url = reverse(
            "journal:delete_journal", args=[self.journal.id]
        )

        # Créer des fichiers de test (factices) - Réutilisable
        # print("Création de fichiers de test\n")
        self.document_content = b"This is a test document."
        self.document_file = SimpleUploadedFile(
            "test.pdf", self.document_content, content_type="application/pdf"
        )

        # Créer un fichier image de test
        self.image = Image.new("RGB", (100, 100), color="red")
        buffer = BytesIO()
        self.image.save(buffer, format="jpeg")
        self.image_content = buffer.getvalue()
        self.cover_file = SimpleUploadedFile(
            "test.jpg", self.image_content, content_type="image/jpeg"
        )

    def tearDown(self):
        # Nettoyer les fichiers uploadés après chaque test
        # print("Nettoyage des fichiers de test\n")
        Journal.objects.all().delete()
        if os.path.exists(MEDIA_ROOT):
            # Supprimer le répertoire et son contenu
            shutil.rmtree(MEDIA_ROOT)

    def test_delete_journal_get_view(self):
        """
        Test l'affichage de la page de confirmation de suppression (GET request).
        """
        # print("Test d'affichage de la page de confirmation de suppression\n")

        # Ajouter des fichiers initiaux au journal
        self.journal.document = self.document_file
        self.journal.cover = self.cover_file
        self.journal.save()

        response = self.client.get(self.delete_journal_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "journal/delete_journal.html")
        self.assertEqual(response.context["journal"], self.journal)
        self.assertContains(response, "Êtes-vous sûr de vouloir supprimer le journal ?")

    def test_delete_journal_post_confirm(self):
        """
        Test la suppression d'un journal avec confirmation (POST request).
        """
        # print("Test de suppression d'un journal avec confirmation\n")

        # Ajouter des fichiers initiaux au journal
        self.journal.document = self.document_file
        self.journal.cover = self.cover_file
        self.journal.save()

        response = self.client.post(self.delete_journal_url, {"confirm": "yes"})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("journal:admin_journaux_list"))
        self.assertEqual(Journal.objects.count(), 0)

        # Vérifier que les fichiers ont été supprimés
        self.assertFalse(os.path.exists(self.journal.document.path))
        self.assertFalse(os.path.exists(self.journal.cover.path))

        # Vérifier le message de succès
        messages_list = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(
            str(messages_list[0]), "Le journal a été supprimé avec succès."
        )

    def test_delete_journal_post_cancel(self):
        """
        Test d'annulation de la suppression d'un journal (POST request).
        """
        # print("Test d'annulation de suppression d'un journal\n")
        # Ajouter des fichiers initiaux au journal
        self.journal.document = self.document_file
        self.journal.cover = self.cover_file
        self.journal.save()

        response = self.client.post(self.delete_journal_url, {"confirm": "no"})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("journal:admin_journaux_list"))
        self.assertEqual(Journal.objects.count(), 1)

        self.assertTrue(os.path.exists(self.journal.document.path))
        self.assertTrue(os.path.exists(self.journal.cover.path))

        messages_list = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)

    def test_delete_journal_post_no_confirmation(self):
        """
        Test de la non-suppression d'un journal sans confirmation (POST request).
        """
        # print("Test de non suppression d'un journal sans confirmation\n")
        # Ajouter des fichiers initiaux au journal
        self.journal.document = self.document_file
        self.journal.cover = self.cover_file
        self.journal.save()

        response = self.client.post(self.delete_journal_url, {})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("journal:admin_journaux_list"))
        self.assertEqual(Journal.objects.count(), 1)

        # Vérifier que les fichiers n'ont pas été supprimés
        self.assertTrue(os.path.exists(self.journal.document.path))
        self.assertTrue(os.path.exists(self.journal.cover.path))

        messages_list = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)

    def test_delete_journal_post_invalid_confirmation(self):
        """
        Test de la non-suppression d'un journal avec une confirmation invalide (POST request).
        """
        # print("Test de non suppression d'un journal avec confirmation invalide\n")
        # Ajouter des fichiers initiaux au journal
        self.journal.document = self.document_file
        self.journal.cover = self.cover_file
        self.journal.save()

        response = self.client.post(self.delete_journal_url, {"confirm": "invalid"})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("journal:admin_journaux_list"))
        self.assertEqual(Journal.objects.count(), 1)

        # Vérifier que les fichiers n'ont pas été supprimés
        self.assertTrue(os.path.exists(self.journal.document.path))
        self.assertTrue(os.path.exists(self.journal.cover.path))

        messages_list = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class JournalPublicViewTestCase(TestCase):
    """Tests pour les vues publiques de l'application Journal"""

    def setUp(self):
        self.client = Client()
        self.journal_url = reverse("journal:journal")

        # Créer des fichiers de test
        self.document_content = b"This is a test document."
        self.document_file = SimpleUploadedFile(
            "test.pdf", self.document_content, content_type="application/pdf"
        )

        self.image = Image.new("RGB", (100, 100), color="red")
        buffer = BytesIO()
        self.image.save(buffer, format="jpeg")
        self.image_content = buffer.getvalue()
        self.cover_file = SimpleUploadedFile(
            "test.jpg", self.image_content, content_type="image/jpeg"
        )

    def tearDown(self):
        # Nettoyer les fichiers uploadés après chaque test
        Journal.objects.all().delete()
        if os.path.exists(MEDIA_ROOT):
            shutil.rmtree(MEDIA_ROOT)

    def test_journal_list_view_empty(self):
        """Test de la vue publique des journaux avec liste vide"""
        response = self.client.get(self.journal_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "journal/journal.html")
        self.assertEqual(len(response.context["journals"]), 0)

    def test_journal_list_view_with_journals(self):
        """Test de la vue publique avec des journaux"""
        # Créer quelques journaux
        for i in range(5):
            Journal.objects.create(
                title=f"Journal {i+1}",
                number=i + 1,
                release_date=date(2024, 1, i + 1),
                page_number=10 + i,
                document=self.document_file,
                cover=self.cover_file,
            )

        response = self.client.get(self.journal_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "journal/journal.html")
        # Vérifier que la pagination limite à 3 journaux par page
        self.assertEqual(len(response.context["journals"]), 3)

    def test_journal_pagination_first_page(self):
        """Test de la pagination - première page"""
        # Créer 5 journaux
        for i in range(5):
            Journal.objects.create(
                title=f"Journal {i+1}",
                number=i + 1,
                release_date=date(2024, 1, i + 1),
                page_number=10 + i,
                document=self.document_file,
                cover=self.cover_file,
            )

        response = self.client.get(self.journal_url + "?page=1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["journals"]), 3)
        # Vérifier l'ordre (par numéro décroissant)
        journals = response.context["journals"]
        self.assertEqual(journals[0].number, 5)
        self.assertEqual(journals[1].number, 4)
        self.assertEqual(journals[2].number, 3)

    def test_journal_pagination_second_page(self):
        """Test de la pagination - deuxième page"""
        # Créer 5 journaux
        for i in range(5):
            Journal.objects.create(
                title=f"Journal {i+1}",
                number=i + 1,
                release_date=date(2024, 1, i + 1),
                page_number=10 + i,
                document=self.document_file,
                cover=self.cover_file,
            )

        response = self.client.get(self.journal_url + "?page=2")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["journals"]), 2)
        # Vérifier l'ordre sur la deuxième page
        journals = response.context["journals"]
        self.assertEqual(journals[0].number, 2)
        self.assertEqual(journals[1].number, 1)

    def test_journal_pagination_invalid_page(self):
        """Test de la pagination avec page invalide"""
        # Créer quelques journaux
        for i in range(3):
            Journal.objects.create(
                title=f"Journal {i+1}",
                number=i + 1,
                release_date=date(2024, 1, i + 1),
                page_number=10 + i,
                document=self.document_file,
                cover=self.cover_file,
            )

        # Test avec page non numérique
        response = self.client.get(self.journal_url + "?page=abc")
        self.assertEqual(response.status_code, 200)
        # Doit afficher la première page
        self.assertEqual(len(response.context["journals"]), 3)

    def test_journal_pagination_out_of_range(self):
        """Test de la pagination avec page hors limites"""
        # Créer quelques journaux
        for i in range(3):
            Journal.objects.create(
                title=f"Journal {i+1}",
                number=i + 1,
                release_date=date(2024, 1, i + 1),
                page_number=10 + i,
                document=self.document_file,
                cover=self.cover_file,
            )

        # Test avec page trop élevée
        response = self.client.get(self.journal_url + "?page=999")
        self.assertEqual(response.status_code, 200)
        # Doit afficher la dernière page
        self.assertEqual(len(response.context["journals"]), 3)


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class JournalModelTestCase(TestCase):
    """Tests pour le modèle Journal"""

    def setUp(self):
        # Créer des fichiers de test
        self.document_content = b"This is a test document."
        self.document_file = SimpleUploadedFile(
            "test.pdf", self.document_content, content_type="application/pdf"
        )

        self.image = Image.new("RGB", (100, 100), color="red")
        buffer = BytesIO()
        self.image.save(buffer, format="jpeg")
        self.image_content = buffer.getvalue()
        self.cover_file = SimpleUploadedFile(
            "test.jpg", self.image_content, content_type="image/jpeg"
        )

    def tearDown(self):
        # Nettoyer les fichiers uploadés après chaque test
        Journal.objects.all().delete()
        if os.path.exists(MEDIA_ROOT):
            shutil.rmtree(MEDIA_ROOT)

    def test_journal_str_method(self):
        """Test de la méthode __str__ du modèle Journal"""
        journal = Journal.objects.create(
            title="Test Journal Title",
            number=1,
            release_date=date(2024, 1, 1),
            page_number=10,
            document=self.document_file,
            cover=self.cover_file,
        )
        self.assertEqual(str(journal), "Test Journal Title")

    def test_get_document_size_with_file(self):
        """Test du calcul de taille de document avec fichier existant"""
        journal = Journal.objects.create(
            title="Test Journal",
            number=1,
            release_date=date(2024, 1, 1),
            page_number=10,
            document=self.document_file,
            cover=self.cover_file,
        )

        size = journal.get_document_size()
        self.assertIsNotNone(size)
        self.assertIn("Ko", size)  # Le fichier de test est petit, donc en Ko

    def test_get_document_size_large_file(self):
        """Test du calcul de taille pour un gros document (simulation)"""
        # Créer un fichier plus volumineux (> 1MB)
        large_content = b"x" * (1024 * 1024 + 1)  # 1MB + 1 byte
        large_document = SimpleUploadedFile(
            "large.pdf", large_content, content_type="application/pdf"
        )

        journal = Journal.objects.create(
            title="Test Journal Large",
            number=1,
            release_date=date(2024, 1, 1),
            page_number=10,
            document=large_document,
            cover=self.cover_file,
        )

        size = journal.get_document_size()
        self.assertIsNotNone(size)
        self.assertIn("Mo", size)  # Doit être en Mo

    def test_get_document_size_file_not_found(self):
        """Test du calcul de taille avec fichier manquant"""
        journal = Journal.objects.create(
            title="Test Journal",
            number=1,
            release_date=date(2024, 1, 1),
            page_number=10,
            document=self.document_file,
            cover=self.cover_file,
        )

        # Supprimer le fichier physique
        if os.path.exists(journal.document.path):
            os.remove(journal.document.path)

        size = journal.get_document_size()
        self.assertFalse(size)

    def test_get_cover_size_with_file(self):
        """Test du calcul de taille de couverture avec fichier existant"""
        journal = Journal.objects.create(
            title="Test Journal",
            number=1,
            release_date=date(2024, 1, 1),
            page_number=10,
            document=self.document_file,
            cover=self.cover_file,
        )

        size = journal.get_cover_size()
        self.assertIsNotNone(size)
        self.assertIn("Ko", size)  # Le fichier de test est petit, donc en Ko

    def test_get_cover_size_large_file(self):
        """Test du calcul de taille pour une grosse couverture (simulation)"""
        # Créer une image plus volumineuse
        large_image = Image.new("RGB", (2000, 2000), color="blue")
        large_buffer = BytesIO()
        large_image.save(large_buffer, format="jpeg", quality=100)
        large_cover = SimpleUploadedFile(
            "large.jpg", large_buffer.getvalue(), content_type="image/jpeg"
        )

        journal = Journal.objects.create(
            title="Test Journal Large Cover",
            number=1,
            release_date=date(2024, 1, 1),
            page_number=10,
            document=self.document_file,
            cover=large_cover,
        )

        size = journal.get_cover_size()
        self.assertIsNotNone(size)
        # Peut être en Ko ou Mo selon la compression

    def test_get_cover_size_file_not_found(self):
        """Test du calcul de taille avec couverture manquante"""
        journal = Journal.objects.create(
            title="Test Journal",
            number=1,
            release_date=date(2024, 1, 1),
            page_number=10,
            document=self.document_file,
            cover=self.cover_file,
        )

        # Supprimer le fichier physique
        if os.path.exists(journal.cover.path):
            os.remove(journal.cover.path)

        size = journal.get_cover_size()
        self.assertFalse(size)

    def test_journal_default_values(self):
        """Test des valeurs par défaut du modèle"""
        journal = Journal(
            title="Test Default",
            release_date=date(2024, 1, 1),
            document=self.document_file,
            cover=self.cover_file,
        )
        self.assertEqual(journal.number, 0)
        self.assertEqual(journal.page_number, 0)


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class JournalAdminTestCase(TestCase):
    """Tests pour l'interface d'administration des journaux"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.superuser = User.objects.create_superuser(
            email="admin@example.com", password="password123"
        )

    def setUp(self):
        self.client = Client()
        self.client.login(email="admin@example.com", password="password123")
        self.site = AdminSite()
        self.admin = CustomJournalAdmin(Journal, self.site)

        # Créer des fichiers de test
        self.document_content = b"This is a test document."
        self.document_file = SimpleUploadedFile(
            "test.pdf", self.document_content, content_type="application/pdf"
        )

        self.image = Image.new("RGB", (100, 100), color="red")
        buffer = BytesIO()
        self.image.save(buffer, format="jpeg")
        self.image_content = buffer.getvalue()
        self.cover_file = SimpleUploadedFile(
            "test.jpg", self.image_content, content_type="image/jpeg"
        )

    def tearDown(self):
        Journal.objects.all().delete()
        if os.path.exists(MEDIA_ROOT):
            shutil.rmtree(MEDIA_ROOT)

    def test_admin_list_display(self):
        """Test de l'affichage de la liste dans l'admin"""
        # Créer un journal
        journal = Journal.objects.create(
            title="Test Admin Journal",
            number=1,
            release_date=date(2024, 1, 1),
            page_number=10,
            document=self.document_file,
            cover=self.cover_file,
        )

        # Vérifier que les champs d'affichage sont configurés
        self.assertTrue(hasattr(self.admin, "list_display"))

        # Test d'accès à la page d'administration
        admin_url = reverse("admin:journal_journal_changelist")
        response = self.client.get(admin_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Admin Journal")

    def test_admin_search_fields(self):
        """Test des champs de recherche dans l'admin"""
        # Créer quelques journaux
        Journal.objects.create(
            title="Journal Recherche 1",
            number=1,
            release_date=date(2024, 1, 1),
            page_number=10,
            document=self.document_file,
            cover=self.cover_file,
        )
        Journal.objects.create(
            title="Journal Recherche 2",
            number=2,
            release_date=date(2024, 2, 1),
            page_number=15,
            document=self.document_file,
            cover=self.cover_file,
        )

        # Vérifier que les champs de recherche sont configurés
        self.assertTrue(hasattr(self.admin, "search_fields"))

        # Test de recherche
        admin_url = reverse("admin:journal_journal_changelist")
        response = self.client.get(admin_url + "?q=Recherche")
        self.assertEqual(response.status_code, 200)

    def test_admin_list_filter(self):
        """Test des filtres dans l'admin"""
        # Créer des journaux avec différentes dates
        Journal.objects.create(
            title="Journal 2024",
            number=1,
            release_date=date(2024, 1, 1),
            page_number=10,
            document=self.document_file,
            cover=self.cover_file,
        )
        Journal.objects.create(
            title="Journal 2023",
            number=2,
            release_date=date(2023, 12, 1),
            page_number=15,
            document=self.document_file,
            cover=self.cover_file,
        )

        # Vérifier que les filtres sont configurés
        if hasattr(self.admin, "list_filter"):
            admin_url = reverse("admin:journal_journal_changelist")
            response = self.client.get(admin_url)
            self.assertEqual(response.status_code, 200)

    def test_admin_ordering(self):
        """Test de l'ordre d'affichage dans l'admin"""
        # Créer plusieurs journaux
        for i in range(3):
            Journal.objects.create(
                title=f"Journal {i+1}",
                number=i + 1,
                release_date=date(2024, 1, i + 1),
                page_number=10 + i,
                document=self.document_file,
                cover=self.cover_file,
            )

        # Vérifier l'ordre d'affichage
        admin_url = reverse("admin:journal_journal_changelist")
        response = self.client.get(admin_url)
        self.assertEqual(response.status_code, 200)

    def test_admin_add_journal(self):
        """Test d'ajout d'un journal via l'admin"""
        admin_add_url = reverse("admin:journal_journal_add")
        response = self.client.get(admin_add_url)
        self.assertEqual(response.status_code, 200)

        # Test d'ajout avec données valides
        response = self.client.post(
            admin_add_url,
            {
                "title": "Journal Admin Test",
                "number": 99,
                "release_date": "2024-01-01",
                "page_number": 20,
                "document": self.document_file,
                "cover": self.cover_file,
            },
        )
        # Redirection après création réussie
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Journal.objects.filter(title="Journal Admin Test").exists())

    def test_admin_change_journal(self):
        """Test de modification d'un journal via l'admin"""
        journal = Journal.objects.create(
            title="Journal à Modifier",
            number=1,
            release_date=date(2024, 1, 1),
            page_number=10,
            document=self.document_file,
            cover=self.cover_file,
        )

        admin_change_url = reverse("admin:journal_journal_change", args=[journal.id])
        response = self.client.get(admin_change_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Journal à Modifier")


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class JournalPermissionTestCase(TestCase):
    """Tests des permissions pour l'application Journal"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Créer un utilisateur normal (sans permissions)
        cls.normal_user = User.objects.create_user(
            email="user@example.com", password="password123"
        )
        # Créer un superutilisateur
        cls.superuser = User.objects.create_superuser(
            email="admin@example.com", password="password123"
        )

    def setUp(self):
        self.client = Client()

        # Créer des fichiers de test
        self.document_content = b"This is a test document."
        self.document_file = SimpleUploadedFile(
            "test.pdf", self.document_content, content_type="application/pdf"
        )

        self.image = Image.new("RGB", (100, 100), color="red")
        buffer = BytesIO()
        self.image.save(buffer, format="jpeg")
        self.image_content = buffer.getvalue()
        self.cover_file = SimpleUploadedFile(
            "test.jpg", self.image_content, content_type="image/jpeg"
        )

    def tearDown(self):
        Journal.objects.all().delete()
        if os.path.exists(MEDIA_ROOT):
            shutil.rmtree(MEDIA_ROOT)

    def test_public_view_no_login_required(self):
        """Test que la vue publique ne nécessite pas de connexion"""
        response = self.client.get(reverse("journal:journal"))
        self.assertEqual(response.status_code, 200)

    def test_admin_views_require_permissions(self):
        """Test que les vues d'administration nécessitent des permissions"""
        # Test sans connexion
        admin_urls = [
            reverse("journal:admin_journaux_list"),
            reverse("journal:add_journal"),
        ]

        for url in admin_urls:
            response = self.client.get(url)
            # Doit rediriger vers la page de connexion ou retourner 403
            self.assertIn(response.status_code, [302, 403])

    def test_admin_views_with_normal_user(self):
        """Test des vues d'administration avec utilisateur normal"""
        self.client.login(email="user@example.com", password="password123")

        admin_urls = [
            reverse("journal:admin_journaux_list"),
            reverse("journal:add_journal"),
        ]

        for url in admin_urls:
            response = self.client.get(url)
            # Doit retourner 403 (permission refusée) ou 302 (redirection)
            self.assertIn(response.status_code, [302, 403])

    def test_admin_views_with_superuser(self):
        """Test des vues d'administration avec superutilisateur"""
        self.client.login(email="admin@example.com", password="password123")

        # Test de la liste des journaux
        response = self.client.get(reverse("journal:admin_journaux_list"))
        self.assertEqual(response.status_code, 200)

        # Test du formulaire d'ajout
        response = self.client.get(reverse("journal:add_journal"))
        self.assertEqual(response.status_code, 200)
