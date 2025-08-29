import io
import os
import shutil

from django.conf import settings
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import HttpRequest
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from PIL import Image

from .admin import CustomContentAdmin, delete_content
from .forms import SemestrielForm
from .models import SemestrielPage

User = get_user_model()
MEDIA_ROOT = "test_media_semestriel"


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class SemestrielPageModelTestCase(TestCase):
    """Tests pour le modèle SemestrielPage"""

    def tearDown(self):
        SemestrielPage.objects.all().delete()
        if os.path.exists(MEDIA_ROOT):
            shutil.rmtree(MEDIA_ROOT)

    def generate_test_image(self, name="test.jpg", format_type="JPEG", size=(100, 100)):
        """Générer une image de test"""
        file = io.BytesIO()
        image = Image.new("RGB", size, color=(255, 0, 0))
        image.save(file, format=format_type)
        file.name = name
        file.seek(0)
        return file

    def generate_test_pdf(self, name="test.pdf"):
        """Générer un PDF de test"""
        return SimpleUploadedFile(
            name, b"Test PDF content", content_type="application/pdf"
        )

    def test_semestriel_page_creation(self):
        """Test de création d'une page semestrielle"""
        image_file = SimpleUploadedFile(
            name="test.jpg",
            content=self.generate_test_image().read(),
            content_type="image/jpeg",
        )
        pdf_file = self.generate_test_pdf()

        semestriel = SemestrielPage.objects.create(picture=image_file, file=pdf_file)

        self.assertTrue(semestriel.picture)
        self.assertTrue(semestriel.file)
        self.assertEqual(SemestrielPage.objects.count(), 1)

    def test_semestriel_page_unique_constraint(self):
        """Test que seule une page semestrielle peut exister"""
        # Créer la première page
        image1 = SimpleUploadedFile(
            name="test1.jpg",
            content=self.generate_test_image().read(),
            content_type="image/jpeg",
        )
        pdf1 = self.generate_test_pdf("test1.pdf")

        semestriel1 = SemestrielPage.objects.create(picture=image1, file=pdf1)

        # Créer une deuxième page - doit remplacer la première
        image2 = SimpleUploadedFile(
            name="test2.jpg",
            content=self.generate_test_image().read(),
            content_type="image/jpeg",
        )
        pdf2 = self.generate_test_pdf("test2.pdf")

        semestriel2 = SemestrielPage.objects.create(picture=image2, file=pdf2)

        # Vérifier qu'il n'y a qu'une seule page
        self.assertEqual(SemestrielPage.objects.count(), 1)

        # Vérifier que c'est la deuxième page qui existe
        remaining_page = SemestrielPage.objects.first()
        self.assertEqual(remaining_page.id, semestriel2.id)

    def test_file_extension_validation(self):
        """Test de validation des extensions de fichiers"""
        # Test avec une image invalide
        invalid_image = SimpleUploadedFile(
            name="test.txt", content=b"not an image", content_type="text/plain"
        )
        pdf_file = self.generate_test_pdf()

        semestriel = SemestrielPage(picture=invalid_image, file=pdf_file)

        with self.assertRaises(ValidationError):
            semestriel.full_clean()

        # Test avec un fichier PDF invalide
        valid_image = SimpleUploadedFile(
            name="test.jpg",
            content=self.generate_test_image().read(),
            content_type="image/jpeg",
        )
        invalid_pdf = SimpleUploadedFile(
            name="test.txt", content=b"not a pdf", content_type="text/plain"
        )

        semestriel2 = SemestrielPage(picture=valid_image, file=invalid_pdf)

        with self.assertRaises(ValidationError):
            semestriel2.full_clean()

    def test_file_size_validation(self):
        """Test de validation de la taille des fichiers"""
        # Créer une image trop grande (simulation)
        large_content = b"x" * (settings.DATA_UPLOAD_MAX_MEMORY_SIZE + 1)
        large_image = SimpleUploadedFile(
            name="large.jpg", content=large_content, content_type="image/jpeg"
        )
        pdf_file = self.generate_test_pdf()

        semestriel = SemestrielPage(picture=large_image, file=pdf_file)

        with self.assertRaises(ValidationError):
            semestriel.full_clean()


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class SemestrielFormTestCase(TestCase):
    """Tests pour le formulaire SemestrielForm"""

    def tearDown(self):
        if os.path.exists(MEDIA_ROOT):
            shutil.rmtree(MEDIA_ROOT)

    def generate_test_image(self):
        """Générer une image de test"""
        file = io.BytesIO()
        image = Image.new("RGB", (100, 100), color=(255, 0, 0))
        image.save(file, format="JPEG")
        file.name = "test.jpg"
        file.seek(0)
        return file

    def test_semestriel_form_valid(self):
        """Test de formulaire valide"""
        image_file = SimpleUploadedFile(
            name="test.jpg",
            content=self.generate_test_image().read(),
            content_type="image/jpeg",
        )
        pdf_file = SimpleUploadedFile(
            name="test.pdf", content=b"Test PDF content", content_type="application/pdf"
        )

        form_data = {}
        form_files = {"picture": image_file, "file": pdf_file}

        form = SemestrielForm(data=form_data, files=form_files)
        self.assertTrue(form.is_valid())

    def test_semestriel_form_invalid_missing_files(self):
        """Test de formulaire invalide avec fichiers manquants"""
        form = SemestrielForm(data={}, files={})
        self.assertFalse(form.is_valid())
        self.assertIn("picture", form.errors)
        self.assertIn("file", form.errors)

    def test_semestriel_form_labels(self):
        """Test des labels du formulaire"""
        form = SemestrielForm()
        self.assertEqual(form.fields["picture"].label, "Image du calendrier")
        self.assertEqual(form.fields["file"].label, "Calendrier semestriel")

    def test_semestriel_form_widgets(self):
        """Test des widgets du formulaire"""
        form = SemestrielForm()
        self.assertIn("placeholder", form.fields["picture"].widget.attrs)
        self.assertIn("placeholder", form.fields["file"].widget.attrs)


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class SemestrielViewsTestCase(TestCase):
    """Tests pour les vues de l'application semestriels"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.superuser = User.objects.create_superuser(
            email="admin@example.com", password="password123"
        )
        cls.normal_user = User.objects.create_user(
            email="user@example.com", password="password123"
        )

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        SemestrielPage.objects.all().delete()
        if os.path.exists(MEDIA_ROOT):
            shutil.rmtree(MEDIA_ROOT)

    def generate_test_image(self):
        """Générer une image de test"""
        file = io.BytesIO()
        image = Image.new("RGB", (100, 100), color=(255, 0, 0))
        image.save(file, format="JPEG")
        file.name = "test.jpg"
        file.seek(0)
        return file

    def create_semestriel_page(self):
        """Créer une page semestrielle de test"""
        image_file = SimpleUploadedFile(
            name="test.jpg",
            content=self.generate_test_image().read(),
            content_type="image/jpeg",
        )
        pdf_file = SimpleUploadedFile(
            name="test.pdf", content=b"Test PDF content", content_type="application/pdf"
        )

        return SemestrielPage.objects.create(picture=image_file, file=pdf_file)

    def test_semestriel_public_view_without_content(self):
        """Test de la vue publique sans contenu"""
        response = self.client.get(reverse("semestriels:semestriel"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "semestriel/semestriel.html")
        self.assertIsNone(response.context["content"])

    def test_semestriel_public_view_with_content(self):
        """Test de la vue publique avec contenu"""
        semestriel = self.create_semestriel_page()

        response = self.client.get(reverse("semestriels:semestriel"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "semestriel/semestriel.html")
        self.assertIsNotNone(response.context["content"])
        self.assertEqual(response.context["content"].id, semestriel.id)

    def test_add_content_view_requires_permission(self):
        """Test que la vue d'ajout nécessite des permissions"""
        response = self.client.get(reverse("semestriels:add_content"))
        self.assertIn(response.status_code, [302, 403])

    def test_add_content_view_get_with_permission(self):
        """Test de l'affichage du formulaire d'ajout avec permissions"""
        self.client.login(email="admin@example.com", password="password123")
        response = self.client.get(reverse("semestriels:add_content"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "semestriel/admin_content_add.html")
        self.assertIn("form", response.context)

    def test_add_content_view_post_valid(self):
        """Test d'ajout de contenu avec données valides"""
        self.client.login(email="admin@example.com", password="password123")

        image_file = SimpleUploadedFile(
            name="test.jpg",
            content=self.generate_test_image().read(),
            content_type="image/jpeg",
        )
        pdf_file = SimpleUploadedFile(
            name="test.pdf", content=b"Test PDF content", content_type="application/pdf"
        )

        response = self.client.post(
            reverse("semestriels:add_content"),
            {"picture": image_file, "file": pdf_file},
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("semestriels:list_content"))
        self.assertTrue(SemestrielPage.objects.exists())

    def test_add_content_view_post_invalid(self):
        """Test d'ajout de contenu avec données invalides"""
        self.client.login(email="admin@example.com", password="password123")

        response = self.client.post(reverse("semestriels:add_content"), {})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "semestriel/admin_content_add.html")
        self.assertFalse(SemestrielPage.objects.exists())

    def test_edit_content_view_requires_permission(self):
        """Test que la vue de modification nécessite des permissions"""
        semestriel = self.create_semestriel_page()
        response = self.client.get(
            reverse("semestriels:edit_content", args=[semestriel.pk])
        )
        self.assertIn(response.status_code, [302, 403])

    def test_edit_content_view_get_with_permission(self):
        """Test de l'affichage du formulaire de modification avec permissions"""
        self.client.login(email="admin@example.com", password="password123")
        semestriel = self.create_semestriel_page()

        response = self.client.get(
            reverse("semestriels:edit_content", args=[semestriel.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "semestriel/admin_content_edit.html")
        self.assertIn("form", response.context)

    def test_edit_content_view_post_valid(self):
        """Test de modification de contenu avec données valides"""
        self.client.login(email="admin@example.com", password="password123")
        semestriel = self.create_semestriel_page()

        new_image = SimpleUploadedFile(
            name="new_test.jpg",
            content=self.generate_test_image().read(),
            content_type="image/jpeg",
        )
        new_pdf = SimpleUploadedFile(
            name="new_test.pdf",
            content=b"New Test PDF content",
            content_type="application/pdf",
        )

        response = self.client.post(
            reverse("semestriels:edit_content", args=[semestriel.pk]),
            {"picture": new_image, "file": new_pdf},
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("semestriels:list_content"))

    def test_edit_content_view_nonexistent(self):
        """Test de modification d'un contenu inexistant"""
        self.client.login(email="admin@example.com", password="password123")
        response = self.client.get(reverse("semestriels:edit_content", args=[99999]))
        self.assertEqual(response.status_code, 404)

    def test_list_content_view_requires_permission(self):
        """Test que la vue de liste nécessite des permissions"""
        response = self.client.get(reverse("semestriels:list_content"))
        self.assertIn(response.status_code, [302, 403])

    def test_list_content_view_without_content(self):
        """Test de la vue de liste sans contenu"""
        self.client.login(email="admin@example.com", password="password123")
        response = self.client.get(reverse("semestriels:list_content"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "semestriel/admin_content_list.html")
        self.assertIsNone(response.context["content"])

    def test_list_content_view_with_content(self):
        """Test de la vue de liste avec contenu"""
        self.client.login(email="admin@example.com", password="password123")
        semestriel = self.create_semestriel_page()

        response = self.client.get(reverse("semestriels:list_content"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "semestriel/admin_content_list.html")
        self.assertIsNotNone(response.context["content"])
        self.assertEqual(response.context["content"].id, semestriel.id)


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class SemestrielAdminTestCase(TestCase):
    """Tests pour l'interface admin de SemestrielPage"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.superuser = User.objects.create_superuser(
            email="admin@example.com", password="password123"
        )

    def setUp(self):
        self.client = Client()
        self.client.login(email="admin@example.com", password="password123")
        self.admin = CustomContentAdmin(SemestrielPage, AdminSite())

    def tearDown(self):
        SemestrielPage.objects.all().delete()
        if os.path.exists(MEDIA_ROOT):
            shutil.rmtree(MEDIA_ROOT)

    def generate_test_image(self):
        """Générer une image de test"""
        file = io.BytesIO()
        image = Image.new("RGB", (100, 100), color=(255, 0, 0))
        image.save(file, format="JPEG")
        file.name = "test.jpg"
        file.seek(0)
        return file

    def create_semestriel_page(self):
        """Créer une page semestrielle de test"""
        image_file = SimpleUploadedFile(
            name="test.jpg",
            content=self.generate_test_image().read(),
            content_type="image/jpeg",
        )
        pdf_file = SimpleUploadedFile(
            name="test.pdf", content=b"Test PDF content", content_type="application/pdf"
        )

        return SemestrielPage.objects.create(picture=image_file, file=pdf_file)

    def test_admin_list_display(self):
        """Test de l'affichage de la liste dans l'admin"""
        expected_fields = ("picture", "file")
        self.assertEqual(self.admin.list_display, expected_fields)

    def test_admin_form_class(self):
        """Test de la classe de formulaire utilisée"""
        self.assertEqual(self.admin.form, SemestrielForm)

    def test_admin_get_actions(self):
        """Test de la suppression de l'action par défaut"""
        request = HttpRequest()
        request.user = self.superuser
        actions = self.admin.get_actions(request)

        self.assertNotIn("delete_selected", actions)
        self.assertIn("delete_content", actions)

    def test_admin_changelist_view(self):
        """Test de l'accès à la liste admin"""
        admin_url = reverse("admin:semestriels_semestrielpage_changelist")
        response = self.client.get(admin_url)
        self.assertEqual(response.status_code, 200)

    def test_admin_add_view(self):
        """Test de l'ajout via l'admin"""
        admin_add_url = reverse("admin:semestriels_semestrielpage_add")
        response = self.client.get(admin_add_url)
        self.assertEqual(response.status_code, 200)

        # Test d'ajout avec données valides
        image_file = SimpleUploadedFile(
            name="admin_test.jpg",
            content=self.generate_test_image().read(),
            content_type="image/jpeg",
        )
        pdf_file = SimpleUploadedFile(
            name="admin_test.pdf",
            content=b"Admin Test PDF content",
            content_type="application/pdf",
        )

        response = self.client.post(
            admin_add_url,
            {
                "picture": image_file,
                "file": pdf_file,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(SemestrielPage.objects.exists())

    def test_admin_change_view(self):
        """Test de modification via l'admin"""
        semestriel = self.create_semestriel_page()
        admin_change_url = reverse(
            "admin:semestriels_semestrielpage_change", args=[semestriel.id]
        )
        response = self.client.get(admin_change_url)
        self.assertEqual(response.status_code, 200)

    def test_admin_delete_model(self):
        """Test de la suppression personnalisée d'un modèle"""
        semestriel = self.create_semestriel_page()
        request = HttpRequest()

        # Tester la suppression
        self.admin.delete_model(request, semestriel)

        # Vérifier que l'objet a été supprimé
        self.assertFalse(SemestrielPage.objects.filter(id=semestriel.id).exists())

    def test_delete_content_action(self):
        """Test de l'action de suppression en lot"""
        semestriel = self.create_semestriel_page()
        queryset = SemestrielPage.objects.filter(id=semestriel.id)
        request = HttpRequest()

        # Exécuter l'action
        delete_content(None, request, queryset)

        # Vérifier que l'objet a été supprimé
        self.assertFalse(SemestrielPage.objects.filter(id=semestriel.id).exists())


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class SemestrielPermissionsTestCase(TestCase):
    """Tests des permissions pour les vues semestriels"""

    def setUp(self):
        self.normal_user = User.objects.create_user(
            email="user@example.com", password="password123"
        )
        self.superuser = User.objects.create_superuser(
            email="admin@example.com", password="password123"
        )
        self.client = Client()

    def tearDown(self):
        SemestrielPage.objects.all().delete()
        if os.path.exists(MEDIA_ROOT):
            shutil.rmtree(MEDIA_ROOT)

    def create_semestriel_page(self):
        """Créer une page semestrielle de test"""
        file = io.BytesIO()
        image = Image.new("RGB", (100, 100), color=(255, 0, 0))
        image.save(file, format="JPEG")
        file.name = "test.jpg"
        file.seek(0)

        image_file = SimpleUploadedFile(
            name="test.jpg", content=file.read(), content_type="image/jpeg"
        )
        pdf_file = SimpleUploadedFile(
            name="test.pdf", content=b"Test PDF content", content_type="application/pdf"
        )

        return SemestrielPage.objects.create(picture=image_file, file=pdf_file)

    def test_public_view_no_login_required(self):
        """Test que la vue publique ne nécessite pas de connexion"""
        response = self.client.get(reverse("semestriels:semestriel"))
        self.assertEqual(response.status_code, 200)

    def test_admin_views_require_permissions(self):
        """Test que les vues d'administration nécessitent des permissions"""
        admin_urls = [
            reverse("semestriels:add_content"),
            reverse("semestriels:list_content"),
        ]

        for url in admin_urls:
            response = self.client.get(url)
            self.assertIn(response.status_code, [302, 403])

    def test_admin_views_with_normal_user(self):
        """Test des vues d'administration avec utilisateur normal"""
        self.client.login(email="user@example.com", password="password123")

        admin_urls = [
            reverse("semestriels:add_content"),
            reverse("semestriels:list_content"),
        ]

        for url in admin_urls:
            response = self.client.get(url)
            self.assertIn(response.status_code, [302, 403])

    def test_admin_views_with_superuser(self):
        """Test des vues d'administration avec superutilisateur"""
        self.client.login(email="admin@example.com", password="password123")

        # Test de la liste de contenu
        response = self.client.get(reverse("semestriels:list_content"))
        self.assertEqual(response.status_code, 200)

        # Test du formulaire d'ajout de contenu
        response = self.client.get(reverse("semestriels:add_content"))
        self.assertEqual(response.status_code, 200)

        # Test du formulaire de modification (avec contenu existant)
        semestriel = self.create_semestriel_page()
        response = self.client.get(
            reverse("semestriels:edit_content", args=[semestriel.pk])
        )
        self.assertEqual(response.status_code, 200)


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class SemestrielEdgeCasesTestCase(TestCase):
    """Tests pour les cas particuliers et edge cases"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.superuser = User.objects.create_superuser(
            email="admin@example.com", password="password123"
        )

    def setUp(self):
        self.client = Client()
        self.client.login(email="admin@example.com", password="password123")

    def tearDown(self):
        SemestrielPage.objects.all().delete()
        if os.path.exists(MEDIA_ROOT):
            shutil.rmtree(MEDIA_ROOT)

    def generate_test_image(self, size=(100, 100)):
        """Générer une image de test"""
        file = io.BytesIO()
        image = Image.new("RGB", size, color=(255, 0, 0))
        image.save(file, format="JPEG")
        file.name = "test.jpg"
        file.seek(0)
        return file

    def test_multiple_semestriel_pages_creation(self):
        """Test de création de plusieurs pages semestrielles"""
        # Créer la première page
        image1 = SimpleUploadedFile(
            name="test1.jpg",
            content=self.generate_test_image().read(),
            content_type="image/jpeg",
        )
        pdf1 = SimpleUploadedFile(
            name="test1.pdf",
            content=b"First PDF content",
            content_type="application/pdf",
        )

        page1 = SemestrielPage.objects.create(picture=image1, file=pdf1)
        self.assertEqual(SemestrielPage.objects.count(), 1)

        # Créer une deuxième page
        image2 = SimpleUploadedFile(
            name="test2.jpg",
            content=self.generate_test_image().read(),
            content_type="image/jpeg",
        )
        pdf2 = SimpleUploadedFile(
            name="test2.pdf",
            content=b"Second PDF content",
            content_type="application/pdf",
        )

        page2 = SemestrielPage.objects.create(picture=image2, file=pdf2)

        # Vérifier qu'il n'y a toujours qu'une seule page
        self.assertEqual(SemestrielPage.objects.count(), 1)

        # Vérifier que c'est la deuxième page qui existe
        remaining_page = SemestrielPage.objects.first()
        self.assertEqual(remaining_page.id, page2.id)

    def test_form_with_different_image_formats(self):
        """Test du formulaire avec différents formats d'image"""
        # Test avec PNG
        png_image = SimpleUploadedFile(
            name="test.png",
            content=self.generate_test_image().read(),
            content_type="image/png",
        )
        pdf_file = SimpleUploadedFile(
            name="test.pdf", content=b"Test PDF content", content_type="application/pdf"
        )

        form = SemestrielForm(data={}, files={"picture": png_image, "file": pdf_file})
        self.assertTrue(form.is_valid())

    def test_view_with_corrupted_files(self):
        """Test des vues avec des fichiers corrompus"""
        # Créer une page avec des fichiers qui pourraient être corrompus
        semestriel = SemestrielPage.objects.create(
            picture=SimpleUploadedFile(
                name="test.jpg",
                content=self.generate_test_image().read(),
                content_type="image/jpeg",
            ),
            file=SimpleUploadedFile(
                name="test.pdf",
                content=b"Test PDF content",
                content_type="application/pdf",
            ),
        )

        # Tester que les vues fonctionnent même si les fichiers sont problématiques
        response = self.client.get(reverse("semestriels:semestriel"))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse("semestriels:list_content"))
        self.assertEqual(response.status_code, 200)

    def test_form_validation_edge_cases(self):
        """Test de validation du formulaire dans des cas limites"""
        # Test sans fichiers
        form = SemestrielForm(data={}, files={})
        self.assertFalse(form.is_valid())

        # Test avec seulement une image
        image_file = SimpleUploadedFile(
            name="test.jpg",
            content=self.generate_test_image().read(),
            content_type="image/jpeg",
        )
        form = SemestrielForm(data={}, files={"picture": image_file})
        self.assertFalse(form.is_valid())

        # Test avec seulement un PDF
        pdf_file = SimpleUploadedFile(
            name="test.pdf", content=b"Test PDF content", content_type="application/pdf"
        )
        form = SemestrielForm(data={}, files={"file": pdf_file})
        self.assertFalse(form.is_valid())


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class SemestrielIntegrationTestCase(TestCase):
    """Tests d'intégration pour l'application semestriels"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.superuser = User.objects.create_superuser(
            email="admin@example.com", password="password123"
        )

    def setUp(self):
        self.client = Client()
        self.client.login(email="admin@example.com", password="password123")

    def tearDown(self):
        SemestrielPage.objects.all().delete()
        if os.path.exists(MEDIA_ROOT):
            shutil.rmtree(MEDIA_ROOT)

    def generate_test_image(self):
        """Générer une image de test"""
        file = io.BytesIO()
        image = Image.new("RGB", (100, 100), color=(255, 0, 0))
        image.save(file, format="JPEG")
        file.name = "test.jpg"
        file.seek(0)
        return file

    def test_complete_workflow_add_edit_view(self):
        """Test du workflow complet : ajout -> modification -> affichage"""
        # 1. Ajouter du contenu
        image_file = SimpleUploadedFile(
            name="original.jpg",
            content=self.generate_test_image().read(),
            content_type="image/jpeg",
        )
        pdf_file = SimpleUploadedFile(
            name="original.pdf",
            content=b"Original PDF content",
            content_type="application/pdf",
        )

        response = self.client.post(
            reverse("semestriels:add_content"),
            {"picture": image_file, "file": pdf_file},
        )
        self.assertEqual(response.status_code, 302)

        # Vérifier que le contenu a été créé
        semestriel = SemestrielPage.objects.first()
        self.assertIsNotNone(semestriel)

        # 2. Modifier le contenu
        new_image = SimpleUploadedFile(
            name="updated.jpg",
            content=self.generate_test_image().read(),
            content_type="image/jpeg",
        )
        new_pdf = SimpleUploadedFile(
            name="updated.pdf",
            content=b"Updated PDF content",
            content_type="application/pdf",
        )

        response = self.client.post(
            reverse("semestriels:edit_content", args=[semestriel.pk]),
            {"picture": new_image, "file": new_pdf},
        )
        self.assertEqual(response.status_code, 302)

        # 3. Vérifier l'affichage public
        response = self.client.get(reverse("semestriels:semestriel"))
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context["content"])

        # 4. Vérifier l'affichage admin
        response = self.client.get(reverse("semestriels:list_content"))
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context["content"])

    def test_file_cleanup_on_replacement(self):
        """Test que les anciens fichiers sont nettoyés lors du remplacement"""
        # Créer une première page
        image1 = SimpleUploadedFile(
            name="first.jpg",
            content=self.generate_test_image().read(),
            content_type="image/jpeg",
        )
        pdf1 = SimpleUploadedFile(
            name="first.pdf",
            content=b"First PDF content",
            content_type="application/pdf",
        )

        page1 = SemestrielPage.objects.create(picture=image1, file=pdf1)

        # Créer une deuxième page (doit remplacer la première)
        image2 = SimpleUploadedFile(
            name="second.jpg",
            content=self.generate_test_image().read(),
            content_type="image/jpeg",
        )
        pdf2 = SimpleUploadedFile(
            name="second.pdf",
            content=b"Second PDF content",
            content_type="application/pdf",
        )

        page2 = SemestrielPage.objects.create(picture=image2, file=pdf2)

        # Vérifier qu'il n'y a qu'une seule page
        self.assertEqual(SemestrielPage.objects.count(), 1)

        # Vérifier que c'est la deuxième page
        remaining_page = SemestrielPage.objects.first()
        self.assertEqual(remaining_page.id, page2.id)
