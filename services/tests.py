import json

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import Client, TestCase
from django.test.utils import override_settings
from django.urls import reverse

from services.forms import ServiceForm
from services.models import Service

User = get_user_model()
MEDIA_ROOT = "test_media_services"


class ServiceModelTestCase(TestCase):
    """Tests pour le modèle Service."""

    def test_service_creation(self):
        """Test de création d'un service."""
        service = Service.objects.create(
            title="Test Service",
            content="Description du service de test.",
            icon="<svg><path/></svg>",
        )
        self.assertEqual(service.title, "Test Service")
        self.assertEqual(service.content, "Description du service de test.")
        # Audit trail
        self.assertIsNotNone(service.created_at)
        self.assertIsNotNone(service.updated_at)

    def test_service_str_method_truncates_content(self):
        """__str__ tronque le content pour éviter les logs explosifs."""
        long_content = "x" * 200
        service = Service.objects.create(
            title="Test", content=long_content, icon="<svg><path/></svg>"
        )
        s = str(service)
        self.assertIn("Test", s)
        self.assertLessEqual(len(s), 60)

    def test_service_title_max_length(self):
        """Test que le titre ne peut pas dépasser 100 caractères."""
        service = Service.objects.create(
            title="A" * 100, content="x", icon="<svg><path/></svg>"
        )
        self.assertEqual(len(service.title), 100)

    def test_service_content_can_be_long(self):
        """Test que le contenu peut être long (TextField)."""
        long_content = "x" * 1000
        service = Service.objects.create(
            title="Test Service",
            content=long_content,
            icon="<svg><path/></svg>",
        )
        self.assertEqual(len(service.content), 1000)


class ServiceFormTestCase(TestCase):
    """Tests pour le formulaire ServiceForm."""

    VALID_SVG = '<svg xmlns="http://www.w3.org/2000/svg"><path/></svg>'

    def test_service_form_valid_data(self):
        form_data = {
            "title": "Test Service",
            "content": "Description du service de test.",
            "icon": self.VALID_SVG,
        }
        form = ServiceForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors.as_json())

    def test_service_form_missing_title(self):
        form_data = {"content": "x", "icon": self.VALID_SVG}
        form = ServiceForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)

    def test_service_form_missing_icon(self):
        form_data = {"title": "Test", "content": "x"}
        form = ServiceForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("icon", form.errors)

    def test_service_form_content_optional(self):
        form_data = {
            "title": "Test Service",
            "content": "",
            "icon": self.VALID_SVG,
        }
        form = ServiceForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors.as_json())

    def test_service_form_widgets(self):
        form = ServiceForm()
        self.assertIn("form-control", form.fields["title"].widget.attrs["class"])
        self.assertIn("placeholder", form.fields["title"].widget.attrs)
        self.assertIn("form-control", form.fields["icon"].widget.attrs["class"])
        self.assertIn("rows", form.fields["icon"].widget.attrs)

    def test_service_form_help_text(self):
        form = ServiceForm()
        self.assertIn("Description", form.fields["content"].help_text)

    def test_service_form_save(self):
        form_data = {
            "title": "Test Service",
            "content": "Description du service de test.",
            "icon": self.VALID_SVG,
        }
        form = ServiceForm(data=form_data)
        self.assertTrue(form.is_valid())
        service = form.save()
        self.assertEqual(service.title, "Test Service")
        self.assertEqual(Service.objects.count(), 1)

    # ---- Tests de sécurité XSS ----

    def test_icon_rejects_script_tag(self):
        """Une balise <script> dans l'icône doit être rejetée."""
        form = ServiceForm(
            data={
                "title": "x",
                "content": "",
                "icon": "<svg><script>alert(1)</script></svg>",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("icon", form.errors)

    def test_icon_rejects_javascript_uri(self):
        form = ServiceForm(
            data={
                "title": "x",
                "content": "",
                "icon": "<svg><a href='javascript:alert(1)'>x</a></svg>",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("icon", form.errors)

    def test_icon_rejects_on_event_handler(self):
        form = ServiceForm(
            data={
                "title": "x",
                "content": "",
                "icon": '<svg onload="alert(1)"></svg>',
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("icon", form.errors)

    def test_icon_rejects_iframe(self):
        form = ServiceForm(
            data={
                "title": "x",
                "content": "",
                "icon": '<svg><iframe src="evil.com"></iframe></svg>',
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("icon", form.errors)

    def test_icon_rejects_non_svg_html(self):
        """Du HTML non-SVG doit être rejeté même sans mot-clé dangereux."""
        form = ServiceForm(
            data={
                "title": "x",
                "content": "",
                "icon": "<div>test</div>",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("icon", form.errors)

    def test_icon_rejects_data_uri(self):
        form = ServiceForm(
            data={
                "title": "x",
                "content": "",
                "icon": '<svg><a xlink:href="data:text/html,<script>">x</a></svg>',
            }
        )
        self.assertFalse(form.is_valid())

    def test_icon_accepts_complex_valid_svg(self):
        """Un SVG avec <defs>, <linearGradient>, etc. doit être accepté."""
        complex_svg = (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 512">'
            '<defs><linearGradient id="g1"><stop offset="0%"/></linearGradient></defs>'
            '<path fill="url(#g1)" d="M0 0"/></svg>'
        )
        form = ServiceForm(data={"title": "x", "content": "", "icon": complex_svg})
        self.assertTrue(form.is_valid(), form.errors.as_json())

    def test_icon_strips_whitespace(self):
        form = ServiceForm(
            data={
                "title": "x",
                "content": "",
                "icon": "  <svg><path/></svg>  \n",
            }
        )
        self.assertTrue(form.is_valid(), form.errors.as_json())
        self.assertFalse(form.cleaned_data["icon"].startswith(" "))


class SvgRenderFilterTestCase(TestCase):
    """
    Vérifie le filtre ``render_svg`` : le contenu SVG validé est marqué
    ``mark_safe`` pour contourner l'auto-escape Django (nécessaire car
    le SVG contient des ``<path>``, ``<circle>``, etc.).
    """

    def test_valid_svg_is_marked_safe(self):
        from django.utils.safestring import SafeString

        from services.templatetags.svg_tags import render_svg

        result = render_svg('<svg viewBox="0 0 24 24"><path d="M0 0"/></svg>')
        self.assertIsInstance(result, SafeString)

    def test_empty_value_returns_empty_string(self):
        from services.templatetags.svg_tags import render_svg

        self.assertEqual(render_svg(""), "")
        self.assertEqual(render_svg(None), "")

    def test_dangerous_content_returns_empty_string(self):
        from services.templatetags.svg_tags import render_svg

        # Defense in depth : si du contenu malicieux était inséré en DB
        # avant le déploiement de la validation, le filtre le neutralise.
        self.assertEqual(
            render_svg("<svg><script>alert(1)</script></svg>"),
            "",
        )
        self.assertEqual(
            render_svg('<svg onload="alert(1)"></svg>'),
            "",
        )
        self.assertEqual(
            render_svg("<div>not an svg</div>"),
            "",
        )

    def test_svg_rendered_in_list_template(self):
        """Vérifie que l'icône SVG est bien rendue (non échappée) dans la liste admin."""
        from django.contrib.auth import get_user_model

        User = get_user_model()
        superuser = User.objects.create_superuser(
            email="admin@exemple.com", password="adminpassword"
        )
        Service.objects.create(
            title="Avec icône",
            content="",
            icon='<svg viewBox="0 0 24 24"><path d="M0 0L10 10"/></svg>',
        )
        self.client.login(email="admin@exemple.com", password="adminpassword")
        response = self.client.get(reverse("services:admin_services_list"))
        self.assertEqual(response.status_code, 200)
        # Le rendu doit contenir la balise <svg> (non échappée en &lt;svg&gt;)
        self.assertContains(response, '<svg viewBox="0 0 24 24">')
        self.assertNotContains(response, "&lt;svg viewBox=")


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class ServiceViewsTestCase(TestCase):
    """Tests pour les vues de l'application services."""

    VALID_SVG = '<svg xmlns="http://www.w3.org/2000/svg"><path/></svg>'

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
        self.client = Client()
        self.service_data = {
            "title": "Test Service",
            "content": "Description du service de test.",
            "icon": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 512"><path fill="#fff" d="M0 0"/></svg>',
        }

    def test_service_list_view_authenticated_superuser(self):
        self.client.login(email=self.superuser.email, password="adminpassword")
        Service.objects.create(**self.service_data)

        response = self.client.get(reverse("services:admin_services_list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "services/service-list.html")
        self.assertContains(response, "Test Service")
        self.assertIn("services", response.context)

    def test_service_list_view_no_services(self):
        """Liste vide : QuerySet vide (pas None) et message d'état vide."""
        self.client.login(email=self.superuser.email, password="adminpassword")
        response = self.client.get(reverse("services:admin_services_list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["services"]), 0)
        self.assertContains(response, "Aucun service pour le moment")

    def test_service_list_view_uses_aggregate(self):
        """Le context fournit total/with_desc/without_desc calculés en 1 aggregate."""
        self.client.login(email=self.superuser.email, password="adminpassword")
        Service.objects.create(**self.service_data)
        Service.objects.create(title="Sans desc", content="", icon=self.VALID_SVG)
        response = self.client.get(reverse("services:admin_services_list"))
        self.assertEqual(response.context["total"], 2)
        self.assertEqual(response.context["with_desc"], 1)
        self.assertEqual(response.context["without_desc"], 1)

    def test_service_list_view_permission_required(self):
        response = self.client.get(reverse("services:admin_services_list"))
        self.assertEqual(response.status_code, 302)

    def test_add_service_view_get(self):
        self.client.login(email=self.superuser.email, password="adminpassword")
        response = self.client.get(reverse("services:add_service"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "services/ajout-service.html")
        self.assertIsInstance(response.context["service_form"], ServiceForm)

    def test_add_service_view_post_valid(self):
        self.client.login(email=self.superuser.email, password="adminpassword")
        response = self.client.post(reverse("services:add_service"), self.service_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("services:admin_services_list"))
        self.assertEqual(Service.objects.count(), 1)

    def test_add_service_view_post_invalid(self):
        self.client.login(email=self.superuser.email, password="adminpassword")
        invalid_data = {"title": "", "content": "", "icon": ""}
        response = self.client.post(reverse("services:add_service"), invalid_data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["service_form"].errors)
        self.assertEqual(Service.objects.count(), 0)

    def test_add_service_view_post_xss_blocked(self):
        """Un POST avec <script> dans l'icône doit être rejeté."""
        self.client.login(email=self.superuser.email, password="adminpassword")
        data = {
            "title": "x",
            "content": "",
            "icon": "<svg><script>alert(1)</script></svg>",
        }
        response = self.client.post(reverse("services:add_service"), data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Service.objects.exists())

    def test_add_service_view_permission_required(self):
        response = self.client.post(reverse("services:add_service"), self.service_data)
        self.assertEqual(response.status_code, 302)

    def test_update_service_view_get(self):
        self.client.login(email=self.superuser.email, password="adminpassword")
        service = Service.objects.create(**self.service_data)
        response = self.client.get(
            reverse("services:update_service", args=[service.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "services/modifier-service.html")
        self.assertEqual(response.context["service_form"].instance, service)

    def test_update_service_view_post_valid(self):
        self.client.login(email=self.superuser.email, password="adminpassword")
        service = Service.objects.create(**self.service_data)
        updated_data = self.service_data.copy()
        updated_data["title"] = "Service Modifié"
        response = self.client.post(
            reverse("services:update_service", args=[service.id]), updated_data
        )
        self.assertEqual(response.status_code, 302)
        service.refresh_from_db()
        self.assertEqual(service.title, "Service Modifié")
        # Le message de succès utilise le nouveau titre
        self.assertTrue(
            any("Service Modifié" in m.message for m in response.wsgi_request._messages)
        )

    def test_update_service_view_post_invalid(self):
        self.client.login(email=self.superuser.email, password="adminpassword")
        service = Service.objects.create(**self.service_data)
        invalid_data = {"title": "", "content": "", "icon": ""}
        response = self.client.post(
            reverse("services:update_service", args=[service.id]), invalid_data
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["service_form"].errors)

    def test_update_service_view_not_found(self):
        self.client.login(email=self.superuser.email, password="adminpassword")
        response = self.client.get(reverse("services:update_service", args=[999]))
        self.assertEqual(response.status_code, 404)

    def test_update_service_view_permission_required(self):
        service = Service.objects.create(**self.service_data)
        response = self.client.post(
            reverse("services:update_service", args=[service.id]), self.service_data
        )
        self.assertEqual(response.status_code, 302)

    def test_delete_service_view_get_is_rejected(self):
        """Le GET sur /supprimer-service/ doit être rejeté (405 ou 302)."""
        self.client.login(email=self.superuser.email, password="adminpassword")
        service = Service.objects.create(**self.service_data)
        response = self.client.get(
            reverse("services:delete_service", args=[service.id])
        )
        # require_POST renvoie 405 Method Not Allowed
        self.assertEqual(response.status_code, 405)
        self.assertTrue(Service.objects.filter(id=service.id).exists())

    def test_delete_service_view_post(self):
        self.client.login(email=self.superuser.email, password="adminpassword")
        service = Service.objects.create(**self.service_data)
        response = self.client.post(
            reverse("services:delete_service", args=[service.id])
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("services:admin_services_list"))
        self.assertEqual(Service.objects.count(), 0)

    def test_delete_service_view_not_found(self):
        self.client.login(email=self.superuser.email, password="adminpassword")
        response = self.client.post(reverse("services:delete_service", args=[999]))
        self.assertEqual(response.status_code, 404)

    def test_delete_service_view_permission_required(self):
        service = Service.objects.create(**self.service_data)
        response = self.client.post(
            reverse("services:delete_service", args=[service.id])
        )
        self.assertEqual(response.status_code, 302)


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class ReorderServicesTestCase(TestCase):
    """Tests de l'endpoint AJAX reorder."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.superuser = User.objects.create_superuser(
            email="admin@exemple.com", password="adminpassword"
        )
        cls.regular_user = User.objects.create_user(
            email="user@exemple.com", password="userpassword"
        )

    def setUp(self):
        self.client = Client()
        self.s1 = Service.objects.create(
            title="A", content="", icon="<svg><path/></svg>"
        )
        self.s2 = Service.objects.create(
            title="B", content="", icon="<svg><path/></svg>"
        )
        self.s3 = Service.objects.create(
            title="C", content="", icon="<svg><path/></svg>"
        )
        self.url = reverse("services:reorder_services")

    def test_reorder_success_applies_new_order(self):
        self.client.login(email=self.superuser.email, password="adminpassword")
        response = self.client.post(
            self.url,
            data=json.dumps({"order": [self.s3.id, self.s1.id, self.s2.id]}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"success": True})
        self.s1.refresh_from_db()
        self.s2.refresh_from_db()
        self.s3.refresh_from_db()
        self.assertEqual(self.s3.order, 0)
        self.assertEqual(self.s1.order, 1)
        self.assertEqual(self.s2.order, 2)

    def test_reorder_uses_bulk_update_single_query(self):
        """Le reorder doit effectuer 1 SELECT + 1 bulk_update, pas N UPDATE."""
        from django.db import connection
        from django.test.utils import CaptureQueriesContext

        self.client.login(email=self.superuser.email, password="adminpassword")
        with CaptureQueriesContext(connection) as ctx:
            self.client.post(
                self.url,
                data=json.dumps({"order": [self.s3.id, self.s1.id, self.s2.id]}),
                content_type="application/json",
            )
        # 1 SAVEPOINT + 1 SELECT + 1 UPDATE (bulk) + RELEASE
        update_queries = [
            q
            for q in ctx.captured_queries
            if "UPDATE" in q["sql"] and "services_service" in q["sql"]
        ]
        self.assertEqual(
            len(update_queries),
            1,
            f"Attendu 1 UPDATE, obtenu {len(update_queries)}: "
            f"{[q['sql'] for q in update_queries]}",
        )

    def test_reorder_invalid_json_returns_400(self):
        self.client.login(email=self.superuser.email, password="adminpassword")
        response = self.client.post(
            self.url,
            data="not json",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())

    def test_reorder_missing_order_key_returns_400(self):
        self.client.login(email=self.superuser.email, password="adminpassword")
        response = self.client.post(
            self.url,
            data=json.dumps({"foo": [1, 2]}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_reorder_too_many_ids_returns_400(self):
        self.client.login(email=self.superuser.email, password="adminpassword")
        response = self.client.post(
            self.url,
            data=json.dumps({"order": list(range(1, 1002))}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_reorder_negative_id_rejected(self):
        self.client.login(email=self.superuser.email, password="adminpassword")
        response = self.client.post(
            self.url,
            data=json.dumps({"order": [self.s1.id, -1, self.s2.id]}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_reorder_string_id_rejected(self):
        self.client.login(email=self.superuser.email, password="adminpassword")
        response = self.client.post(
            self.url,
            data=json.dumps({"order": [self.s1.id, "abc", self.s2.id]}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_reorder_non_existent_id_rejected(self):
        self.client.login(email=self.superuser.email, password="adminpassword")
        response = self.client.post(
            self.url,
            data=json.dumps({"order": [self.s1.id, 99999, self.s2.id]}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_reorder_does_not_disclose_internal_error(self):
        """Une erreur interne ne doit pas exposer str(e) au client."""
        self.client.login(email=self.superuser.email, password="adminpassword")
        with self.assertLogs("services.views", level="ERROR") as captured:
            from unittest.mock import patch

            from django.db import OperationalError

            with patch(
                "services.views.Service.objects.bulk_update",
                side_effect=OperationalError("secret column foo_bar"),
            ):
                response = self.client.post(
                    self.url,
                    data=json.dumps({"order": [self.s1.id, self.s2.id, self.s3.id]}),
                    content_type="application/json",
                )
        self.assertEqual(response.status_code, 500)
        body = response.content.decode()
        self.assertNotIn("foo_bar", body)
        self.assertNotIn("OperationalError", body)
        self.assertTrue(
            any("reorder_services" in r.getMessage() for r in captured.records)
        )

    def test_reorder_requires_post(self):
        self.client.login(email=self.superuser.email, password="adminpassword")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)

    def test_reorder_requires_change_service_permission(self):
        self.client.login(email=self.regular_user.email, password="userpassword")
        response = self.client.post(
            self.url,
            data=json.dumps({"order": [self.s1.id, self.s2.id, self.s3.id]}),
            content_type="application/json",
        )
        # @permission_required redirige les utilisateurs authentifiés sans
        # permission vers la page de login (302), ne lève pas 403.
        self.assertEqual(response.status_code, 302)


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
        self.client = Client()
        self.service_data = {
            "title": "Test Service",
            "content": "Description du service de test.",
            "icon": "<svg><path/></svg>",
        }

    def test_staff_user_with_permissions(self):
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

        response = self.client.get(reverse("services:admin_services_list"))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse("services:add_service"))
        self.assertEqual(response.status_code, 200)

    def test_staff_user_without_permissions(self):
        self.client.login(email=self.staff_user.email, password="staffpassword")
        response = self.client.get(reverse("services:admin_services_list"))
        self.assertEqual(response.status_code, 302)

    def test_regular_user_no_access(self):
        self.client.login(email=self.regular_user.email, password="userpassword")
        response = self.client.get(reverse("services:admin_services_list"))
        self.assertEqual(response.status_code, 302)

    def test_anonymous_user_redirect(self):
        response = self.client.get(reverse("services:admin_services_list"))
        self.assertEqual(response.status_code, 302)


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class ServiceIntegrationTestCase(TestCase):
    """Tests d'intégration pour l'application services."""

    VALID_SVG = '<svg xmlns="http://www.w3.org/2000/svg"><path/></svg>'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.superuser = User.objects.create_superuser(
            email="admin@exemple.com", password="adminpassword"
        )

    def setUp(self):
        self.client = Client()
        self.client.login(email=self.superuser.email, password="adminpassword")

    def test_complete_service_workflow(self):
        service_data = {
            "title": "Service Workflow",
            "content": "Description initiale",
            "icon": self.VALID_SVG,
        }
        response = self.client.post(reverse("services:add_service"), service_data)
        self.assertEqual(response.status_code, 302)
        service = Service.objects.get(title="Service Workflow")

        response = self.client.get(reverse("services:admin_services_list"))
        self.assertContains(response, "Service Workflow")

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

        response = self.client.post(
            reverse("services:delete_service", args=[service.id])
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Service.objects.count(), 0)

    def test_service_with_special_characters_in_title(self):
        """Les caractères Unicode et spéciaux dans le titre sont préservés."""
        data = {
            "title": "Service avec éàü & symboles",
            "content": "Contenu avec \"guillemets\" et 'apostrophes'",
            "icon": self.VALID_SVG,
        }
        response = self.client.post(reverse("services:add_service"), data)
        self.assertEqual(response.status_code, 302)
        service = Service.objects.get(title="Service avec éàü & symboles")
        self.assertEqual(
            service.content, "Contenu avec \"guillemets\" et 'apostrophes'"
        )

    def test_service_with_very_long_content(self):
        long_content = "Lorem ipsum " * 1000
        service_data = {
            "title": "Service Long",
            "content": long_content,
            "icon": self.VALID_SVG,
        }
        response = self.client.post(reverse("services:add_service"), service_data)
        self.assertEqual(response.status_code, 302)
        service = Service.objects.get(title="Service Long")
        self.assertGreater(len(service.content), 10000)

    def test_service_with_empty_content(self):
        service_data = {
            "title": "Service Sans Contenu",
            "content": "",
            "icon": self.VALID_SVG,
        }
        response = self.client.post(reverse("services:add_service"), service_data)
        self.assertEqual(response.status_code, 302)
        service = Service.objects.get(title="Service Sans Contenu")
        self.assertEqual(service.content, "")

    def test_service_with_complex_svg_icon(self):
        complex_svg = (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 512">'
            '<defs><linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="0%">'
            '<stop offset="0%" style="stop-color:rgb(255,255,0)"/>'
            '<stop offset="100%" style="stop-color:rgb(255,0,0)"/>'
            "</linearGradient></defs>"
            '<path fill="url(#grad1)" d="M74.6 373.2c41.7 36.1 108 82.5 166.1 73.7"/>'
            '<circle cx="50" cy="50" r="40" stroke="black" stroke-width="3" fill="red"/>'
            "</svg>"
        )
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
        Service.objects.create(
            title="Zèbre Service", content="", icon="<svg><path/></svg>"
        )
        Service.objects.create(
            title="Alpha Service", content="", icon="<svg><path/></svg>"
        )
        Service.objects.create(
            title="Beta Service", content="", icon="<svg><path/></svg>"
        )

        response = self.client.get(reverse("services:admin_services_list"))
        self.assertEqual(response.status_code, 200)
        services = response.context["services"]
        titles = [service.title for service in services]
        self.assertEqual(titles, ["Alpha Service", "Beta Service", "Zèbre Service"])
