import os
import shutil
from datetime import date, timedelta
from io import BytesIO
from unittest.mock import patch

from django.contrib.admin.sites import site
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile

TEST_IMAGE = SimpleUploadedFile(
    "test_image.jpg",
    b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.' ', #\x1c\x1c(7),\x014\x1b\x1f,5<,2\x1c\x1c\xff\xdb\x00C\x01\t\t\n\n\x18\r\r\x182\x1e\x1c\x1e2\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xc4\x00\xb5\x10\x00\x02\x01\x03\x03\x02\x04\x03\x05\x05\x04\x04\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x11\x04\x12!1A\x06\x13Qa\x07\"q\x142\x81\x91\xa1\x08#B\xb1\xc1\x15R\xd1\xf0$3br\x82\t\n\x16\x17\x18\x19\x1a%&'()*456789:CDEFGHIJSTUVWXYZcdefghijstuvwxyz\x83\x84\x85\x86\x87\x88\x89\x8a\x92\x93\x94\x95\x96\x97\x98\x99\x9a\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xff\xc4\x00\x1f\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xc4\x00\xb5\x11\x00\x02\x01\x02\x04\x04\x03\x04\x07\x05\x04\x04\x00\x01\x02\x03\x11\x04\x05!1\x06\x12AQ\x07aq\x13\"2\x81\x08\x14B\x91\xa1\xb1\xc1\t#3R\xf0\x15br\xd1\n\x16$4\xe1%\xf1\x17\x18\x19\x1a&'()*56789:CDEFGHIJSTUVWXYZcdefghijstuvwxyz\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x92\x93\x94\x95\x96\x97\x98\x99\x9a\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xff\xda\x00\x08\x01\x01\x00\x00?\x00\xf7\xd4\x00\x08",
    content_type="image/jpeg",
)
from django.test import Client, TestCase
from django.test.utils import override_settings
from django.urls import reverse

from communes_membres.admin import CustomCommuneMAdmin
from communes_membres.forms import ActesLocForm
from communes_membres.models import ActeLocal
from communes_membres.services import CommuneListingService
from conseil_communautaire.models import ConseilVille

User = get_user_model()
MEDIA_ROOT = "test_media_communes_membres"


class BaseCommunesMembresTestCase(TestCase):
    """Classe de base pour tous les tests avec gestion MEDIA_ROOT."""

    @classmethod
    def setUpClass(cls):
        """Configuration de classe pour créer le répertoire MEDIA_ROOT."""
        super().setUpClass()
        os.makedirs(MEDIA_ROOT, exist_ok=True)
        # Créer aussi le sous-répertoire pour les actes
        os.makedirs(os.path.join(MEDIA_ROOT, "communes", "actes_locaux"), exist_ok=True)

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
                except Exception:
                    pass


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class ActeLocalModelTestCase(BaseCommunesMembresTestCase):
    """Tests pour le modèle ActeLocal."""

    def setUp(self):
        """Configuration de l'environnement de test."""
        self.commune = ConseilVille.objects.create(
            city_name="Test Commune",
            mayor_sex="M",
            mayor_first_name="Jean",
            mayor_last_name="Dupont",
            address="123 Rue de la République",
            postal_code="75001",
            phone_number="0123456789",
            website="http://www.testcommune.fr",
            slogan="Slogan de la commune",
            nb_habitants=1000,
            image=TEST_IMAGE,
        )

        self.test_file = SimpleUploadedFile(
            "acte_test.pdf", b"Contenu PDF test", content_type="application/pdf"
        )

    def test_acte_local_creation(self):
        """Test de création d'un acte local."""
        acte = ActeLocal.objects.create(
            title="Délibération test",
            date=date.today(),
            description="Description de test",
            commune=self.commune,
            file=self.test_file,
        )

        self.assertEqual(acte.title, "Délibération test")
        self.assertEqual(acte.commune, self.commune)
        self.assertEqual(ActeLocal.objects.count(), 1)

    def test_acte_local_str_method(self):
        """Test de la méthode __str__ du modèle."""
        acte = ActeLocal.objects.create(
            title="Délibération test",
            date=date(2024, 1, 15),
            description="Description de test",
            commune=self.commune,
            file=self.test_file,
        )

        expected_str = f"Acte local du 2024-01-15 pour {self.commune.city_name}"
        self.assertEqual(str(acte), expected_str)

    def test_commune_one_to_one_constraint(self):
        """Test de la contrainte OneToOne avec la commune."""
        # Créer un premier acte
        ActeLocal.objects.create(
            title="Premier acte",
            date=date.today(),
            description="Description 1",
            commune=self.commune,
            file=self.test_file,
        )

        # Tentative de créer un second acte pour la même commune
        with self.assertRaises(Exception):
            ActeLocal.objects.create(
                title="Second acte",
                date=date.today(),
                description="Description 2",
                commune=self.commune,
                file=SimpleUploadedFile(
                    "acte_test2.pdf",
                    b"Contenu PDF test 2",
                    content_type="application/pdf",
                ),
            )

    def test_file_extension_validation(self):
        """Test de validation des extensions de fichier."""
        with self.assertRaises(ValidationError):
            acte = ActeLocal(
                title="Test acte",
                date=date.today(),
                description="Description test",
                commune=self.commune,
                file=SimpleUploadedFile(
                    "acte_test.txt", b"Contenu texte", content_type="text/plain"
                ),
            )
            acte.full_clean()

    def test_required_fields(self):
        """Test des champs obligatoires."""
        # Test sans titre
        with self.assertRaises(ValidationError):
            acte = ActeLocal(
                date=date.today(),
                description="Description test",
                commune=self.commune,
                file=self.test_file,
            )
            acte.full_clean()

        # Test sans date
        with self.assertRaises(ValidationError):
            acte = ActeLocal(
                title="Test acte",
                description="Description test",
                commune=self.commune,
                file=self.test_file,
            )
            acte.full_clean()

    def test_post_delete_signal(self):
        """Test du signal post_delete qui supprime le fichier."""
        with patch(
            "django.core.files.storage.FileSystemStorage.save", return_value="test.pdf"
        ), patch("django.core.files.storage.FileSystemStorage.delete") as mock_delete:
            acte = ActeLocal.objects.create(
                title="Test acte",
                date=date.today(),
                description="Description test",
                commune=self.commune,
                file=self.test_file,
            )

            # Supprimer l'acte
            acte.delete()

            # Vérifier que le fichier a été supprimé
            mock_delete.assert_called_once()


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class ActesLocFormTestCase(BaseCommunesMembresTestCase):
    """Tests pour le formulaire ActesLocForm."""

    def setUp(self):
        """Configuration de l'environnement de test."""
        self.commune = ConseilVille.objects.create(
            city_name="Test Commune",
            mayor_sex="M",
            mayor_first_name="Jean",
            mayor_last_name="Dupont",
            address="123 Rue de la République",
            postal_code="75001",
            phone_number="0123456789",
            website="http://www.testcommune.fr",
            slogan="Slogan de la commune",
            nb_habitants=1000,
        )

        self.test_file = SimpleUploadedFile(
            "acte_test.pdf", b"Contenu PDF test", content_type="application/pdf"
        )

    def test_form_valid_data(self):
        """Test du formulaire avec des données valides."""
        form_data = {
            "title": "Délibération test",
            "date": date.today(),
            "description": "Description de test",
            "commune": self.commune.id,
        }
        form = ActesLocForm(data=form_data, files={"file": self.test_file})
        self.assertTrue(form.is_valid())

    def test_form_missing_title(self):
        """Test du formulaire sans titre."""
        form_data = {
            "date": date.today(),
            "description": "Description de test",
            "commune": self.commune.id,
        }
        form = ActesLocForm(data=form_data, files={"file": self.test_file})
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)

    def test_form_missing_file(self):
        """Test du formulaire sans fichier."""
        form_data = {
            "title": "Délibération test",
            "date": date.today(),
            "description": "Description de test",
            "commune": self.commune.id,
        }
        form = ActesLocForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("file", form.errors)

    def test_form_widgets(self):
        """Test des widgets du formulaire."""
        form = ActesLocForm()

        # Vérifier les widgets personnalisés
        self.assertEqual(form.fields["date"].widget.input_type, "date")
        self.assertIn("placeholder", form.fields["title"].widget.attrs)
        self.assertIn("rows", form.fields["description"].widget.attrs)

    def test_form_labels(self):
        """Test des labels du formulaire."""
        form = ActesLocForm()

        self.assertEqual(form.fields["title"].label, "Titre de l'acte")
        self.assertEqual(form.fields["date"].label, "Date de l'acte")
        self.assertEqual(form.fields["description"].label, "Description de l'acte")
        self.assertEqual(form.fields["commune"].label, "Commune concernée")

    def test_form_save(self):
        """Test de la sauvegarde du formulaire."""
        form_data = {
            "title": "Délibération test",
            "date": date.today(),
            "description": "Description de test",
            "commune": self.commune.id,
        }

        with patch(
            "django.core.files.storage.FileSystemStorage.save", return_value="test.pdf"
        ):
            form = ActesLocForm(data=form_data, files={"file": self.test_file})
            self.assertTrue(form.is_valid())

            acte = form.save()
            self.assertEqual(acte.title, "Délibération test")
            self.assertEqual(acte.commune, self.commune)


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class CommunesMembresViewsTestCase(BaseCommunesMembresTestCase):
    """Tests pour les vues de l'application communes_membres."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.superuser = User.objects.create_superuser(
            email="admin@exemple.com", password="adminpassword"
        )

        # Créer un utilisateur staff avec permissions
        cls.staff_user = User.objects.create_user(
            email="staff@exemple.com", password="staffpassword", is_staff=True
        )

        # Ajouter les permissions nécessaires
        permissions = [
            "add_actelocal",
            "change_actelocal",
            "delete_actelocal",
            "view_actelocal",
        ]
        for perm_name in permissions:
            try:
                permission = Permission.objects.get(codename=perm_name)
                cls.staff_user.user_permissions.add(permission)
            except Permission.DoesNotExist:
                pass

    def setUp(self):
        """Configuration de l'environnement de test."""
        self.client = Client()

        self.commune = ConseilVille.objects.create(
            city_name="Test Commune",
            mayor_sex="M",
            mayor_first_name="Jean",
            mayor_last_name="Dupont",
            address="123 Rue de la République",
            postal_code="75001",
            phone_number="0123456789",
            website="http://www.testcommune.fr",
            slogan="Slogan de la commune",
            nb_habitants=1000,
            image=TEST_IMAGE,
        )

        self.test_file = SimpleUploadedFile(
            "acte_test.pdf", b"Contenu PDF test", content_type="application/pdf"
        )

    def test_commune_view_with_acte(self):
        """Test de la vue commune avec un acte local."""
        with patch(
            "django.core.files.storage.FileSystemStorage.save", return_value="test.pdf"
        ):
            acte = ActeLocal.objects.create(
                title="Délibération test",
                date=date.today(),
                description="Description de test",
                commune=self.commune,
                file=self.test_file,
            )

        response = self.client.get(
            reverse("communes-membres:commune", args=[self.commune.slug])
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "communes_membres/commune.html")
        self.assertEqual(response.context["commune"], self.commune)
        self.assertEqual(response.context["acte"], acte)

    def test_commune_view_without_acte(self):
        """Test de la vue commune sans acte local."""
        response = self.client.get(
            reverse("communes-membres:commune", args=[self.commune.slug])
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "communes_membres/commune.html")
        self.assertEqual(response.context["commune"], self.commune)

        # Vérifier qu'un acte fictif est créé
        acte = response.context["acte"]
        self.assertEqual(acte.id, "0")
        self.assertIsNone(acte.title)

    def test_commune_view_nonexistent_commune(self):
        """Test de la vue commune avec slug inexistant."""
        response = self.client.get(
            reverse("communes-membres:commune", args=["inexistant"])
        )

        self.assertEqual(response.status_code, 404)

    def test_add_acte_local_view_get(self):
        """Test de l'affichage du formulaire d'ajout."""
        self.client.login(email=self.superuser.email, password="adminpassword")

        response = self.client.get(reverse("communes-membres:admin_acte_add"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "communes_membres/admin_acte_add.html")
        self.assertIn("form_acte", response.context)

    def test_add_acte_local_view_post_valid(self):
        """Test d'ajout d'un acte local avec données valides."""
        self.client.login(email=self.superuser.email, password="adminpassword")

        with patch(
            "django.core.files.storage.FileSystemStorage.save", return_value="test.pdf"
        ):
            response = self.client.post(
                reverse("communes-membres:admin_acte_add"),
                {
                    "title": "Délibération test",
                    "date": date.today(),
                    "description": "Description de test",
                    "commune": self.commune.id,
                    "file": self.test_file,
                },
            )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("communes-membres:admin_acte_list"))
        self.assertTrue(ActeLocal.objects.filter(title="Délibération test").exists())

    def test_add_acte_local_view_post_invalid(self):
        """Test d'ajout d'un acte local avec données invalides."""
        self.client.login(email=self.superuser.email, password="adminpassword")

        response = self.client.post(
            reverse("communes-membres:admin_acte_add"),
            {
                "title": "",  # Titre manquant
                "date": date.today(),
                "description": "Description de test",
                "commune": self.commune.id,
                "file": self.test_file,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "communes_membres/admin_acte_add.html")
        self.assertFalse(
            ActeLocal.objects.filter(description="Description de test").exists()
        )

    def test_list_acte_local_view_with_data(self):
        """Test de la vue liste avec des actes locaux."""
        self.client.login(email=self.superuser.email, password="adminpassword")

        with patch(
            "django.core.files.storage.FileSystemStorage.save", return_value="test.pdf"
        ):
            ActeLocal.objects.create(
                title="Délibération test",
                date=date.today(),
                description="Description de test",
                commune=self.commune,
                file=self.test_file,
            )

        response = self.client.get(reverse("communes-membres:admin_acte_list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "communes_membres/admin_acte_list.html")
        self.assertContains(response, "Délibération test")

    def test_list_acte_local_view_no_data(self):
        """Test de la vue liste sans actes locaux."""
        self.client.login(email=self.superuser.email, password="adminpassword")

        response = self.client.get(reverse("communes-membres:admin_acte_list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "communes_membres/admin_acte_list.html")

        # Vérifier qu'un acte fictif est présent
        actes = response.context["actes_locaux"]
        self.assertEqual(len(actes), 1)
        self.assertEqual(actes[0].id, "-1")

    def test_update_acte_local_view_get(self):
        """Test de l'affichage du formulaire de modification."""
        self.client.login(email=self.superuser.email, password="adminpassword")

        with patch(
            "django.core.files.storage.FileSystemStorage.save", return_value="test.pdf"
        ):
            acte = ActeLocal.objects.create(
                title="Délibération test",
                date=date.today(),
                description="Description de test",
                commune=self.commune,
                file=self.test_file,
            )

        response = self.client.get(
            reverse("communes-membres:admin_acte_update", args=[acte.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "communes_membres/admin_acte_edit.html")
        self.assertEqual(response.context["form_acte"].instance, acte)

    def test_update_acte_local_view_post_valid(self):
        """Test de modification d'un acte local avec données valides."""
        self.client.login(email=self.superuser.email, password="adminpassword")

        with patch(
            "django.core.files.storage.FileSystemStorage.save", return_value="test.pdf"
        ):
            acte = ActeLocal.objects.create(
                title="Délibération test",
                date=date.today(),
                description="Description de test",
                commune=self.commune,
                file=self.test_file,
            )

        with patch(
            "django.core.files.storage.FileSystemStorage.save",
            return_value="test_updated.pdf",
        ), patch("os.path.exists", return_value=True), patch("os.remove"):
            response = self.client.post(
                reverse("communes-membres:admin_acte_update", args=[acte.id]),
                {
                    "title": "Délibération modifiée",
                    "date": date.today(),
                    "description": "Description modifiée",
                    "commune": self.commune.id,
                    "file": SimpleUploadedFile(
                        "acte_modifie.pdf",
                        b"Contenu PDF modifie",
                        content_type="application/pdf",
                    ),
                },
            )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("communes-membres:admin_acte_list"))

        acte.refresh_from_db()
        self.assertEqual(acte.title, "Délibération modifiée")

    def test_delete_acte_local_view_get(self):
        """Test de l'affichage de la confirmation de suppression."""
        self.client.login(email=self.superuser.email, password="adminpassword")

        with patch(
            "django.core.files.storage.FileSystemStorage.save", return_value="test.pdf"
        ):
            acte = ActeLocal.objects.create(
                title="Délibération test",
                date=date.today(),
                description="Description de test",
                commune=self.commune,
                file=self.test_file,
            )

        response = self.client.get(
            reverse("communes-membres:admin_acte_delete", args=[acte.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "communes_membres/admin_acte_delete.html")
        self.assertEqual(response.context["acte_local"], acte)

    def test_delete_acte_local_view_post(self):
        """Test de suppression d'un acte local."""
        self.client.login(email=self.superuser.email, password="adminpassword")

        with patch(
            "django.core.files.storage.FileSystemStorage.save", return_value="test.pdf"
        ):
            acte = ActeLocal.objects.create(
                title="Délibération test",
                date=date.today(),
                description="Description de test",
                commune=self.commune,
                file=self.test_file,
            )

        response = self.client.post(
            reverse("communes-membres:admin_acte_delete", args=[acte.id])
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("communes-membres:admin_acte_list"))
        self.assertFalse(ActeLocal.objects.filter(id=acte.id).exists())

    def test_view_not_found(self):
        """Test d'accès à un acte inexistant."""
        self.client.login(email=self.superuser.email, password="adminpassword")

        response = self.client.get(
            reverse("communes-membres:admin_acte_update", args=[999])
        )
        self.assertEqual(response.status_code, 404)


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class CommunesMembresPermissionsTestCase(BaseCommunesMembresTestCase):
    """Tests pour les permissions de l'application communes_membres."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.superuser = User.objects.create_superuser(
            email="admin@exemple.com", password="adminpassword"
        )

        cls.staff_user_with_perms = User.objects.create_user(
            email="staff_with_perms@exemple.com",
            password="staffpassword",
            is_staff=True,
        )

        cls.staff_user_no_perms = User.objects.create_user(
            email="staff_no_perms@exemple.com", password="staffpassword", is_staff=True
        )

        cls.regular_user = User.objects.create_user(
            email="user@exemple.com", password="userpassword"
        )

        # Ajouter les permissions au staff user
        permissions = [
            "add_actelocal",
            "change_actelocal",
            "delete_actelocal",
            "view_actelocal",
        ]
        for perm_name in permissions:
            try:
                permission = Permission.objects.get(codename=perm_name)
                cls.staff_user_with_perms.user_permissions.add(permission)
            except Permission.DoesNotExist:
                pass

    def setUp(self):
        """Configuration de l'environnement de test."""
        self.client = Client()

        self.commune = ConseilVille.objects.create(
            city_name="Test Commune",
            mayor_sex="M",
            mayor_first_name="Jean",
            mayor_last_name="Dupont",
            address="123 Rue de la République",
            postal_code="75001",
            phone_number="0123456789",
            website="http://www.testcommune.fr",
            slogan="Slogan de la commune",
            nb_habitants=1000,
        )

    def test_superuser_access(self):
        """Test qu'un superutilisateur peut accéder à toutes les vues."""
        self.client.login(email=self.superuser.email, password="adminpassword")

        urls = [
            reverse("communes-membres:admin_acte_add"),
            reverse("communes-membres:admin_acte_list"),
        ]

        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

    def test_staff_user_with_permissions(self):
        """Test qu'un utilisateur staff avec permissions peut accéder."""
        self.client.login(
            email=self.staff_user_with_perms.email, password="staffpassword"
        )

        urls = [
            reverse("communes-membres:admin_acte_add"),
            reverse("communes-membres:admin_acte_list"),
        ]

        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

    def test_staff_user_without_permissions(self):
        """Test qu'un utilisateur staff sans permissions ne peut pas accéder."""
        self.client.login(
            email=self.staff_user_no_perms.email, password="staffpassword"
        )

        response = self.client.get(reverse("communes-membres:admin_acte_add"))
        # Django redirige vers la page de login au lieu de retourner 403
        self.assertEqual(response.status_code, 302)

    def test_regular_user_no_access(self):
        """Test qu'un utilisateur normal ne peut pas accéder."""
        self.client.login(email=self.regular_user.email, password="userpassword")

        response = self.client.get(reverse("communes-membres:admin_acte_add"))
        # Django redirige vers la page de login au lieu de retourner 403
        self.assertEqual(response.status_code, 302)

    def test_anonymous_user_redirect(self):
        """Test qu'un utilisateur anonyme est redirigé."""
        response = self.client.get(reverse("communes-membres:admin_acte_add"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_public_view_accessible_to_all(self):
        """Test que la vue publique est accessible à tous."""
        # Test utilisateur anonyme
        response = self.client.get(
            reverse("communes-membres:commune", args=[self.commune.slug])
        )
        self.assertEqual(response.status_code, 200)

        # Test utilisateur connecté
        self.client.login(email=self.regular_user.email, password="userpassword")
        response = self.client.get(
            reverse("communes-membres:commune", args=[self.commune.slug])
        )
        self.assertEqual(response.status_code, 200)


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class CommunesMembresAdminTestCase(BaseCommunesMembresTestCase):
    """Tests pour l'interface d'administration de ActeLocal."""

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

        self.commune = ConseilVille.objects.create(
            city_name="Test Commune",
            mayor_sex="M",
            mayor_first_name="Jean",
            mayor_last_name="Dupont",
            address="123 Rue de la République",
            postal_code="75001",
            phone_number="0123456789",
            website="http://www.testcommune.fr",
            slogan="Slogan de la commune",
            nb_habitants=1000,
        )

        self.test_file = SimpleUploadedFile(
            "acte_test.pdf", b"Contenu PDF test", content_type="application/pdf"
        )

    def test_admin_model_registered(self):
        """Test que le modèle est enregistré dans l'admin."""
        self.assertIn(ActeLocal, site._registry)
        admin_class = site._registry[ActeLocal]
        self.assertIsInstance(admin_class, CustomCommuneMAdmin)

    def test_admin_list_display(self):
        """Test de la configuration list_display."""
        admin_class = site._registry[ActeLocal]
        expected_fields = ("title", "date", "description", "commune", "file")
        self.assertEqual(admin_class.list_display, expected_fields)

    def test_admin_list_filter(self):
        """Test de la configuration list_filter."""
        admin_class = site._registry[ActeLocal]
        expected_filters = ("title", "date", "description", "commune", "file")
        self.assertEqual(admin_class.list_filter, expected_filters)

    def test_admin_search_fields(self):
        """Test de la configuration search_fields."""
        admin_class = site._registry[ActeLocal]
        expected_fields = ("title", "date", "description", "commune", "file")
        self.assertEqual(admin_class.search_fields, expected_fields)

    def test_admin_ordering(self):
        """Test de la configuration ordering."""
        admin_class = site._registry[ActeLocal]
        expected_ordering = ("date",)
        self.assertEqual(admin_class.ordering, expected_ordering)

    def test_admin_form_class(self):
        """Test que le formulaire personnalisé est utilisé."""
        admin_class = site._registry[ActeLocal]
        self.assertEqual(admin_class.form, ActesLocForm)


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class CommunesMembresIntegrationTestCase(BaseCommunesMembresTestCase):
    """Tests d'intégration pour l'application communes_membres."""

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

        self.commune = ConseilVille.objects.create(
            city_name="Test Commune",
            mayor_sex="M",
            mayor_first_name="Jean",
            mayor_last_name="Dupont",
            address="123 Rue de la République",
            postal_code="75001",
            phone_number="0123456789",
            website="http://www.testcommune.fr",
            slogan="Slogan de la commune",
            nb_habitants=1000,
        )

    def test_complete_acte_workflow(self):
        """Test du workflow complet : création → modification → suppression."""
        # 1. Créer un acte local
        test_file = SimpleUploadedFile(
            "acte_workflow.pdf", b"Contenu workflow", content_type="application/pdf"
        )

        with patch(
            "django.core.files.storage.FileSystemStorage.save",
            return_value="workflow.pdf",
        ):
            response = self.client.post(
                reverse("communes-membres:admin_acte_add"),
                {
                    "title": "Délibération workflow",
                    "date": date.today(),
                    "description": "Description workflow",
                    "commune": self.commune.id,
                    "file": test_file,
                },
            )

        self.assertEqual(response.status_code, 302)
        acte = ActeLocal.objects.get(title="Délibération workflow")

        # 2. Vérifier dans la liste d'administration
        response = self.client.get(reverse("communes-membres:admin_acte_list"))
        self.assertContains(response, "Délibération workflow")

        # 3. Modifier l'acte
        new_file = SimpleUploadedFile(
            "acte_modifie.pdf", b"Contenu modifie", content_type="application/pdf"
        )

        with patch(
            "django.core.files.storage.FileSystemStorage.save",
            return_value="modifie.pdf",
        ), patch("os.path.exists", return_value=True), patch("os.remove"):
            response = self.client.post(
                reverse("communes-membres:admin_acte_update", args=[acte.id]),
                {
                    "title": "Délibération modifiée",
                    "date": date.today(),
                    "description": "Description modifiée",
                    "commune": self.commune.id,
                    "file": new_file,
                },
            )

        self.assertEqual(response.status_code, 302)

        # 4. Vérifier sur la page publique
        response = self.client.get(
            reverse("communes-membres:commune", args=[self.commune.slug])
        )
        self.assertContains(response, "Délibération modifiée")

        # 5. Supprimer l'acte
        response = self.client.post(
            reverse("communes-membres:admin_acte_delete", args=[acte.id])
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ActeLocal.objects.count(), 0)

    def test_commune_with_multiple_scenarios(self):
        """Test de la commune dans différents scénarios."""
        # Scénario 1: Commune sans acte
        response = self.client.get(
            reverse("communes-membres:commune", args=[self.commune.slug])
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["acte"].id, "0")

        # Scénario 2: Commune avec acte
        with patch(
            "django.core.files.storage.FileSystemStorage.save", return_value="test.pdf"
        ):
            ActeLocal.objects.create(
                title="Délibération test",
                date=date.today(),
                description="Description de test",
                commune=self.commune,
                file=SimpleUploadedFile(
                    "acte_test.pdf", b"Contenu PDF test", content_type="application/pdf"
                ),
            )

        response = self.client.get(
            reverse("communes-membres:commune", args=[self.commune.slug])
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.context["acte"].id, "0")

        # Scénario 3: Commune inexistante
        response = self.client.get(
            reverse("communes-membres:commune", args=["inexistant"])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "communes_membres/commune_no_ville.html")


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class CommunesMembresEdgeCasesTestCase(BaseCommunesMembresTestCase):
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

        self.commune = ConseilVille.objects.create(
            city_name="Test Commune",
            mayor_sex="M",
            mayor_first_name="Jean",
            mayor_last_name="Dupont",
            address="123 Rue de la République",
            postal_code="75001",
            phone_number="0123456789",
            website="http://www.testcommune.fr",
            slogan="Slogan de la commune",
            nb_habitants=1000,
        )

    def test_acte_with_very_old_date(self):
        """Test avec une date très ancienne."""
        old_date = date(1900, 1, 1)

        with patch(
            "django.core.files.storage.FileSystemStorage.save", return_value="old.pdf"
        ):
            acte = ActeLocal.objects.create(
                title="Acte très ancien",
                date=old_date,
                description="Description ancienne",
                commune=self.commune,
                file=SimpleUploadedFile(
                    "acte_ancien.pdf", b"Contenu ancien", content_type="application/pdf"
                ),
            )

        self.assertEqual(acte.date, old_date)
        self.assertIn("1900-01-01", str(acte))

    def test_acte_with_future_date(self):
        """Test avec une date future."""
        future_date = date.today() + timedelta(days=365)

        with patch(
            "django.core.files.storage.FileSystemStorage.save",
            return_value="future.pdf",
        ):
            acte = ActeLocal.objects.create(
                title="Acte futur",
                date=future_date,
                description="Description future",
                commune=self.commune,
                file=SimpleUploadedFile(
                    "acte_futur.pdf", b"Contenu futur", content_type="application/pdf"
                ),
            )

        self.assertEqual(acte.date, future_date)

    def test_acte_with_very_long_title(self):
        """Test avec un titre très long."""
        long_title = "A" * 200  # Titre de 200 caractères (limite du modèle)

        with patch(
            "django.core.files.storage.FileSystemStorage.save", return_value="long.pdf"
        ):
            acte = ActeLocal.objects.create(
                title=long_title,
                date=date.today(),
                description="Description normale",
                commune=self.commune,
                file=SimpleUploadedFile(
                    "acte_long.pdf",
                    b"Contenu long titre",
                    content_type="application/pdf",
                ),
            )

        self.assertEqual(acte.title, long_title)

    def test_acte_with_very_long_description(self):
        """Test avec une description très longue."""
        long_description = "B" * 500  # Description de 500 caractères (limite du modèle)

        with patch(
            "django.core.files.storage.FileSystemStorage.save",
            return_value="longdesc.pdf",
        ):
            acte = ActeLocal.objects.create(
                title="Titre normal",
                date=date.today(),
                description=long_description,
                commune=self.commune,
                file=SimpleUploadedFile(
                    "acte_longdesc.pdf",
                    b"Contenu long description",
                    content_type="application/pdf",
                ),
            )

        self.assertEqual(acte.description, long_description)

    def test_acte_with_special_characters(self):
        """Test avec des caractères spéciaux."""
        special_title = "Délibération n°123 - Arrêté préfectoral (éàùç)"
        special_description = "Description avec caractères spéciaux : éèàùç - «»"

        with patch(
            "django.core.files.storage.FileSystemStorage.save",
            return_value="special.pdf",
        ):
            acte = ActeLocal.objects.create(
                title=special_title,
                date=date.today(),
                description=special_description,
                commune=self.commune,
                file=SimpleUploadedFile(
                    "acte_special.pdf",
                    b"Contenu special",
                    content_type="application/pdf",
                ),
            )

        self.assertEqual(acte.title, special_title)
        self.assertEqual(acte.description, special_description)

    def test_file_upload_error_handling(self):
        """Test de gestion des erreurs d'upload de fichier."""
        # Test avec un fichier non-PDF
        with self.assertRaises(ValidationError):
            acte = ActeLocal(
                title="Test upload error",
                date=date.today(),
                description="Description test",
                commune=self.commune,
                file=SimpleUploadedFile(
                    "invalid_file.txt",
                    b"Contenu texte invalide",
                    content_type="text/plain",
                ),
            )
            acte.full_clean()

    def test_commune_slug_with_special_characters(self):
        """Test avec un slug de commune contenant des caractères spéciaux."""
        commune_special = ConseilVille.objects.create(
            city_name="Saint-Étienne-lès-Remiremont",
            mayor_sex="F",
            mayor_first_name="Marie",
            mayor_last_name="Dubois",
            address="Place de la Mairie",
            postal_code="88200",
            phone_number="0329000000",
            website="http://www.saint-etienne-les-remiremont.fr",
            slogan="Ville d'histoire",
            nb_habitants=3500,
        )

        response = self.client.get(
            reverse("communes-membres:commune", args=[commune_special.slug])
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["commune"], commune_special)


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class CommunesListViewTestCase(BaseCommunesMembresTestCase):
    """Tests pour la vue publique listant les communes membres sous forme de cards.

    TDD : ces tests sont écrits AVANT l'implémentation de la vue et du service.
    Ils doivent échouer tant que la vue ``communes_list`` n'existe pas et que
    ``CommuneListingService`` n'est pas créé.
    """

    def setUp(self):
        """Préparation : 3 communes de test avec images."""
        from django.core.cache import cache

        cache.clear()  # Reset cache entre tests (le service utilise le cache)
        self.client = Client()

        self.commune_a = ConseilVille.objects.create(
            city_name="Anor",
            mayor_sex="M",
            mayor_first_name="Jean",
            mayor_last_name="Dupont",
            address="Place de la Mairie",
            postal_code="59186",
            phone_number="0359600000",
            website="http://www.anor.fr",
            slogan="Ville d'histoire",
            nb_habitants=3200,
            image=TEST_IMAGE,
        )
        self.commune_b = ConseilVille.objects.create(
            city_name="Baives",
            mayor_sex="M",
            mayor_first_name="Pierre",
            mayor_last_name="Martin",
            address="Rue Principale",
            postal_code="59132",
            phone_number="0359600001",
            website="http://www.baives.fr",
            slogan=None,
            nb_habitants=180,
            image=TEST_IMAGE,
        )
        self.commune_c = ConseilVille.objects.create(
            city_name="Fourmies",
            mayor_sex="M",
            mayor_first_name="Alain",
            mayor_last_name="Durand",
            address="Rue de l'Hôtel de Ville",
            postal_code="59610",
            phone_number="0359600002",
            website="http://www.fourmies.fr",
            slogan="Pôle urbain du Sud-Avesnois",
            nb_habitants=12000,
            image=TEST_IMAGE,
        )

    def test_list_view_status_200(self):
        """La page de liste renvoie HTTP 200."""
        response = self.client.get(reverse("communes-membres:list"))
        self.assertEqual(response.status_code, 200)

    def test_list_view_uses_correct_template(self):
        """La vue utilise le template ``communes_list.html``."""
        response = self.client.get(reverse("communes-membres:list"))
        self.assertTemplateUsed(response, "communes_membres/communes_list.html")

    def test_list_view_context_contains_communes(self):
        """Le contexte expose la liste des communes triées alphabétiquement."""
        response = self.client.get(reverse("communes-membres:list"))
        self.assertIn("communes", response.context)
        communes = list(response.context["communes"])
        self.assertEqual(
            [c.city_name for c in communes],
            ["Anor", "Baives", "Fourmies"],
        )

    def test_list_view_context_contains_total(self):
        """Le contexte expose le nombre total de communes."""
        response = self.client.get(reverse("communes-membres:list"))
        self.assertEqual(response.context["total"], 3)

    def test_list_view_uses_only_one_query(self):
        """La vue ne déclenche pas de N+1 (2 requêtes max : 1 vue + 1 context_processor).

        La 2ᵉ requête provient de ``app.context_processors.get_cities`` qui est
        appelé sur **chaque** page du site pour alimenter le menu des communes.
        C'est un comportement existant, indépendant de notre vue.
        """
        with self.assertNumQueries(2):
            self.client.get(reverse("communes-membres:list"))

    def test_list_view_accessible_to_anonymous(self):
        """La page est publique : accessible sans authentification."""
        response = self.client.get(reverse("communes-membres:list"))
        self.assertEqual(response.status_code, 200)

    def test_list_view_contains_all_commune_names(self):
        """Chaque nom de commune apparaît dans le HTML rendu."""
        response = self.client.get(reverse("communes-membres:list"))
        self.assertContains(response, "Anor")
        self.assertContains(response, "Baives")
        self.assertContains(response, "Fourmies")

    def test_list_view_contains_descriptive_alt_on_images(self):
        """Chaque image de card possède un attribut ``alt`` descriptif."""
        response = self.client.get(reverse("communes-membres:list"))
        for city in ["Anor", "Baives", "Fourmies"]:
            self.assertContains(
                response,
                f'alt="Vue de la commune de {city}"',
            )

    def test_list_view_contains_aria_labelledby(self):
        """Chaque card est liée à son titre via ``aria-labelledby``."""
        response = self.client.get(reverse("communes-membres:list"))
        for city in ["anor", "baives", "fourmies"]:
            self.assertContains(
                response,
                f'aria-labelledby="commune-{city}"',
            )

    def test_list_view_contains_h2_heading_per_card(self):
        """Chaque card possède un titre de niveau 2 (sémantique liste cards)."""
        response = self.client.get(reverse("communes-membres:list"))
        self.assertContains(response, '<h2 id="commune-anor"', html=True)
        self.assertContains(response, '<h2 id="commune-baives"', html=True)
        self.assertContains(response, '<h2 id="commune-fourmies"', html=True)

    def test_list_view_contains_semantic_ul_list(self):
        """La liste des cards est dans un ``<ul role="list">`` sémantique."""
        response = self.client.get(reverse("communes-membres:list"))
        self.assertContains(response, '<ul role="list"')

    def test_list_view_contains_link_to_detail(self):
        """Chaque card renvoie vers la fiche détail de la commune."""
        response = self.client.get(reverse("communes-membres:list"))
        for slug in ["anor", "baives", "fourmies"]:
            detail_url = reverse("communes-membres:commune", args=[slug])
            self.assertContains(response, detail_url)

    def test_list_view_empty_state_does_not_crash(self):
        """Une liste vide affiche un message ``role="status"`` sans crash."""
        ConseilVille.objects.all().delete()
        response = self.client.get(reverse("communes-membres:list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'role="status"')
        self.assertEqual(response.context["total"], 0)

    def test_list_view_contains_slogan_or_fallback(self):
        """Le slogan de la commune OU le fallback apparaît dans chaque card.

        Note : les apostrophes sont HTML-escapées par Django (``'`` → ``&#x27;``),
        c'est pourquoi on cherche les fragments sans apostrophe.
        """
        response = self.client.get(reverse("communes-membres:list"))
        # commune_a a un slogan explicite (contient "histoire")
        self.assertContains(response, "histoire")
        # commune_b n'a pas de slogan : le fallback est utilisé
        self.assertContains(response, "Commune membre")
        # commune_c a un slogan explicite
        self.assertContains(response, "Pôle urbain")

    def test_list_view_contains_inhabitants_count(self):
        """Le badge affiche le nombre d'habitants de chaque commune (format français)."""
        response = self.client.get(reverse("communes-membres:list"))
        # commune_a : 3 200 hab. (espace fine U+202F comme séparateur)
        self.assertContains(response, "3 200")
        # commune_b : 180 hab.
        self.assertContains(response, "180")
        # commune_c : 12 000 hab.
        self.assertContains(response, "12 000")
        # Le suffixe "hab." doit être présent
        self.assertContains(response, "hab.")
        # L'aria-label descriptif est présent (apostrophe brute, pas échappée dans un attr double-quoted)
        self.assertContains(response, 'aria-label="Nombre d\'habitants : 3200"')
        self.assertContains(response, 'aria-label="Nombre d\'habitants : 180"')
        self.assertContains(response, 'aria-label="Nombre d\'habitants : 12000"')

    def test_list_view_uses_lazy_loading(self):
        """Les images sont en ``loading="lazy"`` (perf + RGAA 8.1)."""
        response = self.client.get(reverse("communes-membres:list"))
        self.assertContains(response, 'loading="lazy"')

    def test_list_view_uses_paired_dimensions(self):
        """Les images ont ``width``/``height`` (CLS - Core Web Vitals)."""
        response = self.client.get(reverse("communes-membres:list"))
        self.assertContains(response, 'width="400"')
        self.assertContains(response, 'height="225"')

    def test_list_view_url_named(self):
        """La route ``communes-membres:list`` est résolvable."""
        url = reverse("communes-membres:list")
        self.assertEqual(url, "/communes-membres/")

    def test_list_view_h1_present(self):
        """La page contient un H1 unique et pertinent."""
        response = self.client.get(reverse("communes-membres:list"))
        self.assertContains(response, "<h1")

    def test_list_view_dark_mode_classes(self):
        """Les cards ont des classes ``dark:`` pour le mode sombre."""
        response = self.client.get(reverse("communes-membres:list"))
        self.assertContains(response, "dark:")


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class CommuneListingServiceTestCase(BaseCommunesMembresTestCase):
    """Tests unitaires du service SOLID ``CommuneListingService``."""

    def setUp(self):
        from django.core.cache import cache

        cache.clear()
        self.commune_a = ConseilVille.objects.create(
            city_name="Anor",
            mayor_sex="M",
            mayor_first_name="Jean",
            mayor_last_name="Dupont",
            address="Place de la Mairie",
            postal_code="59186",
            phone_number="0359600000",
            slogan="Ville d'histoire",
            nb_habitants=3200,
            image=TEST_IMAGE,
        )
        # Commune SANS slogan pour tester le fallback
        self.commune_b = ConseilVille.objects.create(
            city_name="Baives",
            mayor_sex="M",
            mayor_first_name="Pierre",
            mayor_last_name="Martin",
            address="Rue Principale",
            postal_code="59132",
            phone_number="0359600001",
            slogan=None,
            nb_habitants=180,
        )

    def test_service_returns_communes_alphabetical(self):
        """Le service retourne les communes triées par nom."""
        communes = list(CommuneListingService.get_communes_for_listing())
        self.assertEqual([c.city_name for c in communes], ["Anor", "Baives"])

    def test_service_uses_only_necessary_fields(self):
        """Le service ne charge que les colonnes utiles (perf)."""
        with self.assertNumQueries(1):
            list(CommuneListingService.get_communes_for_listing())

    def test_get_placeholder_image_url_returns_string(self):
        """Le service expose une URL placeholder non vide."""
        url = CommuneListingService.get_placeholder_image_url()
        self.assertIsInstance(url, str)
        self.assertGreater(len(url), 0)

    def test_get_card_context_returns_full_dict(self):
        """Le contexte d'une card contient tous les champs attendus."""
        ctx = CommuneListingService.get_card_context(self.commune_a)
        for key in (
            "commune",
            "title",
            "image_url",
            "alt_text",
            "slogan",
            "detail_url",
            "heading_id",
            "nb_habitants",
        ):
            self.assertIn(key, ctx)
        self.assertEqual(ctx["heading_id"], "commune-anor")
        self.assertEqual(ctx["alt_text"], "Vue de la commune de Anor")
        self.assertIn("Ville d'histoire", ctx["slogan"])
        self.assertEqual(ctx["nb_habitants"], 3200)

    def test_get_card_context_slogan_fallback(self):
        """Si la commune n'a pas de slogan, le service applique un fallback."""
        ctx = CommuneListingService.get_card_context(self.commune_b)
        self.assertIn("Commune membre", ctx["slogan"])
