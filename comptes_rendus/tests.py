import os
import shutil
from unittest.mock import Mock, patch

from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.test.utils import override_settings
from django.urls import reverse

from comptes_rendus.admin import (CustomConseilAdmin, CustomCRAdmin,
                                  delete_content)
from comptes_rendus.forms import ConseilForm, CRForm
from comptes_rendus.models import CompteRendu, Conseil

User = get_user_model()
MEDIA_ROOT = "test_media_comptes-rendus"


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class ComptesRendusTestCase(TestCase):
    """
    Tests pour les vues de l'application Comptes Rendus.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.superuser = User.objects.create_superuser(
            email="admin@exemple.com", password="adminpassword"
        )

    def setUp(self):
        """
        Configuration de l'environnement de test.
        """
        self.client = Client()
        self.client.login(email=self.superuser.email, password="adminpassword")

    def tearDown(self):
        CompteRendu.objects.all().delete()
        Conseil.objects.all().delete()
        # Supprimer le répertoire MEDIA_ROOT après les tests
        if os.path.exists(MEDIA_ROOT):
            shutil.rmtree(MEDIA_ROOT)

    # Test d'affichage de la page publique
    def test_cr_public_get_views(self):
        """
        Test de la page publique des comptes-rendus.
        """
        response = self.client.get(reverse("comptes_rendus:comptes_rendus"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "comptes_rendus/comptes-rendus.html")
        self.assertContains(response, "Non disponible.")
        self.assertContains(response, "Aucun conseil disponible")

    def test_cr_public_get_views_with_data(self):
        """
        Test de la page publique des comptes-rendus avec des données.
        """
        compte_rendu = CompteRendu.objects.create(link="https://example.com/cr")
        conseil = Conseil.objects.create(
            date="2023-10-01", hour="10:00", place="Salle de réunion", day_order=None
        )

        response = self.client.get(reverse("comptes_rendus:comptes_rendus"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "comptes_rendus/comptes-rendus.html")
        self.assertContains(response, "https://example.com/cr")
        self.assertContains(response, "10h00")
        self.assertContains(response, "Salle de réunion")
        self.assertContains(response, "À venir")
        self.assertContains(response, "1 octobre 2023")

    # Test de la page admin
    def test_cr_admin_get_views(self):
        """
        Test de la page admin des comptes-rendus.
        """
        response = self.client.get(reverse("comptes_rendus:admin_cr_list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "comptes_rendus/admin_page.html")
        self.assertContains(response, "Ajouter le lien vers les comptes rendus")
        self.assertContains(response, "Programmer un conseil")
        self.assertContains(response, "Aucun compte rendu disponible")

    def test_cr_admin_get_views_with_data(self):
        """
        Test de la page admin des comptes-rendus avec des données.
        """
        compte_rendu = CompteRendu.objects.create(link="https://example.com/cr")
        conseil = Conseil.objects.create(
            date="2023-10-01", hour="10:00", place="Salle de réunion", day_order=None
        )

        response = self.client.get(reverse("comptes_rendus:admin_cr_list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "comptes_rendus/admin_page.html")
        self.assertContains(response, "https://example.com/cr")
        self.assertContains(response, "10h00")
        self.assertContains(response, "Salle de réunion")
        self.assertContains(response, "À venir")
        self.assertContains(response, "1 octobre 2023")

    # Test d'ajout des conseils
    def test_cr_admin_add_conseil_get_view(self):
        """
        Test de la page d'ajout d'un conseil.
        """
        response = self.client.get(reverse("comptes_rendus:add_conseil"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "comptes_rendus/admin_conseil_add.html")
        self.assertContains(response, "Publier")
        self.assertContains(response, "Date")
        self.assertContains(response, "Heure")
        self.assertContains(response, "Lieu")
        self.assertContains(response, "Ordre du jour")

    def test_cr_admin_add_conseil_post_view(self):
        """
        Test de l'ajout d'un conseil.
        """

        response = self.client.post(
            reverse("comptes_rendus:add_conseil"),
            {
                "date": "2023-10-01",
                "hour": "10:00",
                "place": "Salle de réunion",
                "day_order": SimpleUploadedFile(
                    "test.pdf",
                    content=b"Document pdf de test",
                    content_type="application/pdf",
                ),
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Conseil.objects.filter(date="2023-10-01").exists())

    def test_cr_admin_add_conseil_post_view_without_file(self):
        """
        Test de l'ajout d'un conseil sans fichier.
        """
        response = self.client.post(
            reverse("comptes_rendus:add_conseil"),
            {
                "date": "2023-10-01",
                "hour": "10:00",
                "place": "Salle de réunion",
                "day_order": "",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Conseil.objects.filter(date="2023-10-01").exists())

    def test_cr_admin_add_conseil_post_view_invalid_data(self):
        """
        Test de l'ajout d'un conseil avec des données invalides.
        """
        response = self.client.post(
            reverse("comptes_rendus:add_conseil"),
            {
                "date": "2023-10-01",
                "hour": "10:00",
                "place": "",
                "day_order": SimpleUploadedFile(
                    "test.pdf",
                    content=b"Document pdf de test",
                    content_type="application/pdf",
                ),
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "comptes_rendus/admin_conseil_add.html")
        self.assertFalse(Conseil.objects.filter(date="2023-10-01").exists())
        self.assertFalse(
            os.path.exists(MEDIA_ROOT + "/comptes-rendus/ordre-du-jour/pdf_1.pdf")
        )

    # Test de la page d'édition des conseils
    def test_cr_admin_edit_conseil_get_view(self):
        """
        Test de la page d'édition d'un conseil.
        """
        conseil = Conseil.objects.create(
            date="2023-10-01", hour="10:00", place="Salle de réunion", day_order=None
        )
        response = self.client.get(
            reverse("comptes_rendus:edit_conseil", args=[conseil.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "comptes_rendus/admin_conseil_edit.html")
        self.assertContains(response, "Appliquer")

    def test_cr_admin_edit_conseil_post_view(self):
        """
        Test de l'édition d'un conseil.
        """

        conseil = Conseil.objects.create(
            date="2023-10-01",
            hour="10:00",
            place="Salle de réunion",
            day_order=SimpleUploadedFile(
                "last_day_order.pdf",
                content=b"Document pdf de test",
                content_type="application/pdf",
            ),
        )

        id = conseil.id
        last_day_order_path = conseil.day_order.path

        response = self.client.post(
            reverse("comptes_rendus:edit_conseil", args=[conseil.id]),
            {
                "date": "2023-10-02",
                "hour": "11:00",
                "place": "Salle de réunion 2",
                "day_order": SimpleUploadedFile(
                    "new_day_order.pdf",
                    content=b"Document pdf de test",
                    content_type="application/pdf",
                ),
            },
        )

        # on récupère le conseil mis à jour
        conseil = Conseil.objects.get(id=id)

        self.assertEqual(response.status_code, 302)
        self.assertFalse(os.path.exists(last_day_order_path))
        self.assertTrue(os.path.exists(conseil.day_order.path))
        self.assertTrue(Conseil.objects.filter(date="2023-10-02").exists())
        self.assertFalse(Conseil.objects.filter(date="2023-10-01").exists())

    def test_cr_admin_edit_conseil_post_view_without_file(self):
        """
        Test de l'édition d'un conseil sans fichier changement de fichier.
        """

        conseil = Conseil.objects.create(
            date="2023-10-01",
            hour="10:00",
            place="Salle de réunion",
            day_order=SimpleUploadedFile(
                "last_day_order.pdf",
                content=b"Document pdf de test",
                content_type="application/pdf",
            ),
        )

        id = conseil.id
        last_day_order_path = conseil.day_order.path

        response = self.client.post(
            reverse("comptes_rendus:edit_conseil", args=[conseil.id]),
            {
                "date": "2023-10-02",
                "hour": "11:00",
                "place": "Salle de réunion 2",
                "day_order": "",
            },
        )

        # on récupère le conseil mis à jour
        conseil = Conseil.objects.get(id=id)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(os.path.exists(last_day_order_path))
        self.assertTrue(Conseil.objects.filter(date="2023-10-02").exists())
        self.assertFalse(Conseil.objects.filter(date="2023-10-01").exists())

    def test_cr_admin_edit_conseil_post_view_invalid_data(self):
        """
        Test de l'édition d'un conseil avec des données invalides.
        """
        conseil = Conseil.objects.create(
            date="2023-10-01",
            hour="10:00",
            place="Salle de réunion",
            day_order=SimpleUploadedFile(
                "last_day_order.pdf",
                content=b"Document pdf de test",
                content_type="application/pdf",
            ),
        )

        id = conseil.id
        last_day_order_path = conseil.day_order.path

        response = self.client.post(
            reverse("comptes_rendus:edit_conseil", args=[conseil.id]),
            {
                "date": "2023-10-02",
                "hour": "11:00",
                "place": "",
                "day_order": SimpleUploadedFile(
                    "new_day_order.pdf",
                    content=b"Document pdf de test",
                    content_type="application/pdf",
                ),
            },
        )

        # on récupère le conseil mis à jour
        conseil = Conseil.objects.get(id=id)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "comptes_rendus/admin_conseil_edit.html")
        self.assertTrue(os.path.exists(last_day_order_path))

    # Test de la page de suppression des conseils
    def test_cr_admin_delete_conseil_get_view(self):
        """
        Test de la page de suppression d'un conseil.
        """
        conseil = Conseil.objects.create(
            date="2023-10-01",
            hour="10:00",
            place="Salle de réunion",
            day_order=SimpleUploadedFile(
                "not_deleted_day_order.pdf",
                content=b"Document pdf de test",
                content_type="application/pdf",
            ),
        )
        response = self.client.get(
            reverse("comptes_rendus:delete_conseil", args=[conseil.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "comptes_rendus/admin_conseil_delete.html")
        self.assertContains(response, "Supprimer le conseil")

    def test_cr_admin_delete_conseil_post_view(self):
        """
        Test de la suppression d'un conseil.
        """
        conseil = Conseil.objects.create(
            date="2023-10-01",
            hour="10:00",
            place="Salle de réunion",
            day_order=SimpleUploadedFile(
                "day_order_to_delete.pdf",
                content=b"Document pdf de test",
                content_type="application/pdf",
            ),
        )

        id = conseil.id
        day_order_path = conseil.day_order.path

        response = self.client.post(
            reverse("comptes_rendus:delete_conseil", args=[conseil.id])
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Conseil.objects.filter(id=id).exists())
        self.assertFalse(os.path.exists(day_order_path))


class BaseComptesRendusTestCase(TestCase):
    """Classe de base pour tous les tests de comptes_rendus."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.staff_user = User.objects.create_user(
            username="staffuser",
            email="staff@example.com",
            password="staffpass123",
            is_staff=True,
        )

        # Créer un superuser pour les tests d'admin
        self.superuser = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="adminpass123"
        )

    def tearDown(self):
        """Nettoyage après chaque test."""
        CompteRendu.objects.all().delete()
        Conseil.objects.all().delete()
        if os.path.exists(MEDIA_ROOT):
            shutil.rmtree(MEDIA_ROOT)


class CompteRenduModelTestCase(BaseComptesRendusTestCase):
    """Tests pour le modèle CompteRendu."""

    def test_compterendu_creation(self):
        """Test création d'un compte rendu."""
        cr = CompteRendu.objects.create(link="https://drive.google.com/test")
        self.assertEqual(cr.link, "https://drive.google.com/test")
        self.assertEqual(str(cr), "https://drive.google.com/test")

    def test_compterendu_singleton_pattern(self):
        """Test que CompteRendu suit le pattern singleton."""
        # Créer le premier compte rendu
        cr1 = CompteRendu.objects.create(link="https://example.com/cr1")
        self.assertEqual(CompteRendu.objects.count(), 1)

        # Créer un second compte rendu (doit remplacer le premier)
        cr2 = CompteRendu.objects.create(link="https://example.com/cr2")
        self.assertEqual(CompteRendu.objects.count(), 1)

        # Vérifier que seul le second existe
        self.assertFalse(CompteRendu.objects.filter(id=cr1.id).exists())
        self.assertTrue(
            CompteRendu.objects.filter(link="https://example.com/cr2").exists()
        )

    def test_compterendu_str_representation(self):
        """Test représentation string du modèle CompteRendu."""
        cr = CompteRendu.objects.create(link="https://test.com/document")
        self.assertEqual(str(cr), "https://test.com/document")


class ConseilModelTestCase(BaseComptesRendusTestCase):
    """Tests pour le modèle Conseil."""

    def test_conseil_creation(self):
        """Test création d'un conseil."""
        conseil = Conseil.objects.create(
            date="2024-01-15", hour="14:30:00", place="Mairie de Fourmies"
        )
        self.assertEqual(conseil.place, "Mairie de Fourmies")
        self.assertEqual(str(conseil.date), "2024-01-15")

    def test_conseil_str_representation(self):
        """Test représentation string du modèle Conseil."""
        conseil = Conseil.objects.create(
            date="2024-01-15", hour="14:30:00", place="Mairie", day_order="test.pdf"
        )
        expected_str = (
            "Conseil du 2024-01-15 - 14:30:00 - Mairie -             Ordre du jour: test.pdf"
        )
        self.assertEqual(str(conseil), expected_str)

    @override_settings(MEDIA_ROOT=MEDIA_ROOT)
    def test_conseil_with_file_upload(self):
        """Test création d'un conseil avec fichier."""
        test_file = SimpleUploadedFile(
            "ordre_du_jour.pdf", b"PDF content", content_type="application/pdf"
        )

        conseil = Conseil.objects.create(
            date="2024-01-15", hour="14:30:00", place="Mairie", day_order=test_file
        )

        self.assertTrue(conseil.day_order)
        self.assertTrue(conseil.day_order.name.endswith(".pdf"))

    def test_conseil_ordering(self):
        """Test tri des conseils par date."""
        conseil1 = Conseil.objects.create(
            date="2024-01-20", hour="14:00:00", place="Lieu 1"
        )
        conseil2 = Conseil.objects.create(
            date="2024-01-15", hour="10:00:00", place="Lieu 2"
        )

        conseils = Conseil.objects.order_by("date")
        self.assertEqual(list(conseils), [conseil2, conseil1])


class CRFormTestCase(BaseComptesRendusTestCase):
    """Tests pour le formulaire CRForm."""

    def test_crform_valid_data(self):
        """Test formulaire CRForm avec données valides."""
        form = CRForm(data={"link": "https://drive.google.com/test"})
        self.assertTrue(form.is_valid())

    def test_crform_invalid_data(self):
        """Test formulaire CRForm avec données invalides."""
        form = CRForm(data={"link": ""})  # Champ requis vide
        self.assertFalse(form.is_valid())
        self.assertIn("link", form.errors)

    def test_crform_labels(self):
        """Test labels du formulaire CRForm."""
        form = CRForm()
        self.assertEqual(form.fields["link"].label, "Lien vers le stockage en ligne")

    def test_crform_widgets(self):
        """Test widgets du formulaire CRForm."""
        form = CRForm()
        widget = form.fields["link"].widget
        self.assertIn("form-control", widget.attrs["class"])
        self.assertIn("https://drive.google.com/", widget.attrs["placeholder"])


class ConseilFormTestCase(BaseComptesRendusTestCase):
    """Tests pour le formulaire ConseilForm."""

    def test_conseilform_valid_data(self):
        """Test formulaire ConseilForm avec données valides."""
        form = ConseilForm(
            data={"date": "2024-01-15", "hour": "14:30", "place": "Mairie de Fourmies"}
        )
        self.assertTrue(form.is_valid())

    def test_conseilform_invalid_data(self):
        """Test formulaire ConseilForm avec données invalides."""
        form = ConseilForm(
            data={"date": "", "hour": "14:30", "place": "Mairie"}  # Champ requis vide
        )
        self.assertFalse(form.is_valid())
        self.assertIn("date", form.errors)

    def test_conseilform_labels(self):
        """Test labels du formulaire ConseilForm."""
        form = ConseilForm()
        expected_labels = {
            "date": "Date",
            "hour": "Heure",
            "place": "Lieu",
            "day_order": "Ordre du jour",
        }

        for field_name, expected_label in expected_labels.items():
            self.assertEqual(form.fields[field_name].label, expected_label)

    def test_conseilform_widgets(self):
        """Test widgets du formulaire ConseilForm."""
        form = ConseilForm()

        # Test widget date
        date_widget = form.fields["date"].widget
        self.assertIn("form-control", date_widget.attrs["class"])
        # Le type peut être dans les attrs ou pas selon la version de Django
        if "type" in date_widget.attrs:
            self.assertEqual(date_widget.attrs["type"], "date")

        # Test widget hour
        hour_widget = form.fields["hour"].widget
        self.assertIn("form-control", hour_widget.attrs["class"])
        if "type" in hour_widget.attrs:
            self.assertEqual(hour_widget.attrs["type"], "time")

        # Test widget place
        place_widget = form.fields["place"].widget
        self.assertIn("form-control", place_widget.attrs["class"])
        self.assertIn("Lieu de la réunion", place_widget.attrs["placeholder"])

    @override_settings(MEDIA_ROOT=MEDIA_ROOT)
    def test_conseilform_with_file(self):
        """Test formulaire ConseilForm avec fichier."""
        test_file = SimpleUploadedFile(
            "test.pdf", b"PDF content", content_type="application/pdf"
        )

        form = ConseilForm(
            data={"date": "2024-01-15", "hour": "14:30", "place": "Mairie"},
            files={"day_order": test_file},
        )

        self.assertTrue(form.is_valid())


class ComptesRendusPermissionsTestCase(BaseComptesRendusTestCase):
    """Tests pour les permissions de l'application comptes_rendus."""

    def test_public_view_accessible_to_all(self):
        """Test que la vue publique est accessible à tous."""
        # Utilisateur anonyme
        response = self.client.get(reverse("comptes_rendus:comptes_rendus"))
        self.assertEqual(response.status_code, 200)

        # Utilisateur connecté
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("comptes_rendus:comptes_rendus"))
        self.assertEqual(response.status_code, 200)

    def test_admin_views_require_permissions(self):
        """Test que les vues admin nécessitent des permissions."""
        # Test sans connexion
        response = self.client.get(reverse("comptes_rendus:admin_cr_list"))
        self.assertEqual(response.status_code, 302)  # Redirection vers login

        # Test avec utilisateur normal (sans permissions)
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("comptes_rendus:admin_cr_list"))
        self.assertEqual(response.status_code, 302)  # Redirection (permission refusée)

    def test_add_conseil_permission_required(self):
        """Test que l'ajout de conseil nécessite une permission."""
        # Test sans permission
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("comptes_rendus:add_conseil"))
        self.assertEqual(response.status_code, 302)  # Redirection (permission refusée)

    def test_add_cr_link_permission_required(self):
        """Test que l'ajout de lien CR nécessite une permission."""
        # Test sans permission
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("comptes_rendus:add_cr_link"))
        self.assertEqual(response.status_code, 302)  # Redirection (permission refusée)


class ComptesRendusAdminTestCase(BaseComptesRendusTestCase):
    """Tests pour l'interface admin de comptes_rendus."""

    def setUp(self):
        super().setUp()
        self.site = AdminSite()
        self.conseil_admin = CustomConseilAdmin(Conseil, self.site)
        self.cr_admin = CustomCRAdmin(CompteRendu, self.site)

    def test_conseil_admin_configuration(self):
        """Test configuration de l'admin Conseil."""
        self.assertEqual(
            self.conseil_admin.list_display, ("date", "hour", "place", "day_order")
        )
        self.assertEqual(self.conseil_admin.search_fields, ("place", "date"))
        self.assertEqual(self.conseil_admin.list_filter, ("date", "hour"))
        self.assertEqual(self.conseil_admin.ordering, ("date", "hour"))

    def test_conseil_admin_actions(self):
        """Test actions personnalisées de l'admin Conseil."""
        # Créer un mock request
        request = Mock()
        request.GET = {}

        actions = self.conseil_admin.get_actions(request)
        self.assertIn("delete_content", actions)
        self.assertNotIn("delete_selected", actions)  # Action par défaut supprimée

    @patch("os.path.exists")
    @patch("os.remove")
    def test_conseil_admin_delete_model(self, mock_remove, mock_exists):
        """Test suppression de modèle avec fichier."""
        mock_exists.return_value = True

        conseil = Conseil.objects.create(
            date="2024-01-15", hour="14:30:00", place="Mairie"
        )
        conseil.day_order.name = "test.pdf"

        request = Mock()
        self.conseil_admin.delete_model(request, conseil)

        mock_exists.assert_called_once()
        mock_remove.assert_called_once()

    @patch("os.path.exists")
    @patch("os.remove")
    def test_conseil_admin_delete_content_action(self, mock_remove, mock_exists):
        """Test action de suppression de contenu."""
        mock_exists.return_value = True

        conseil1 = Conseil.objects.create(
            date="2024-01-15", hour="14:30:00", place="Mairie 1"
        )
        conseil2 = Conseil.objects.create(
            date="2024-01-16", hour="15:30:00", place="Mairie 2"
        )

        queryset = Conseil.objects.all()
        request = Mock()

        delete_content(self.conseil_admin, request, queryset)

        self.assertEqual(Conseil.objects.count(), 0)

    def test_cr_admin_configuration(self):
        """Test configuration de l'admin CompteRendu."""
        self.assertEqual(self.cr_admin.list_display, ("link",))
        self.assertEqual(self.cr_admin.model, CompteRendu)


class ComptesRendusIntegrationTestCase(BaseComptesRendusTestCase):
    """Tests d'intégration pour l'application comptes_rendus."""

    def test_public_view_with_multiple_data(self):
        """Test vue publique avec plusieurs conseils et un lien CR."""
        # Créer des données de test
        CompteRendu.objects.create(link="https://drive.google.com/cr")

        Conseil.objects.create(
            date="2024-01-15", hour="14:30:00", place="Mairie de Fourmies"
        )
        Conseil.objects.create(
            date="2024-02-15", hour="10:00:00", place="Mairie d'Anor"
        )

        response = self.client.get(reverse("comptes_rendus:comptes_rendus"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "https://drive.google.com/cr")
        self.assertContains(response, "Mairie de Fourmies")
        # Le HTML encode l'apostrophe comme &#x27;
        self.assertContains(response, "Mairie d&#x27;Anor")
        self.assertContains(response, "15 janvier 2024")
        self.assertContains(response, "15 février 2024")

    def test_model_interactions(self):
        """Test interactions entre les modèles."""
        # Test création de plusieurs conseils
        conseil1 = Conseil.objects.create(
            date="2024-01-15", hour="14:30:00", place="Mairie de Fourmies"
        )
        conseil2 = Conseil.objects.create(
            date="2024-01-16", hour="10:00:00", place="Mairie d'Anor"
        )

        self.assertEqual(Conseil.objects.count(), 2)

        # Test pattern singleton CompteRendu
        cr1 = CompteRendu.objects.create(link="https://example.com/cr1")
        cr2 = CompteRendu.objects.create(link="https://example.com/cr2")

        # Seul le second doit exister
        self.assertEqual(CompteRendu.objects.count(), 1)
        self.assertEqual(CompteRendu.objects.first().link, "https://example.com/cr2")


class ComptesRendusEdgeCasesTestCase(BaseComptesRendusTestCase):
    """Tests pour les cas limites de l'application comptes_rendus."""

    def setUp(self):
        super().setUp()
        self.site = AdminSite()
        self.conseil_admin = CustomConseilAdmin(Conseil, self.site)

    def test_conseil_with_special_characters(self):
        """Test conseil avec caractères spéciaux."""
        conseil = Conseil.objects.create(
            date="2024-01-15", hour="14:30:00", place="Mairie d'Étrœungt - Salle n°1"
        )

        self.assertEqual(conseil.place, "Mairie d'Étrœungt - Salle n°1")
        self.assertIn("Étrœungt", str(conseil))

    def test_conseil_past_and_future_dates(self):
        """Test conseils avec dates passées et futures."""
        from datetime import date, timedelta

        # Conseil passé
        past_date = date.today() - timedelta(days=30)
        conseil_passe = Conseil.objects.create(
            date=past_date, hour="14:30:00", place="Mairie"
        )

        # Conseil futur
        future_date = date.today() + timedelta(days=30)
        conseil_futur = Conseil.objects.create(
            date=future_date, hour="14:30:00", place="Mairie"
        )

        self.assertTrue(conseil_passe.date < date.today())
        self.assertTrue(conseil_futur.date > date.today())

    def test_compterendu_with_very_long_url(self):
        """Test CompteRendu avec URL très longue."""
        long_url = "https://drive.google.com/" + "a" * 150
        cr = CompteRendu.objects.create(link=long_url)
        self.assertEqual(cr.link, long_url)

    @patch("os.path.exists")
    @patch("os.remove")
    def test_file_deletion_when_path_not_exists(self, mock_remove, mock_exists):
        """Test suppression de fichier quand le chemin n'existe pas."""
        mock_exists.return_value = False

        conseil = Conseil.objects.create(
            date="2024-01-15", hour="14:30:00", place="Mairie"
        )
        conseil.day_order.name = "nonexistent.pdf"

        request = Mock()
        self.conseil_admin.delete_model(request, conseil)

        mock_exists.assert_called_once()
        mock_remove.assert_not_called()

    def test_conseil_ordering_with_same_date(self):
        """Test tri des conseils avec même date mais heures différentes."""
        conseil1 = Conseil.objects.create(
            date="2024-01-15", hour="16:00:00", place="Lieu 1"
        )
        conseil2 = Conseil.objects.create(
            date="2024-01-15", hour="14:00:00", place="Lieu 2"
        )

        conseils = Conseil.objects.order_by("date", "hour")
        self.assertEqual(list(conseils), [conseil2, conseil1])

    def test_empty_forms_validation(self):
        """Test validation de formulaires complètement vides."""
        cr_form = CRForm(data={})
        self.assertFalse(cr_form.is_valid())

        conseil_form = ConseilForm(data={})
        self.assertFalse(conseil_form.is_valid())
        self.assertIn("date", conseil_form.errors)
        self.assertIn("hour", conseil_form.errors)
        self.assertIn("place", conseil_form.errors)
