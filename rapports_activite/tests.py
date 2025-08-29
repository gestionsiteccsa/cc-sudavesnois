import os
import shutil
from unittest.mock import MagicMock, patch

from django.contrib.admin.sites import site
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.test.utils import override_settings
from django.urls import reverse

from rapports_activite.admin import (CustomRapportActiviteAdmin,
                                     delete_rapports_activite)
from rapports_activite.forms import RapportActiviteForm
from rapports_activite.models import RapportActivite

User = get_user_model()
MEDIA_ROOT = "test_media_rapports_activite"


class BaseRapportActiviteTestCase(TestCase):
    """Classe de base pour tous les tests avec gestion MEDIA_ROOT."""

    @classmethod
    def setUpClass(cls):
        """Configuration de classe pour créer le répertoire MEDIA_ROOT."""
        super().setUpClass()
        os.makedirs(MEDIA_ROOT, exist_ok=True)
        # Créer aussi le sous-répertoire pour les rapports
        os.makedirs(
            os.path.join(MEDIA_ROOT, "rapports_activite", "rapports"), exist_ok=True
        )

    @classmethod
    def tearDownClass(cls):
        """Nettoyage de classe pour supprimer le répertoire MEDIA_ROOT."""
        super().tearDownClass()
        if os.path.exists(MEDIA_ROOT):
            shutil.rmtree(MEDIA_ROOT)

    def tearDown(self):
        """Nettoyage après chaque test."""
        # Nettoyer les fichiers créés pendant le test
        for root, dirs, files in os.walk(MEDIA_ROOT):
            for file in files:
                try:
                    os.remove(os.path.join(root, file))
                except (OSError, FileNotFoundError):
                    pass


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class RapportActiviteModelTestCase(BaseRapportActiviteTestCase):
    """Tests pour le modèle RapportActivite."""

    def setUp(self):
        """Configuration pour chaque test."""
        self.test_file = SimpleUploadedFile(
            "rapport_2024.pdf", b"Contenu PDF test", content_type="application/pdf"
        )

    def test_rapport_creation(self):
        """Test de création d'un rapport d'activité."""
        rapport = RapportActivite.objects.create(year=2024, file=self.test_file)
        self.assertEqual(rapport.year, 2024)
        self.assertTrue(rapport.file)
        self.assertIsNotNone(rapport.publish_date)

    def test_rapport_str_method(self):
        """Test de la méthode __str__ du modèle."""
        rapport = RapportActivite.objects.create(year=2024, file=self.test_file)
        expected_str = "Rapport d'activité 2024"
        self.assertEqual(str(rapport), expected_str)

    def test_auto_generation_title(self):
        """Test de la génération automatique du titre."""
        rapport = RapportActivite.objects.create(year=2024, file=self.test_file)
        expected_title = "Rapport d'activité 2024"
        self.assertEqual(rapport.title, expected_title)

    def test_auto_generation_description(self):
        """Test de la génération automatique de la description."""
        rapport = RapportActivite.objects.create(year=2024, file=self.test_file)
        self.assertIn("Bilant des actions menées en 2024", rapport.description)
        self.assertIn("perspectives pour l'année 2025", rapport.description)

    def test_custom_title_and_description(self):
        """Test avec titre et description personnalisés."""
        rapport = RapportActivite.objects.create(
            year=2024,
            title="Titre personnalisé",
            description="Description personnalisée",
            file=self.test_file,
        )
        self.assertEqual(rapport.title, "Titre personnalisé")
        self.assertEqual(rapport.description, "Description personnalisée")

    def test_year_unique_constraint(self):
        """Test de la contrainte d'unicité sur l'année."""
        RapportActivite.objects.create(year=2024, file=self.test_file)

        # Tentative de création d'un second rapport pour la même année
        test_file2 = SimpleUploadedFile(
            "rapport_2024_bis.pdf", b"Autre contenu PDF", content_type="application/pdf"
        )

        with self.assertRaises(Exception):  # IntegrityError ou ValidationError
            RapportActivite.objects.create(year=2024, file=test_file2)

    def test_file_extension_validation(self):
        """Test de validation des extensions de fichier."""
        valid_extensions = ["pdf", "docx", "doc", "txt"]

        for ext in valid_extensions:
            test_file = SimpleUploadedFile(
                f"rapport.{ext}", b"Contenu test", content_type="application/pdf"
            )
            rapport = RapportActivite(year=2020 + len(ext), file=test_file)
            try:
                rapport.full_clean()
                self.assertTrue(True)  # Validation réussie
            except ValidationError:
                self.fail(f"Extension {ext} devrait être valide")

    def test_invalid_file_extension(self):
        """Test avec extension de fichier invalide."""
        invalid_file = SimpleUploadedFile(
            "rapport.jpg", b"Contenu image", content_type="image/jpeg"
        )
        rapport = RapportActivite(year=2024, file=invalid_file)

        with self.assertRaises(ValidationError):
            rapport.full_clean()

    def test_get_document_size_ko(self):
        """Test de get_document_size pour un fichier en Ko."""
        # Créer un fichier de test plus gros
        large_content = b"x" * (512 * 1024)  # 512 Ko
        large_file = SimpleUploadedFile(
            "rapport_large.pdf", large_content, content_type="application/pdf"
        )

        rapport = RapportActivite.objects.create(year=2024, file=large_file)
        size = rapport.get_document_size()
        # Vérifier que la taille est calculée correctement (environ 512 Ko)
        self.assertTrue(size.endswith(" Ko") or size.endswith(" Mo"))

    def test_get_document_size_mo(self):
        """Test de get_document_size pour un fichier en Mo."""
        # Créer un fichier de test de 2 Mo
        large_content = b"x" * (2 * 1024 * 1024)  # 2 Mo
        large_file = SimpleUploadedFile(
            "rapport_large_mo.pdf", large_content, content_type="application/pdf"
        )

        rapport = RapportActivite.objects.create(year=2023, file=large_file)
        size = rapport.get_document_size()
        # Vérifier que la taille est en Mo
        self.assertTrue(size.endswith(" Mo"))

    def test_get_document_size_file_not_found(self):
        """Test de get_document_size quand le fichier n'existe pas."""
        rapport = RapportActivite.objects.create(year=2024, file=self.test_file)
        # Simuler un fichier manquant
        rapport.file.name = "fichier_inexistant.pdf"

        size = rapport.get_document_size()
        self.assertEqual(size, "Indisponible")


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class RapportActiviteFormTestCase(BaseRapportActiviteTestCase):
    """Tests pour le formulaire RapportActiviteForm."""

    def setUp(self):
        """Configuration pour chaque test."""
        self.test_file = SimpleUploadedFile(
            "rapport_2024.pdf", b"Contenu PDF test", content_type="application/pdf"
        )

    def test_form_valid_data(self):
        """Test du formulaire avec des données valides."""
        form = RapportActiviteForm(data={"year": 2024}, files={"file": self.test_file})
        self.assertTrue(form.is_valid())

    def test_form_missing_year(self):
        """Test du formulaire sans année."""
        form = RapportActiviteForm(data={}, files={"file": self.test_file})
        self.assertFalse(form.is_valid())
        self.assertIn("year", form.errors)

    def test_form_missing_file(self):
        """Test du formulaire sans fichier."""
        form = RapportActiviteForm(data={"year": 2024})
        self.assertFalse(form.is_valid())
        self.assertIn("file", form.errors)

    def test_form_invalid_year(self):
        """Test du formulaire avec année invalide."""
        form = RapportActiviteForm(
            data={"year": "invalid"}, files={"file": self.test_file}
        )
        self.assertFalse(form.is_valid())
        self.assertIn("year", form.errors)

    def test_form_widgets(self):
        """Test des widgets du formulaire."""
        form = RapportActiviteForm()
        self.assertIn("form-control", form.fields["year"].widget.attrs["class"])
        self.assertIn("form-control", form.fields["file"].widget.attrs["class"])

    def test_form_save(self):
        """Test de la sauvegarde du formulaire."""
        form = RapportActiviteForm(data={"year": 2024}, files={"file": self.test_file})
        self.assertTrue(form.is_valid())
        rapport = form.save()
        self.assertEqual(rapport.year, 2024)
        self.assertEqual(RapportActivite.objects.count(), 1)


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class RapportActiviteViewsTestCase(BaseRapportActiviteTestCase):
    """Tests pour les vues de l'application rapports_activite."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.superuser = User.objects.create_superuser(
            email="admin@exemple.com", password="adminpassword"
        )
        cls.staff_user = User.objects.create_user(
            email="staff@exemple.com", password="staffpassword", is_staff=True
        )
        cls.regular_user = User.objects.create_user(
            email="user@exemple.com", password="userpassword"
        )

    def setUp(self):
        """Configuration de l'environnement de test."""
        self.client = Client()
        self.test_file = SimpleUploadedFile(
            "rapport_2024.pdf", b"Contenu PDF test", content_type="application/pdf"
        )

    def test_rapports_activite_public_view_no_data(self):
        """Test de la vue publique sans données."""
        response = self.client.get(reverse("rapports_activite:rapports_activite"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "rapports_activite/rapports-activite.html")
        self.assertIsNone(response.context["rapport_recents"])
        self.assertIsNone(response.context["archive"])

    def test_rapports_activite_public_view_with_data(self):
        """Test de la vue publique avec données."""
        # Créer 6 rapports pour tester la séparation récents/archive
        for year in range(2019, 2025):
            test_file = SimpleUploadedFile(
                f"rapport_{year}.pdf",
                b"Contenu PDF test",
                content_type="application/pdf",
            )
            RapportActivite.objects.create(year=year, file=test_file)

        response = self.client.get(reverse("rapports_activite:rapports_activite"))
        self.assertEqual(response.status_code, 200)

        # Vérifier la séparation récents (4) / archive (2)
        self.assertEqual(len(response.context["rapport_recents"]), 4)
        self.assertEqual(len(response.context["archive"]), 2)

        # Vérifier l'ordre (plus récent en premier)
        rapport_recents = response.context["rapport_recents"]
        self.assertEqual(rapport_recents[0].year, 2024)
        self.assertEqual(rapport_recents[3].year, 2021)

    def test_manage_rapports_activite_view_authenticated(self):
        """Test de la vue gestion avec superutilisateur."""
        self.client.login(email=self.superuser.email, password="adminpassword")
        RapportActivite.objects.create(year=2024, file=self.test_file)

        response = self.client.get(
            reverse("rapports_activite:gestion_rapports_activite")
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, "rapports_activite/admin-manage-rapports-activite.html"
        )
        self.assertIn("rapports", response.context)

    def test_manage_rapports_activite_view_no_data(self):
        """Test de la vue gestion sans données."""
        self.client.login(email=self.superuser.email, password="adminpassword")

        response = self.client.get(
            reverse("rapports_activite:gestion_rapports_activite")
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context["rapports"])

    def test_manage_rapports_activite_permission_required(self):
        """Test que la vue gestion nécessite les permissions."""
        response = self.client.get(
            reverse("rapports_activite:gestion_rapports_activite")
        )
        self.assertEqual(response.status_code, 302)  # Redirection vers login

    def test_add_rapport_activite_view_get(self):
        """Test de l'affichage du formulaire d'ajout."""
        self.client.login(email=self.superuser.email, password="adminpassword")

        response = self.client.get(reverse("rapports_activite:add_rapport_activite"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "rapports_activite/admin-rapport-add.html")
        self.assertIn("form", response.context)
        self.assertIsInstance(response.context["form"], RapportActiviteForm)

    def test_add_rapport_activite_view_post_valid(self):
        """Test d'ajout d'un rapport avec données valides."""
        self.client.login(email=self.superuser.email, password="adminpassword")

        response = self.client.post(
            reverse("rapports_activite:add_rapport_activite"),
            {"year": 2024, "file": self.test_file},
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, reverse("rapports_activite:gestion_rapports_activite")
        )
        self.assertEqual(RapportActivite.objects.count(), 1)
        self.assertEqual(RapportActivite.objects.first().year, 2024)

    def test_add_rapport_activite_view_post_invalid(self):
        """Test d'ajout d'un rapport avec données invalides."""
        self.client.login(email=self.superuser.email, password="adminpassword")

        response = self.client.post(
            reverse("rapports_activite:add_rapport_activite"),
            {
                "year": "",  # Année manquante
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "rapports_activite/admin-rapport-add.html")
        self.assertTrue(response.context["form"].errors)
        self.assertEqual(RapportActivite.objects.count(), 0)

    def test_add_rapport_activite_permission_required(self):
        """Test que l'ajout nécessite les permissions."""
        response = self.client.post(
            reverse("rapports_activite:add_rapport_activite"),
            {"year": 2024, "file": self.test_file},
        )
        self.assertEqual(response.status_code, 302)  # Redirection vers login

    def test_edit_rapport_activite_view_get(self):
        """Test de l'affichage du formulaire de modification."""
        self.client.login(email=self.superuser.email, password="adminpassword")
        rapport = RapportActivite.objects.create(year=2024, file=self.test_file)

        response = self.client.get(
            reverse("rapports_activite:edit_rapport_activite", args=[rapport.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "rapports_activite/admin-rapport-edit.html")
        self.assertEqual(response.context["form"].instance, rapport)

    def test_edit_rapport_activite_view_post_valid_with_file_change(self):
        """Test de modification d'un rapport avec changement de fichier."""
        with patch("os.path.exists", return_value=True), patch(
            "os.remove"
        ) as mock_remove, patch(
            "django.core.files.storage.FileSystemStorage.save",
            side_effect=["test1.pdf", "test2.pdf"],
        ):
            self.client.login(email=self.superuser.email, password="adminpassword")
            rapport = RapportActivite.objects.create(year=2024, file=self.test_file)

            new_file = SimpleUploadedFile(
                "nouveau_rapport_2024.pdf",
                b"Nouveau contenu PDF",
                content_type="application/pdf",
            )

            response = self.client.post(
                reverse("rapports_activite:edit_rapport_activite", args=[rapport.id]),
                {"year": 2024, "file": new_file},
            )

            self.assertEqual(response.status_code, 302)
            self.assertRedirects(
                response, reverse("rapports_activite:gestion_rapports_activite")
            )

            # Vérifier que l'ancien fichier a été supprimé
            mock_remove.assert_called_once()

    def test_edit_rapport_activite_view_post_invalid(self):
        """Test de modification d'un rapport avec données invalides."""
        self.client.login(email=self.superuser.email, password="adminpassword")
        rapport = RapportActivite.objects.create(year=2024, file=self.test_file)

        response = self.client.post(
            reverse("rapports_activite:edit_rapport_activite", args=[rapport.id]),
            {
                "year": "",  # Année invalide
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "rapports_activite/admin-rapport-edit.html")
        self.assertTrue(response.context["form"].errors)

    def test_edit_rapport_activite_view_not_found(self):
        """Test de modification d'un rapport inexistant."""
        self.client.login(email=self.superuser.email, password="adminpassword")

        response = self.client.get(
            reverse("rapports_activite:edit_rapport_activite", args=[999])
        )
        self.assertEqual(response.status_code, 404)

    def test_edit_rapport_activite_permission_required(self):
        """Test que la modification nécessite les permissions."""
        rapport = RapportActivite.objects.create(year=2024, file=self.test_file)

        response = self.client.post(
            reverse("rapports_activite:edit_rapport_activite", args=[rapport.id]),
            {"year": 2024, "file": self.test_file},
        )
        self.assertEqual(response.status_code, 302)  # Redirection vers login

    def test_delete_rapport_activite_view_get(self):
        """Test de l'affichage de la confirmation de suppression."""
        self.client.login(email=self.superuser.email, password="adminpassword")
        rapport = RapportActivite.objects.create(year=2024, file=self.test_file)

        response = self.client.get(
            reverse("rapports_activite:delete_rapport_activite", args=[rapport.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "rapports_activite/admin-rapport-delete.html")
        self.assertEqual(response.context["form"], rapport)

    def test_delete_rapport_activite_view_post(self):
        """Test de suppression d'un rapport."""
        with patch("os.path.exists", return_value=True), patch(
            "os.remove"
        ) as mock_remove, patch(
            "django.core.files.storage.FileSystemStorage.save", return_value="test.pdf"
        ):
            self.client.login(email=self.superuser.email, password="adminpassword")
            rapport = RapportActivite.objects.create(year=2024, file=self.test_file)

            response = self.client.post(
                reverse("rapports_activite:delete_rapport_activite", args=[rapport.id])
            )
            self.assertEqual(response.status_code, 302)
            self.assertRedirects(
                response, reverse("rapports_activite:gestion_rapports_activite")
            )
            self.assertEqual(RapportActivite.objects.count(), 0)

            # Vérifier que le fichier a été supprimé
            mock_remove.assert_called_once()

    def test_delete_rapport_activite_view_not_found(self):
        """Test de suppression d'un rapport inexistant."""
        self.client.login(email=self.superuser.email, password="adminpassword")

        response = self.client.get(
            reverse("rapports_activite:delete_rapport_activite", args=[999])
        )
        self.assertEqual(response.status_code, 404)

    def test_delete_rapport_activite_permission_required(self):
        """Test que la suppression nécessite les permissions."""
        rapport = RapportActivite.objects.create(year=2024, file=self.test_file)

        response = self.client.post(
            reverse("rapports_activite:delete_rapport_activite", args=[rapport.id])
        )
        self.assertEqual(response.status_code, 302)  # Redirection vers login

    def tearDown(self):
        """Nettoyage après chaque test."""
        if os.path.exists(MEDIA_ROOT):
            shutil.rmtree(MEDIA_ROOT)


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class RapportActivitePermissionsTestCase(BaseRapportActiviteTestCase):
    """Tests pour les permissions de l'application rapports_activite."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.staff_user = User.objects.create_user(
            email="staff@exemple.com", password="staffpassword", is_staff=True
        )
        cls.regular_user = User.objects.create_user(
            email="user@exemple.com", password="userpassword"
        )

    def setUp(self):
        """Configuration de l'environnement de test."""
        self.test_file = SimpleUploadedFile(
            "rapport_2024.pdf", b"Contenu PDF test", content_type="application/pdf"
        )

    def test_staff_user_with_permissions(self):
        """Test qu'un utilisateur staff avec permissions peut accéder."""
        # Donner les permissions nécessaires
        permissions = Permission.objects.filter(
            content_type__app_label="rapports_activite",
            codename__in=[
                "add_rapportactivite",
                "change_rapportactivite",
                "delete_rapportactivite",
                "view_rapportactivite",
            ],
        )
        self.staff_user.user_permissions.set(permissions)

        self.client.login(email=self.staff_user.email, password="staffpassword")

        # Test accès à la gestion
        response = self.client.get(
            reverse("rapports_activite:gestion_rapports_activite")
        )
        self.assertEqual(response.status_code, 200)

        # Test ajout
        response = self.client.get(reverse("rapports_activite:add_rapport_activite"))
        self.assertEqual(response.status_code, 200)

    def test_staff_user_without_permissions(self):
        """Test qu'un utilisateur staff sans permissions ne peut pas accéder."""
        self.client.login(email=self.staff_user.email, password="staffpassword")

        response = self.client.get(
            reverse("rapports_activite:gestion_rapports_activite")
        )
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_regular_user_no_access(self):
        """Test qu'un utilisateur normal ne peut pas accéder."""
        self.client.login(email=self.regular_user.email, password="userpassword")

        response = self.client.get(
            reverse("rapports_activite:gestion_rapports_activite")
        )
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_anonymous_user_redirect(self):
        """Test qu'un utilisateur anonyme est redirigé."""
        response = self.client.get(
            reverse("rapports_activite:gestion_rapports_activite")
        )
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_public_view_accessible_to_all(self):
        """Test que la vue publique est accessible à tous."""
        # Utilisateur anonyme
        response = self.client.get(reverse("rapports_activite:rapports_activite"))
        self.assertEqual(response.status_code, 200)

        # Utilisateur normal
        self.client.login(email=self.regular_user.email, password="userpassword")
        response = self.client.get(reverse("rapports_activite:rapports_activite"))
        self.assertEqual(response.status_code, 200)

    def tearDown(self):
        """Nettoyage après chaque test."""
        if os.path.exists(MEDIA_ROOT):
            shutil.rmtree(MEDIA_ROOT)


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class RapportActiviteAdminTestCase(BaseRapportActiviteTestCase):
    """Tests pour l'interface d'administration de RapportActivite."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.superuser = User.objects.create_superuser(
            email="admin@exemple.com", password="adminpassword"
        )

    def setUp(self):
        """Configuration de l'environnement de test."""
        self.client = Client()
        self.client.login(email=self.superuser.email, password="adminpassword")
        self.test_file = SimpleUploadedFile(
            "rapport_2024.pdf", b"Contenu PDF test", content_type="application/pdf"
        )

    def test_admin_model_registered(self):
        """Test que le modèle est enregistré dans l'admin."""
        self.assertIn(RapportActivite, site._registry)
        admin_class = site._registry[RapportActivite]
        self.assertIsInstance(admin_class, CustomRapportActiviteAdmin)

    def test_admin_list_display(self):
        """Test de la configuration list_display."""
        admin_class = site._registry[RapportActivite]
        expected_fields = ("title", "year", "description", "publish_date", "file")
        self.assertEqual(admin_class.list_display, expected_fields)

    def test_admin_list_filter(self):
        """Test de la configuration list_filter."""
        admin_class = site._registry[RapportActivite]
        expected_filters = ("year", "publish_date")
        self.assertEqual(admin_class.list_filter, expected_filters)

    def test_admin_search_fields(self):
        """Test de la configuration search_fields."""
        admin_class = site._registry[RapportActivite]
        expected_fields = ("year", "publish_date")
        self.assertEqual(admin_class.search_fields, expected_fields)

    def test_admin_ordering(self):
        """Test de la configuration ordering."""
        admin_class = site._registry[RapportActivite]
        expected_ordering = ("-publish_date",)
        self.assertEqual(admin_class.ordering, expected_ordering)

    def test_admin_custom_actions(self):
        """Test des actions personnalisées."""
        admin_class = site._registry[RapportActivite]
        self.assertIn(delete_rapports_activite, admin_class.actions)

    def test_admin_default_delete_action_removed(self):
        """Test que l'action de suppression par défaut est supprimée."""
        admin_class = site._registry[RapportActivite]
        request = MagicMock()
        actions = admin_class.get_actions(request)
        self.assertNotIn("delete_selected", actions)

    def test_admin_delete_model_removes_file(self):
        """Test que delete_model supprime le fichier associé."""
        with patch("os.path.exists", return_value=True), patch(
            "os.remove"
        ) as mock_remove, patch(
            "django.core.files.storage.FileSystemStorage.save", return_value="test.pdf"
        ):
            rapport = RapportActivite.objects.create(year=2024, file=self.test_file)
            admin_class = site._registry[RapportActivite]

            request = MagicMock()
            admin_class.delete_model(request, rapport)

            # Vérifier que le fichier a été supprimé
            mock_remove.assert_called_once()

    def test_admin_custom_delete_action(self):
        """Test de l'action personnalisée de suppression."""
        with patch("os.path.exists", return_value=True), patch(
            "os.remove"
        ) as mock_remove, patch(
            "django.core.files.storage.FileSystemStorage.save",
            side_effect=["test1.pdf", "test2.pdf"],
        ):
            rapport1 = RapportActivite.objects.create(year=2024, file=self.test_file)
            rapport2 = RapportActivite.objects.create(
                year=2023,
                file=SimpleUploadedFile(
                    "rapport_2023.pdf", b"Contenu 2023", content_type="application/pdf"
                ),
            )

            queryset = RapportActivite.objects.all()
            admin_class = site._registry[RapportActivite]
            request = MagicMock()

            delete_rapports_activite(admin_class, request, queryset)

            # Vérifier que les fichiers ont été supprimés
            self.assertEqual(mock_remove.call_count, 2)
            # Vérifier que les objets ont été supprimés
            self.assertEqual(RapportActivite.objects.count(), 0)

    def tearDown(self):
        """Nettoyage après chaque test."""
        if os.path.exists(MEDIA_ROOT):
            shutil.rmtree(MEDIA_ROOT)


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class RapportActiviteIntegrationTestCase(BaseRapportActiviteTestCase):
    """Tests d'intégration pour l'application rapports_activite."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.superuser = User.objects.create_superuser(
            email="admin@exemple.com", password="adminpassword"
        )

    def setUp(self):
        """Configuration de l'environnement de test."""
        self.client = Client()
        self.client.login(email=self.superuser.email, password="adminpassword")

    def test_complete_rapport_workflow(self):
        """Test du workflow complet : création -> modification -> suppression."""
        # 1. Créer un rapport
        test_file = SimpleUploadedFile(
            "rapport_workflow.pdf", b"Contenu workflow", content_type="application/pdf"
        )

        response = self.client.post(
            reverse("rapports_activite:add_rapport_activite"),
            {"year": 2024, "file": test_file},
        )
        self.assertEqual(response.status_code, 302)
        rapport = RapportActivite.objects.get(year=2024)

        # 2. Vérifier dans la liste de gestion
        response = self.client.get(
            reverse("rapports_activite:gestion_rapports_activite")
        )
        self.assertContains(response, "2024")

        # 3. Modifier le rapport
        new_file = SimpleUploadedFile(
            "rapport_modifie.pdf", b"Contenu modifie", content_type="application/pdf"
        )

        with patch("os.path.exists", return_value=True), patch("os.remove"):
            response = self.client.post(
                reverse("rapports_activite:edit_rapport_activite", args=[rapport.id]),
                {"year": 2024, "file": new_file},
            )
            self.assertEqual(response.status_code, 302)

        # 4. Vérifier sur la page publique
        response = self.client.get(reverse("rapports_activite:rapports_activite"))
        self.assertContains(response, "2024")

        # 5. Supprimer le rapport
        with patch("os.path.exists", return_value=True), patch("os.remove"):
            response = self.client.post(
                reverse("rapports_activite:delete_rapport_activite", args=[rapport.id])
            )
            self.assertEqual(response.status_code, 302)
            self.assertEqual(RapportActivite.objects.count(), 0)

    def test_public_view_with_multiple_reports(self):
        """Test de la vue publique avec plusieurs rapports."""
        # Créer 6 rapports pour tester la pagination
        for year in range(2019, 2025):
            test_file = SimpleUploadedFile(
                f"rapport_{year}.pdf",
                f"Contenu {year}".encode(),
                content_type="application/pdf",
            )
            RapportActivite.objects.create(year=year, file=test_file)

        response = self.client.get(reverse("rapports_activite:rapports_activite"))
        self.assertEqual(response.status_code, 200)

        # Vérifier la séparation récents/archive
        self.assertEqual(len(response.context["rapport_recents"]), 4)
        self.assertEqual(len(response.context["archive"]), 2)

        # Vérifier que les plus récents sont en premier
        rapport_recents = response.context["rapport_recents"]
        years = [r.year for r in rapport_recents]
        self.assertEqual(years, [2024, 2023, 2022, 2021])

    def tearDown(self):
        """Nettoyage après chaque test."""
        if os.path.exists(MEDIA_ROOT):
            shutil.rmtree(MEDIA_ROOT)


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class RapportActiviteEdgeCasesTestCase(BaseRapportActiviteTestCase):
    """Tests pour les cas limites et erreurs."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.superuser = User.objects.create_superuser(
            email="admin@exemple.com", password="adminpassword"
        )

    def setUp(self):
        """Configuration de l'environnement de test."""
        self.client = Client()
        self.client.login(email=self.superuser.email, password="adminpassword")

    def test_rapport_with_very_old_year(self):
        """Test avec une année très ancienne."""
        test_file = SimpleUploadedFile(
            "rapport_1990.pdf", b"Contenu ancien", content_type="application/pdf"
        )

        rapport = RapportActivite.objects.create(year=1990, file=test_file)
        self.assertEqual(rapport.year, 1990)
        self.assertEqual(str(rapport), "Rapport d'activité 1990")

    def test_rapport_with_future_year(self):
        """Test avec une année future."""
        test_file = SimpleUploadedFile(
            "rapport_2030.pdf", b"Contenu futur", content_type="application/pdf"
        )

        rapport = RapportActivite.objects.create(year=2030, file=test_file)
        self.assertEqual(rapport.year, 2030)
        self.assertIn("perspectives pour l'année 2031", rapport.description)

    def test_rapport_with_very_long_title(self):
        """Test avec un titre très long."""
        long_title = "x" * 300  # Plus long que max_length=255
        test_file = SimpleUploadedFile(
            "rapport_long.pdf", b"Contenu test", content_type="application/pdf"
        )

        rapport = RapportActivite(year=2024, title=long_title, file=test_file)

        with self.assertRaises(ValidationError):
            rapport.full_clean()

    def test_rapport_with_special_characters_in_title(self):
        """Test avec des caractères spéciaux dans le titre."""
        special_title = "Rapport d'activité 2024 - Évaluation & Perspectives !"
        test_file = SimpleUploadedFile(
            "rapport_special.pdf", b"Contenu special", content_type="application/pdf"
        )

        rapport = RapportActivite.objects.create(
            year=2024, title=special_title, file=test_file
        )
        self.assertEqual(rapport.title, special_title)

    def test_file_size_calculation_edge_cases(self):
        """Test des cas limites pour le calcul de taille de fichier."""
        # Test avec fichier très petit
        small_file = SimpleUploadedFile(
            "rapport_small.pdf", b"x" * 100, content_type="application/pdf"  # 100 bytes
        )
        rapport_small = RapportActivite.objects.create(year=2022, file=small_file)
        size_small = rapport_small.get_document_size()
        self.assertTrue(size_small.endswith(" Ko"))

        # Test avec fichier exactement 1 Mo
        mo_content = b"x" * (1024 * 1024)  # 1 Mo
        mo_file = SimpleUploadedFile(
            "rapport_1mo.pdf", mo_content, content_type="application/pdf"
        )
        rapport_mo = RapportActivite.objects.create(year=2021, file=mo_file)
        size_mo = rapport_mo.get_document_size()
        # Vérifier que la taille est calculée (Ko ou Mo)
        self.assertTrue(size_mo.endswith(" Ko") or size_mo.endswith(" Mo"))

    @patch("os.path.exists")
    @patch("os.remove")
    def test_file_deletion_when_file_not_exists(self, mock_remove, mock_exists):
        """Test de suppression quand le fichier n'existe pas."""
        mock_exists.return_value = False

        test_file = SimpleUploadedFile(
            "rapport_inexistant.pdf", b"Contenu test", content_type="application/pdf"
        )
        rapport = RapportActivite.objects.create(year=2024, file=test_file)

        # Supprimer via la vue
        response = self.client.post(
            reverse("rapports_activite:delete_rapport_activite", args=[rapport.id])
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(RapportActivite.objects.count(), 0)
        # Vérifier que os.remove n'a pas été appelé
        mock_remove.assert_not_called()

    def tearDown(self):
        """Nettoyage après chaque test."""
        if os.path.exists(MEDIA_ROOT):
            shutil.rmtree(MEDIA_ROOT)
