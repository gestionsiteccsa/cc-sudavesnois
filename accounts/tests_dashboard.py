"""
Tests TDD pour la refonte UI/UX de /adminccsa/.

Ces tests couvrent le Lot 1 (quick wins) :
- Accessibilite : skip-link, main landmark, aria-expanded
- Nouvelles statistiques affichees sur le dashboard
- Lien "Tableau de bord" dans la sidebar
- Champ de recherche dans la sidebar
- Optimisation SQL : nombre de requetes borne
- Securite : endpoints proteges contre les anonymes/non-superusers
"""

from django.test import Client, TestCase
from django.urls import reverse

from accounts.models import CustomUser
from contact.models import ContactEmail

User = CustomUser


SUPERUSER_CREDS = {
    "email": "superadmin@example.com",
    "username": "superadmin",
    "password": "Sup3r-Str0ng-Pa55!",
}

MODERATOR_CREDS = {
    "email": "moderator@example.com",
    "username": "moderator",
    "password": "Mod-Str0ng-Pa55!",
}


def make_superuser():
    return User.objects.create_superuser(
        email=SUPERUSER_CREDS["email"],
        username=SUPERUSER_CREDS["username"],
        password=SUPERUSER_CREDS["password"],
    )


def make_moderator():
    from django.contrib.auth.models import Group

    moderator = User.objects.create_user(
        email=MODERATOR_CREDS["email"],
        username=MODERATOR_CREDS["username"],
        password=MODERATOR_CREDS["password"],
    )
    group, _ = Group.objects.get_or_create(name="moderator")
    moderator.groups.add(group)
    return moderator


class AdminDashboardAccessTests(TestCase):
    """Securite : l'acces au dashboard est protege."""

    def setUp(self):
        self.client = Client()
        self.url = reverse("accounts:admin_dashboard")

    def test_anonymous_is_redirected(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("accounts:login"), response.url)

    def test_authenticated_non_moderator_is_forbidden(self):
        User.objects.create_user(
            email="user@example.com",
            username="regular",
            password="Plain-Pa55-word!",
        )
        self.client.login(username="user@example.com", password="Plain-Pa55-word!")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)


class AdminDashboardStatsTests(TestCase):
    """Le dashboard expose toutes les nouvelles stats."""

    @classmethod
    def setUpTestData(cls):
        from django.core.files.uploadedfile import SimpleUploadedFile

        from bureau_communautaire.models import Document, Elus
        from commissions.models import Commission
        from conseil_communautaire.models import ConseilMembre, ConseilVille
        from journal.models import Journal
        from services.models import Service

        cls.superuser = make_superuser()
        ville = ConseilVille.objects.create(
            city_name="Ville Test",
            mayor_sex=ConseilVille.Sexe.Monsieur,
            mayor_first_name="Jean",
            mayor_last_name="DUPONT",
            address="1 rue de la Mairie",
            postal_code="59000",
            phone_number="0312345678",
            image=SimpleUploadedFile(
                "city.png", b"\x89PNG\r\n\x1a\n", content_type="image/png"
            ),
            nb_habitants=1000,
        )
        ConseilMembre.objects.create(
            first_name="Jean",
            last_name="DUPONT",
            city=ville,
        )
        Service.objects.create(
            title="Service Test",
            content="Desc",
            icon="icofont-test",
        )
        Commission.objects.create(title="Commission Test", icon="<svg></svg>")
        Journal.objects.create(
            title="Journal Test",
            number=1,
            release_date="2025-01-01",
            document=SimpleUploadedFile(
                "test.pdf", b"%PDF-1.4 fake", content_type="application/pdf"
            ),
            cover=SimpleUploadedFile(
                "cover.png", b"\x89PNG\r\n\x1a\n", content_type="image/png"
            ),
        )
        Elus.objects.create(
            first_name="Marie",
            last_name="CURIE",
            city=ville,
            picture=SimpleUploadedFile(
                "elu.png", b"\x89PNG\r\n\x1a\n", content_type="image/png"
            ),
        )
        Document.objects.create(
            document=SimpleUploadedFile(
                "doc.pdf", b"%PDF-1.4 fake", content_type="application/pdf"
            ),
            title="Doc Test",
            type="organigramme",
        )
        ContactEmail.objects.create(email="contact1@ccsa.fr", is_active=True)
        ContactEmail.objects.create(email="contact2@ccsa.fr", is_active=False)

    def setUp(self):
        from django.core.cache import cache

        cache.clear()
        self.client = Client()
        self.client.login(
            username=SUPERUSER_CREDS["email"],
            password=SUPERUSER_CREDS["password"],
        )

    def test_dashboard_returns_200(self):
        response = self.client.get(reverse("accounts:admin_dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_exposes_all_stats(self):
        response = self.client.get(reverse("accounts:admin_dashboard"))
        stats = response.context["stats"]
        expected_keys = {
            "users",
            "journals",
            "elus",
            "services",
            "membres",
            "commissions",
            "villes",
            "documents",
            "contacts",
        }
        self.assertTrue(
            expected_keys.issubset(stats.keys()),
            f"Stats manquantes : {expected_keys - set(stats.keys())}",
        )

    def test_dashboard_stats_values_match_db(self):
        from bureau_communautaire.models import Document, Elus
        from commissions.models import Commission
        from conseil_communautaire.models import ConseilMembre, ConseilVille
        from journal.models import Journal
        from services.models import Service

        response = self.client.get(reverse("accounts:admin_dashboard"))
        stats = response.context["stats"]
        self.assertEqual(stats["journals"], Journal.objects.count())
        self.assertEqual(stats["elus"], Elus.objects.count())
        self.assertEqual(stats["services"], Service.objects.count())
        self.assertEqual(stats["membres"], ConseilMembre.objects.count())
        self.assertEqual(stats["commissions"], Commission.objects.count())
        self.assertEqual(stats["villes"], ConseilVille.objects.count())
        self.assertEqual(stats["documents"], Document.objects.count())
        self.assertEqual(stats["contacts"], ContactEmail.objects.count())
        self.assertEqual(stats["users"], User.objects.count())

    def test_dashboard_renders_stat_cards(self):
        response = self.client.get(reverse("accounts:admin_dashboard"))
        for label in [
            "Utilisateurs",
            "Journaux",
            "Élus",
            "Villes",
            "Membres",
            "Commissions",
            "Services",
            "Documents",
        ]:
            self.assertContains(
                response,
                label,
                msg_prefix=f"Carte stat '{label}' absente du dashboard",
            )

    def test_dashboard_excludes_users_for_non_superuser(self):
        self.client.logout()
        make_moderator()
        self.client.login(
            username=MODERATOR_CREDS["email"],
            password=MODERATOR_CREDS["password"],
        )
        response = self.client.get(reverse("accounts:admin_dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("users", response.context["stats"])


class AdminDashboardSQLOptimizationTests(TestCase):
    """Le nombre de requetes SQL sur le dashboard est borne."""

    def setUp(self):
        from django.core.cache import cache

        cache.clear()
        self.client = Client()
        self.superuser = make_superuser()
        self.client.login(
            username=SUPERUSER_CREDS["email"],
            password=SUPERUSER_CREDS["password"],
        )

    def test_dashboard_query_count_is_bounded(self):
        from django.db import connection
        from django.test.utils import CaptureQueriesContext

        url = reverse("accounts:admin_dashboard")
        with CaptureQueriesContext(connection) as ctx:
            response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertLessEqual(
            len(ctx.captured_queries),
            25,
            f"Trop de requetes ({len(ctx.captured_queries)}) sur le dashboard",
        )

    def test_dashboard_uses_cache_for_stats(self):
        from django.core.cache import cache

        cache.clear()
        url = reverse("accounts:admin_dashboard")
        self.client.get(url)
        cached = cache.get("admin_dashboard_stats")
        self.assertIsNotNone(cached, "Les stats doivent etre mises en cache")
        self.assertIn("journals", cached)
        self.assertIn("elus", cached)


class AdminDashboardAccessibilityTests(TestCase):
    """Le template admin_base.html expose les landmarks d'accessibilite."""

    def setUp(self):
        from django.core.cache import cache

        cache.clear()
        self.client = Client()
        self.superuser = make_superuser()
        self.client.login(
            username=SUPERUSER_CREDS["email"],
            password=SUPERUSER_CREDS["password"],
        )

    def test_dashboard_renders_skip_link(self):
        response = self.client.get(reverse("accounts:admin_dashboard"))
        self.assertContains(response, 'href="#main-content"')
        self.assertContains(response, "Aller au contenu")

    def test_dashboard_has_main_landmark(self):
        response = self.client.get(reverse("accounts:admin_dashboard"))
        self.assertContains(response, 'id="main-content"')
        self.assertContains(response, "<main")


class AdminSidebarAccessibilityTests(TestCase):
    """La sidebar expose les attributs ARIA et les aides a la navigation."""

    def setUp(self):
        from django.core.cache import cache

        cache.clear()
        self.client = Client()
        self.superuser = make_superuser()
        self.client.login(
            username=SUPERUSER_CREDS["email"],
            password=SUPERUSER_CREDS["password"],
        )

    def test_sidebar_has_dashboard_link(self):
        response = self.client.get(reverse("accounts:admin_dashboard"))
        self.assertContains(response, 'href="/adminccsa/"')

    def test_sidebar_has_filter_input(self):
        response = self.client.get(reverse("accounts:admin_dashboard"))
        self.assertContains(response, 'id="sidebar-filter"')
        self.assertContains(response, 'aria-label="Filtrer les modules')

    def test_sidebar_sections_have_aria_expanded(self):
        response = self.client.get(reverse("accounts:admin_dashboard"))
        self.assertContains(response, 'aria-expanded="false"')

    def test_sidebar_links_have_data_url_name_for_active_state(self):
        response = self.client.get(reverse("accounts:admin_dashboard"))
        self.assertContains(response, "data-url-name=")

    def test_sidebar_includes_admin_sidebar_js(self):
        response = self.client.get(reverse("accounts:admin_dashboard"))
        # L'URL du script peut etre avec ou sans hash de manifeste
        # (par ex. /static/js/admin_sidebar.fde373b1f04d.js en prod,
        # /static/js/admin_sidebar.js en debug)
        self.assertContains(response, "admin_sidebar")
        self.assertContains(response, ".js")

    def test_messages_have_aria_live(self):
        response = self.client.get(reverse("accounts:admin_dashboard"))
        self.assertContains(response, 'aria-live="polite"')


class AdminSidebarContrastTests(TestCase):
    """Verifie que les classes dark:text-gray-600 problematiques sont remplacees."""

    def setUp(self):
        from django.core.cache import cache

        cache.clear()
        self.client = Client()
        self.superuser = make_superuser()
        self.client.login(
            username=SUPERUSER_CREDS["email"],
            password=SUPERUSER_CREDS["password"],
        )

    def test_no_problematic_contrast_class(self):
        response = self.client.get(reverse("accounts:admin_dashboard"))
        self.assertNotIn(
            "text-gray-600 dark:text-gray-600",
            response.content.decode("utf-8"),
            "La classe dark:text-gray-600 a un contraste insuffisant",
        )
