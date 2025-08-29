from io import StringIO

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.test import Client, TestCase
from django.test.utils import override_settings
from django.urls import reverse

from services.forms import ServiceForm
from services.models import Service

User = get_user_model()
MEDIA_ROOT = "test_media_services"


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class ServiceModelTestCase(TestCase):
    """Tests pour le modèle Service."""

    def test_service_creation(self):
        """Test de création d'un service."""
        service = Service.objects.create(
            title="Test Service",
            content="Description du service de test.",
            icon="<svg>test</svg>",
        )
        self.assertEqual(service.title, "Test Service")
        self.assertEqual(service.content, "Description du service de test.")
        self.assertEqual(service.icon, "<svg>test</svg>")
        self.assertTrue(isinstance(service, Service))

    def test_service_str_method(self):
        """Test de la méthode __str__ du modèle Service."""
        service = Service.objects.create(
            title="Test Service",
            content="Description du service de test.",
            icon="<svg>test</svg>",
        )
        expected_str = "Test Service - Description du service de test."
        self.assertEqual(str(service), expected_str)

    def test_service_title_max_length(self):
        """Test de la longueur maximale du titre."""
        long_title = "x" * 101  # Dépasse la limite de 100 caractères
        service = Service(
            title=long_title, content="Description", icon="<svg>test</svg>"
        )
        with self.assertRaises(ValidationError):
            service.full_clean()

    def test_service_fields_required(self):
        """Test que les champs requis sont bien obligatoires."""
        service = Service()
        with self.assertRaises(ValidationError):
            service.full_clean()

    def test_service_content_can_be_long(self):
        """Test que le contenu peut être long (TextField)."""
        long_content = "x" * 1000
        service = Service.objects.create(
            title="Test Service", content=long_content, icon="<svg>test</svg>"
        )
        self.assertEqual(len(service.content), 1000)


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class ServiceFormTestCase(TestCase):
    """Tests pour le formulaire ServiceForm."""

    def test_service_form_valid_data(self):
        """Test du formulaire avec des données valides."""
        form_data = {
            "title": "Test Service",
            "content": "Description du service de test.",
            "icon": '<svg xmlns="http://www.w3.org/2000/svg"><path/></svg>',
        }
        form = ServiceForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_service_form_missing_title(self):
        """Test du formulaire sans titre."""
        form_data = {
            "content": "Description du service de test.",
            "icon": '<svg xmlns="http://www.w3.org/2000/svg"><path/></svg>',
        }
        form = ServiceForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)

    def test_service_form_missing_icon(self):
        """Test du formulaire sans icône."""
        form_data = {
            "title": "Test Service",
            "content": "Description du service de test.",
        }
        form = ServiceForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("icon", form.errors)

    def test_service_form_content_optional(self):
        """Test que le contenu est optionnel."""
        form_data = {
            "title": "Test Service",
            "content": "",  # Contenu vide
            "icon": '<svg xmlns="http://www.w3.org/2000/svg"><path/></svg>',
        }
        form = ServiceForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_service_form_widgets(self):
        """Test des widgets du formulaire."""
        form = ServiceForm()
        self.assertIn("form-control", form.fields["title"].widget.attrs["class"])
        self.assertIn("placeholder", form.fields["title"].widget.attrs)
        self.assertIn("form-control", form.fields["icon"].widget.attrs["class"])

    def test_service_form_help_text(self):
        """Test du texte d'aide du formulaire."""
        form = ServiceForm()
        self.assertEqual(form.fields["content"].help_text, "Description du service")

    def test_service_form_save(self):
        """Test de la sauvegarde du formulaire."""
        form_data = {
            "title": "Test Service",
            "content": "Description du service de test.",
            "icon": '<svg xmlns="http://www.w3.org/2000/svg"><path/></svg>',
        }
        form = ServiceForm(data=form_data)
        self.assertTrue(form.is_valid())
        service = form.save()
        self.assertEqual(service.title, "Test Service")
        self.assertEqual(Service.objects.count(), 1)


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class ServiceViewsTestCase(TestCase):
    """Tests pour les vues de l'application services."""

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
        self.service_data = {
            "title": "Test Service",
            "content": "Description du service de test.",
            "icon": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 512"><path fill="#fff" d="M74.6 373.2c41.7 36.1 108 82.5 166.1 73.7z"/></svg>',
        }

    def test_service_list_view_authenticated_superuser(self):
        """Test de la vue liste avec superutilisateur."""
        self.client.login(email=self.superuser.email, password="adminpassword")
        Service.objects.create(**self.service_data)

        response = self.client.get(reverse("services:admin_services_list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "services/service-list.html")
        self.assertContains(response, "Test Service")
        self.assertIn("services", response.context)

    def test_service_list_view_no_services(self):
        """Test de la vue liste sans services."""
        self.client.login(email=self.superuser.email, password="adminpassword")

        response = self.client.get(reverse("services:admin_services_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Aucun service n'a été créé pour le moment.")
        self.assertIsNone(response.context["services"])

    def test_service_list_view_permission_required(self):
        """Test que la vue liste nécessite les permissions."""
        response = self.client.get(reverse("services:admin_services_list"))
        self.assertEqual(response.status_code, 302)  # Redirection vers login

    def test_add_service_view_get(self):
        """Test de l'affichage du formulaire d'ajout."""
        self.client.login(email=self.superuser.email, password="adminpassword")

        response = self.client.get(reverse("services:add_service"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "services/ajout-service.html")
        self.assertIn("service_form", response.context)
        self.assertIsInstance(response.context["service_form"], ServiceForm)

    def test_add_service_view_post_valid(self):
        """Test d'ajout d'un service avec données valides."""
        self.client.login(email=self.superuser.email, password="adminpassword")

        response = self.client.post(reverse("services:add_service"), self.service_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("services:admin_services_list"))
        self.assertEqual(Service.objects.count(), 1)
        self.assertEqual(Service.objects.first().title, "Test Service")

    def test_add_service_view_post_invalid(self):
        """Test d'ajout d'un service avec données invalides."""
        self.client.login(email=self.superuser.email, password="adminpassword")
        invalid_data = {"title": "", "content": "", "icon": ""}

        response = self.client.post(reverse("services:add_service"), invalid_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "services/ajout-service.html")
        self.assertIn("service_form", response.context)
        self.assertTrue(response.context["service_form"].errors)
        self.assertEqual(Service.objects.count(), 0)

    def test_add_service_view_permission_required(self):
        """Test que l'ajout nécessite les permissions."""
        response = self.client.post(reverse("services:add_service"), self.service_data)
        self.assertEqual(response.status_code, 302)  # Redirection vers login

    def test_update_service_view_get(self):
        """Test de l'affichage du formulaire de modification."""
        self.client.login(email=self.superuser.email, password="adminpassword")
        service = Service.objects.create(**self.service_data)

        response = self.client.get(
            reverse("services:update_service", args=[service.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "services/modifier-service.html")
        self.assertIn("service_form", response.context)
        self.assertEqual(response.context["service_form"].instance, service)

    def test_update_service_view_post_valid(self):
        """Test de modification d'un service avec données valides."""
        self.client.login(email=self.superuser.email, password="adminpassword")
        service = Service.objects.create(**self.service_data)
        updated_data = self.service_data.copy()
        updated_data["title"] = "Service Modifié"

        response = self.client.post(
            reverse("services:update_service", args=[service.id]), updated_data
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("services:admin_services_list"))
        service.refresh_from_db()
        self.assertEqual(service.title, "Service Modifié")

    def test_update_service_view_post_invalid(self):
        """Test de modification d'un service avec données invalides."""
        self.client.login(email=self.superuser.email, password="adminpassword")
        service = Service.objects.create(**self.service_data)
        invalid_data = {"title": "", "content": "", "icon": ""}

        response = self.client.post(
            reverse("services:update_service", args=[service.id]), invalid_data
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "services/modifier-service.html")
        self.assertTrue(response.context["service_form"].errors)

    def test_update_service_view_not_found(self):
        """Test de modification d'un service inexistant."""
        self.client.login(email=self.superuser.email, password="adminpassword")

        response = self.client.get(reverse("services:update_service", args=[999]))
        self.assertEqual(response.status_code, 404)

    def test_update_service_view_permission_required(self):
        """Test que la modification nécessite les permissions."""
        service = Service.objects.create(**self.service_data)

        response = self.client.post(
            reverse("services:update_service", args=[service.id]), self.service_data
        )
        self.assertEqual(response.status_code, 302)  # Redirection vers login

    def test_delete_service_view_get(self):
        """Test de l'affichage de la confirmation de suppression."""
        self.client.login(email=self.superuser.email, password="adminpassword")
        service = Service.objects.create(**self.service_data)

        response = self.client.get(
            reverse("services:delete_service", args=[service.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "services/supprimer-service.html")
        self.assertEqual(response.context["service"], service)

    def test_delete_service_view_post(self):
        """Test de suppression d'un service."""
        self.client.login(email=self.superuser.email, password="adminpassword")
        service = Service.objects.create(**self.service_data)

        response = self.client.post(
            reverse("services:delete_service", args=[service.id])
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("services:admin_services_list"))
        self.assertEqual(Service.objects.count(), 0)

    def test_delete_service_view_not_found(self):
        """Test de suppression d'un service inexistant."""
        self.client.login(email=self.superuser.email, password="adminpassword")

        response = self.client.get(reverse("services:delete_service", args=[999]))
        self.assertEqual(response.status_code, 404)

    def test_delete_service_view_permission_required(self):
        """Test que la suppression nécessite les permissions."""
        service = Service.objects.create(**self.service_data)

        response = self.client.post(
            reverse("services:delete_service", args=[service.id])
        )
        self.assertEqual(response.status_code, 302)  # Redirection vers login


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class ServicePermissionsTestCase(TestCase):
    """Tests pour les permissions de l'application services."""

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
        self.service_data = {
            "title": "Test Service",
            "content": "Description du service de test.",
            "icon": "<svg>test</svg>",
        }

    def test_staff_user_with_permissions(self):
        """Test qu'un utilisateur staff avec permissions peut accéder."""
        # Donner les permissions nécessaires
        permissions = Permission.objects.filter(
            content_type__app_label="services",
            codename__in=[
                "add_service",
                "change_service",
                "delete_service",
                "view_service",
            ],
        )
        self.staff_user.user_permissions.set(permissions)

        self.client.login(email=self.staff_user.email, password="staffpassword")

        # Test accès à la liste
        response = self.client.get(reverse("services:admin_services_list"))
        self.assertEqual(response.status_code, 200)

        # Test ajout
        response = self.client.get(reverse("services:add_service"))
        self.assertEqual(response.status_code, 200)

    def test_staff_user_without_permissions(self):
        """Test qu'un utilisateur staff sans permissions ne peut pas accéder."""
        self.client.login(email=self.staff_user.email, password="staffpassword")

        response = self.client.get(reverse("services:admin_services_list"))
        # Django redirige vers login même pour les utilisateurs staff sans permissions
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_regular_user_no_access(self):
        """Test qu'un utilisateur normal ne peut pas accéder."""
        self.client.login(email=self.regular_user.email, password="userpassword")

        response = self.client.get(reverse("services:admin_services_list"))
        # Django redirige vers login pour les utilisateurs normaux
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_anonymous_user_redirect(self):
        """Test qu'un utilisateur anonyme est redirigé."""
        response = self.client.get(reverse("services:admin_services_list"))
        self.assertEqual(response.status_code, 302)  # Redirect to login


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class ServiceIntegrationTestCase(TestCase):
    """Tests d'intégration pour l'application services."""

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

    def test_complete_service_workflow(self):
        """Test du workflow complet : création -> modification -> suppression."""
        # 1. Créer un service
        service_data = {
            "title": "Service Workflow",
            "content": "Description initiale",
            "icon": "<svg>workflow</svg>",
        }

        response = self.client.post(reverse("services:add_service"), service_data)
        self.assertEqual(response.status_code, 302)
        service = Service.objects.get(title="Service Workflow")

        # 2. Vérifier dans la liste
        response = self.client.get(reverse("services:admin_services_list"))
        self.assertContains(response, "Service Workflow")

        # 3. Modifier le service
        updated_data = service_data.copy()
        updated_data["title"] = "Service Workflow Modifié"
        updated_data["content"] = "Description modifiée"

        response = self.client.post(
            reverse("services:update_service", args=[service.id]), updated_data
        )
        self.assertEqual(response.status_code, 302)

        service.refresh_from_db()
        self.assertEqual(service.title, "Service Workflow Modifié")
        self.assertEqual(service.content, "Description modifiée")

        # 4. Supprimer le service
        response = self.client.post(
            reverse("services:delete_service", args=[service.id])
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Service.objects.count(), 0)

    def test_service_display_on_home_page(self):
        """Test de l'affichage des services sur la page d'accueil."""
        # Créer quelques services
        Service.objects.create(
            title="Service Test 1", content="Description 1", icon="<svg>test1</svg>"
        )
        Service.objects.create(
            title="Service Test 2", content="Description 2", icon="<svg>test2</svg>"
        )

        # Vérifier l'affichage sur la page d'accueil
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Service Test 1")
        self.assertContains(response, "Service Test 2")
        self.assertContains(response, "Description 1")
        self.assertContains(response, "Description 2")

    def test_empty_services_display_on_home(self):
        """Test de l'affichage quand aucun service n'existe."""
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Aucun service n'est disponible pour le moment.")


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class ServiceEdgeCasesTestCase(TestCase):
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

    def test_service_with_special_characters(self):
        """Test avec des caractères spéciaux dans les données."""
        special_data = {
            "title": "Service avec éàü & <script>",
            "content": "Contenu avec \"guillemets\" et 'apostrophes'",
            "icon": '<svg xmlns="http://www.w3.org/2000/svg"><path d="M10,10"/></svg>',
        }

        response = self.client.post(reverse("services:add_service"), special_data)
        self.assertEqual(response.status_code, 302)

        service = Service.objects.get(title="Service avec éàü & <script>")
        self.assertEqual(
            service.content, "Contenu avec \"guillemets\" et 'apostrophes'"
        )

    def test_service_with_very_long_content(self):
        """Test avec un contenu très long."""
        long_content = "Lorem ipsum " * 1000  # Très long contenu
        service_data = {
            "title": "Service Long",
            "content": long_content,
            "icon": "<svg>long</svg>",
        }

        response = self.client.post(reverse("services:add_service"), service_data)
        self.assertEqual(response.status_code, 302)

        service = Service.objects.get(title="Service Long")
        # Vérifier que le contenu est bien long (au moins 10000 caractères)
        self.assertGreater(len(service.content), 10000)

    def test_service_with_empty_content(self):
        """Test avec un contenu vide (optionnel)."""
        service_data = {
            "title": "Service Sans Contenu",
            "content": "",
            "icon": "<svg>empty</svg>",
        }

        response = self.client.post(reverse("services:add_service"), service_data)
        self.assertEqual(response.status_code, 302)

        service = Service.objects.get(title="Service Sans Contenu")
        self.assertEqual(service.content, "")

    def test_service_with_complex_svg_icon(self):
        """Test avec une icône SVG complexe."""
        complex_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 512">
            <defs>
                <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" style="stop-color:rgb(255,255,0);stop-opacity:1" />
                    <stop offset="100%" style="stop-color:rgb(255,0,0);stop-opacity:1" />
                </linearGradient>
            </defs>
            <path fill="url(#grad1)" d="M74.6 373.2c41.7 36.1 108 82.5 166.1 73.7"/>
            <circle cx="50" cy="50" r="40" stroke="black" stroke-width="3" fill="red" />
        </svg>"""

        service_data = {
            "title": "Service SVG Complexe",
            "content": "Service avec SVG complexe",
            "icon": complex_svg,
        }

        response = self.client.post(reverse("services:add_service"), service_data)
        self.assertEqual(response.status_code, 302)

        service = Service.objects.get(title="Service SVG Complexe")
        self.assertEqual(service.icon, complex_svg)

    def test_multiple_services_ordering(self):
        """Test de l'ordre des services dans la liste."""
        # Créer des services dans un ordre spécifique
        Service.objects.create(title="Zèbre Service", content="Z", icon="<svg>z</svg>")
        Service.objects.create(title="Alpha Service", content="A", icon="<svg>a</svg>")
        Service.objects.create(title="Beta Service", content="B", icon="<svg>b</svg>")

        response = self.client.get(reverse("services:admin_services_list"))
        self.assertEqual(response.status_code, 200)

        # Vérifier que les services sont triés par titre
        services = response.context["services"]
        titles = [service.title for service in services]
        self.assertEqual(titles, ["Alpha Service", "Beta Service", "Zèbre Service"])
