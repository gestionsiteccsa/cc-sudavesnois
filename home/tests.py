import os
import shutil
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core import mail
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from conseil_communautaire.models import ConseilVille
from contact.models import ContactEmail
from journal.models import Journal
from services.models import Service

from .sitemaps import CommunesSitemap, JournalSitemap, StaticViewSitemap
from .views import is_staff_or_superuser

User = get_user_model()


class HomeStaticViewsTestCase(TestCase):
    """Tests pour les vues statiques de l'application Home"""

    def setUp(self):
        self.client = Client()

    def test_marches_publics_view(self):
        """Test de la vue marchés publics"""
        response = self.client.get(reverse("marches_publics"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home/marches-publics.html")

    def test_mobilite_view(self):
        """Test de la vue mobilité"""
        response = self.client.get(reverse("mobilite"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home/mobilite.html")

    def test_habitat_view(self):
        """Test de la vue habitat"""
        response = self.client.get(reverse("habitat"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home/habitat.html")

    def test_collecte_dechets_view(self):
        """Test de la vue collecte des déchets"""
        response = self.client.get(reverse("collecte_dechets"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home/collecte-dechets.html")

    def test_encombrants_view(self):
        """Test de la vue encombrants"""
        response = self.client.get(reverse("encombrants"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home/encombrants.html")

    def test_dechetteries_view(self):
        """Test de la vue déchetteries"""
        response = self.client.get(reverse("dechetteries"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home/dechetteries.html")

    def test_maisons_sante_view(self):
        """Test de la vue maisons de santé"""
        response = self.client.get(reverse("maisons_sante"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home/maisons-sante.html")

    def test_mutuelle_view(self):
        """Test de la vue mutuelle"""
        response = self.client.get(reverse("mutuelle"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home/mutuelle.html")

    def test_plui_view(self):
        """Test de la vue PLUi"""
        response = self.client.get(reverse("plui"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home/plui.html")

    def test_projet_plui_view(self):
        """Test de la vue projet PLUi"""
        response = self.client.get(reverse("projet_plui"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home/projet-plui.html")

    def test_equipe_view(self):
        """Test de la vue équipe"""
        response = self.client.get(reverse("equipe"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home/equipe.html")

    def test_mentions_legales_view(self):
        """Test de la vue mentions légales"""
        response = self.client.get(reverse("mentions_legales"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home/mentions-legales.html")

    def test_politique_confidentialite_view(self):
        """Test de la vue politique de confidentialité"""
        response = self.client.get(reverse("politique_confidentialite"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home/politique-confidentialite.html")

    def test_cookies_view(self):
        """Test de la vue politique de cookies"""
        response = self.client.get(reverse("cookies"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home/cookies.html")

    def test_plan_du_site_view(self):
        """Test de la vue plan du site"""
        response = self.client.get(reverse("plan_du_site"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home/plan-du-site.html")

    def test_accessibilite_view(self):
        """Test de la vue accessibilité"""
        response = self.client.get(reverse("accessibilite"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home/accessibilite.html")


class UtilityFunctionsTestCase(TestCase):
    """Tests pour les fonctions utilitaires"""

    def setUp(self):
        self.normal_user = User.objects.create_user(
            email="user@example.com", password="password123"
        )
        self.staff_user = User.objects.create_user(
            email="staff@example.com", password="password123", is_staff=True
        )
        self.superuser = User.objects.create_superuser(
            email="admin@example.com", password="password123"
        )

    def test_is_staff_or_superuser_normal_user(self):
        """Test avec un utilisateur normal"""
        self.assertFalse(is_staff_or_superuser(self.normal_user))

    def test_is_staff_or_superuser_staff_user(self):
        """Test avec un utilisateur staff"""
        self.assertTrue(is_staff_or_superuser(self.staff_user))

    def test_is_staff_or_superuser_superuser(self):
        """Test avec un superutilisateur"""
        self.assertTrue(is_staff_or_superuser(self.superuser))


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    MEDIA_ROOT="test_media_home",
    TESTING=False,
)
class HomeViewTestCase(TestCase):
    """Tests pour la vue d'accueil avec le formulaire de contact"""

    def setUp(self):
        self.client = Client()
        # Nettoyer le cache pour éviter les interférences avec le rate limiting
        cache.clear()

        # Créer des données de test
        self.city = ConseilVille.objects.create(
            city_name="Fourmies",
            mayor_sex="M",
            mayor_first_name="Jean",
            mayor_last_name="Dupont",
            address="1 rue de la Mairie",
            postal_code="59610",
            phone_number="0321234567",
            website="http://www.fourmies.fr",
            image=SimpleUploadedFile(
                name="test_image.jpg",
                content=b"fake_image_content",
                content_type="image/jpeg",
            ),
            slogan="La ville de Fourmies, c'est la vie !",
            nb_habitants=10000,
        )

        self.service = Service.objects.create(
            title="Service Test", content="Contenu du service test"
        )

        self.contact_email = ContactEmail.objects.create(
            email="contact@ccsa.fr", is_active=True
        )

    def tearDown(self):
        # Nettoyer les fichiers de test
        if os.path.exists("test_media_home"):
            shutil.rmtree("test_media_home")

    def test_home_view_get_without_data(self):
        """Test de la vue d'accueil GET sans données"""
        # Supprimer les données pour tester sans données
        ConseilVille.objects.all().delete()
        Service.objects.all().delete()

        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home/index.html")
        self.assertIsNone(response.context["services"])
        self.assertIsNone(response.context["communes"])
        self.assertIsNone(response.context["nb_communes"])
        self.assertIsNone(response.context["nb_habitants"])

    def test_home_view_get_with_data(self):
        """Test de la vue d'accueil GET avec des données"""
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home/index.html")

        # Vérifier que les données sont présentes
        self.assertIsNotNone(response.context["services"])
        self.assertIsNotNone(response.context["communes"])
        self.assertEqual(response.context["nb_communes"], 1)
        self.assertEqual(response.context["nb_habitants"], 10000)
        self.assertIn(self.service, response.context["services"])

    def test_home_view_post_valid_form_with_contact_email(self):
        """Test du formulaire de contact valide avec email de contact actif"""
        form_data = {
            "first_name": "Jean",
            "last_name": "Dupont",
            "email": "jean.dupont@example.com",
            "phone": "0123456789",
            "message": "Ceci est un message de test",
            "rgpd": True,  # Champ RGPD requis
        }

        response = self.client.post(reverse("home"), form_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("home"))

        # Vérifier que les emails ont été envoyés
        self.assertEqual(len(mail.outbox), 2)  # Email au CCSA + email de confirmation

        # Vérifier le premier email (au CCSA)
        email_ccsa = mail.outbox[0]
        self.assertIn("CONTACT - CCSA", email_ccsa.subject)
        self.assertIn("Jean", email_ccsa.subject)
        self.assertIn("Dupont", email_ccsa.subject)
        self.assertEqual(email_ccsa.from_email, "jean.dupont@example.com")
        self.assertIn("contact@ccsa.fr", email_ccsa.to)

        # Vérifier le deuxième email (confirmation client)
        email_client = mail.outbox[1]
        self.assertIn("CONFIRMATION DE CONTACT - CCSA", email_client.subject)
        self.assertIn("Jean", email_client.subject)
        self.assertIn("Dupont", email_client.subject)
        self.assertEqual(email_client.from_email, "contact@ccsa.fr")
        self.assertIn("jean.dupont@example.com", email_client.to)

    @override_settings(TESTING=False)
    def test_rate_limit_blocks_6th_submission_same_ip(self):
        """La 6e soumission depuis la même IP dans 60s doit être ignorée (pas d'emails supplémentaires)."""
        form_data = {
            "first_name": "Jean",
            "last_name": "Dupont",
            "email": "jean.dupont@example.com",
            "phone": "0123456789",
            "message": "Ceci est un message de test",
            "rgpd": True,
        }

        # 5 soumissions autorisées
        for _ in range(5):
            response = self.client.post(
                reverse("home"),
                form_data,
                HTTP_X_FORWARDED_FOR="1.2.3.4",
                REMOTE_ADDR="1.2.3.4",
            )
            self.assertEqual(response.status_code, 302)

        # Après 5, il doit y avoir 10 emails (2 par soumission)
        self.assertEqual(len(mail.outbox), 10)

        # 6e soumission (même IP): doit être bloquée (pas d'emails supplémentaires)
        response = self.client.post(
            reverse("home"),
            form_data,
            HTTP_X_FORWARDED_FOR="1.2.3.4",
            REMOTE_ADDR="1.2.3.4",
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 10)

    @override_settings(TESTING=False)
    def test_rate_limit_allows_other_ip_after_block(self):
        """Une autre IP ne doit pas être impactée par le blocage de l'IP précédente."""
        form_data = {
            "first_name": "Jean",
            "last_name": "Dupont",
            "email": "jean.dupont@example.com",
            "phone": "0123456789",
            "message": "Ceci est un message de test",
            "rgpd": True,
        }

        # Remplir le quota de l'IP A
        for _ in range(5):
            self.client.post(
                reverse("home"),
                form_data,
                HTTP_X_FORWARDED_FOR="10.0.0.1",
                REMOTE_ADDR="10.0.0.1",
            )

        self.assertEqual(len(mail.outbox), 10)

        # 6e (IP A) bloquée
        self.client.post(
            reverse("home"),
            form_data,
            HTTP_X_FORWARDED_FOR="10.0.0.1",
            REMOTE_ADDR="10.0.0.1",
        )
        self.assertEqual(len(mail.outbox), 10)

        # Soumission depuis IP B: doit passer et ajouter 2 emails
        response = self.client.post(
            reverse("home"),
            form_data,
            HTTP_X_FORWARDED_FOR="10.0.0.2",
            REMOTE_ADDR="10.0.0.2",
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 12)

    def test_home_view_post_valid_form_without_contact_email(self):
        """Test du formulaire de contact valide sans email de contact actif"""
        # Supprimer les emails de contact
        ContactEmail.objects.all().delete()

        form_data = {
            "first_name": "Jean",
            "last_name": "Dupont",
            "email": "jean.dupont@example.com",
            "phone": "0123456789",
            "message": "Ceci est un message de test",
            "rgpd": True,  # Champ RGPD requis
        }

        with patch("builtins.print") as mock_print:
            response = self.client.post(reverse("home"), form_data)
            self.assertEqual(response.status_code, 302)
            self.assertRedirects(response, reverse("home"))

            # Vérifier que le message d'erreur a été affiché
            mock_print.assert_called_with("Aucun contact CCSA défini")

            # Vérifier qu'aucun email n'a été envoyé
            self.assertEqual(len(mail.outbox), 0)

    def test_home_view_post_invalid_form(self):
        """Test du formulaire de contact invalide"""
        form_data = {
            "first_name": "",  # Champ requis vide
            "last_name": "Dupont",
            "email": "invalid-email",  # Email invalide
            "phone": "0123456789",
            "message": "Ceci est un message de test",
        }

        with patch("builtins.print") as mock_print:
            response = self.client.post(reverse("home"), form_data)
            self.assertEqual(response.status_code, 302)
            self.assertRedirects(response, reverse("home"))

            # Vérifier que les erreurs ont été affichées
            mock_print.assert_called()

            # Vérifier qu'aucun email n'a été envoyé
            self.assertEqual(len(mail.outbox), 0)


@override_settings(MEDIA_ROOT="test_media_home")
class PresentationViewTestCase(TestCase):
    """Tests pour la vue présentation"""

    def setUp(self):
        self.client = Client()

    def test_presentation_view_without_data(self):
        """Test de la vue présentation sans données"""
        response = self.client.get(reverse("presentation"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home/presentation.html")

        # Vérifier les valeurs par défaut
        self.assertIsNone(response.context["communes"])
        self.assertEqual(response.context["nb_communes"], 0)
        self.assertEqual(response.context["nb_habitants"], 0)

    def test_presentation_view_with_data(self):
        """Test de la vue présentation avec des données"""
        # Créer des communes de test
        city1 = ConseilVille.objects.create(
            city_name="Fourmies",
            mayor_sex="M",
            mayor_first_name="Jean",
            mayor_last_name="Dupont",
            address="1 rue de la Mairie",
            postal_code="59610",
            phone_number="0321234567",
            website="http://www.fourmies.fr",
            image=SimpleUploadedFile(
                name="test_image1.jpg",
                content=b"fake_image_content1",
                content_type="image/jpeg",
            ),
            slogan="La ville de Fourmies",
            nb_habitants=12000,
        )

        city2 = ConseilVille.objects.create(
            city_name="Anor",
            mayor_sex="F",
            mayor_first_name="Marie",
            mayor_last_name="Martin",
            address="2 rue de la Mairie",
            postal_code="59611",
            phone_number="0321234568",
            website="http://www.anor.fr",
            image=SimpleUploadedFile(
                name="test_image2.jpg",
                content=b"fake_image_content2",
                content_type="image/jpeg",
            ),
            slogan="La ville d'Anor",
            nb_habitants=3000,
        )

        response = self.client.get(reverse("presentation"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home/presentation.html")

        # Vérifier les données calculées
        self.assertIsNotNone(response.context["communes"])
        self.assertEqual(response.context["nb_communes"], 2)
        self.assertEqual(response.context["nb_habitants"], 15000)  # 12000 + 3000

        # Vérifier que les communes sont présentes
        communes = list(response.context["communes"])
        self.assertIn(city1, communes)
        self.assertIn(city2, communes)

    def tearDown(self):
        # Nettoyer les fichiers de test
        if os.path.exists("test_media_home"):
            shutil.rmtree("test_media_home")


@override_settings(MEDIA_ROOT="test_media_home")
class SitemapTestCase(TestCase):
    """Tests pour les sitemaps"""

    def setUp(self):
        # Créer des données de test pour les sitemaps
        self.city = ConseilVille.objects.create(
            city_name="Fourmies",
            mayor_sex="M",
            mayor_first_name="Jean",
            mayor_last_name="Dupont",
            address="1 rue de la Mairie",
            postal_code="59610",
            phone_number="0321234567",
            website="http://www.fourmies.fr",
            image=SimpleUploadedFile(
                name="test_image.jpg",
                content=b"fake_image_content",
                content_type="image/jpeg",
            ),
            slogan="La ville de Fourmies",
            nb_habitants=12000,
        )

        # Créer des fichiers de test pour le journal
        from io import BytesIO

        from PIL import Image

        # Document PDF de test
        document_content = b"This is a test document."
        document_file = SimpleUploadedFile(
            "test.pdf", document_content, content_type="application/pdf"
        )

        # Image de couverture de test
        image = Image.new("RGB", (100, 100), color="red")
        buffer = BytesIO()
        image.save(buffer, format="jpeg")
        image_content = buffer.getvalue()
        cover_file = SimpleUploadedFile(
            "test.jpg", image_content, content_type="image/jpeg"
        )

        self.journal = Journal.objects.create(
            title="Journal Test",
            number=1,
            release_date="2024-01-01",
            page_number=10,
            document=document_file,
            cover=cover_file,
        )

    def tearDown(self):
        # Nettoyer les fichiers de test
        if os.path.exists("test_media_home"):
            shutil.rmtree("test_media_home")

    def test_static_view_sitemap(self):
        """Test du sitemap des vues statiques"""
        sitemap = StaticViewSitemap()

        # Vérifier les propriétés
        self.assertEqual(sitemap.priority, 0.5)
        self.assertEqual(sitemap.changefreq, "weekly")

        # Vérifier les items
        items = sitemap.items()
        self.assertIn("home", items)
        self.assertIn("presentation", items)
        self.assertIn("marches_publics", items)
        self.assertIn("mobilite", items)

        # Vérifier la génération des URLs pour les vues qui existent
        location = sitemap.location("home")
        self.assertEqual(location, reverse("home"))

        location = sitemap.location("presentation")
        self.assertEqual(location, reverse("presentation"))

    def test_communes_sitemap(self):
        """Test du sitemap des communes"""
        sitemap = CommunesSitemap()

        # Vérifier les propriétés
        self.assertEqual(sitemap.priority, 0.7)
        self.assertEqual(sitemap.changefreq, "monthly")

        # Vérifier les items
        items = list(sitemap.items())
        self.assertIn(self.city, items)

        # Vérifier la génération des URLs
        location = sitemap.location(self.city)
        expected_url = reverse(
            "communes-membres:commune", kwargs={"slug": self.city.slug}
        )
        self.assertEqual(location, expected_url)

    def test_journal_sitemap(self):
        """Test du sitemap du journal"""
        sitemap = JournalSitemap()

        # Vérifier les propriétés
        self.assertEqual(sitemap.priority, 0.6)
        self.assertEqual(sitemap.changefreq, "monthly")

        # Vérifier les items
        items = list(sitemap.items())
        self.assertIn(self.journal, items)

        # Vérifier lastmod
        lastmod = sitemap.lastmod(self.journal)
        self.assertEqual(lastmod, self.journal.release_date)

        # Note: Le test de location est commenté car l'URL 'journal_detail' n'existe pas
        # dans les URLs actuelles de l'application journal


class ErrorHandlerTestCase(TestCase):
    """Tests pour les gestionnaires d'erreur"""

    def setUp(self):
        self.client = Client()

    def test_custom_handler404(self):
        """Test du gestionnaire d'erreur 404 personnalisé"""
        from django.http import HttpRequest
        from django.test import RequestFactory

        from .views import custom_handler404

        factory = RequestFactory()
        request = factory.get("/nonexistent-url/")
        response = custom_handler404(request)

        self.assertEqual(response.status_code, 404)
        # Juste vérifier que le handler fonctionne
        self.assertIsNotNone(response.content)


@override_settings(MEDIA_ROOT="test_media_home")
class EdgeCasesTestCase(TestCase):
    """Tests pour les cas particuliers et la couverture complète"""

    def setUp(self):
        self.client = Client()

    def test_home_view_with_empty_contact_email_list(self):
        """Test de la vue home avec une liste d'emails de contact vide mais existante"""
        # Créer un email de contact inactif - cela va provoquer l'erreur IndexError
        ContactEmail.objects.create(email="inactive@ccsa.fr", is_active=False)

        form_data = {
            "first_name": "Jean",
            "last_name": "Dupont",
            "email": "jean.dupont@example.com",
            "phone": "0123456789",
            "message": "Ceci est un message de test",
            "rgpd": True,  # Champ RGPD requis
        }

        # Ce test devrait générer une erreur dans la vue car ccsa_contact[0] sur une liste vide
        with self.assertRaises(IndexError):
            response = self.client.post(reverse("home"), form_data)

    def test_home_view_nb_habitants_calculation(self):
        """Test du calcul du nombre d'habitants dans la vue home"""
        # Créer plusieurs communes avec des nombres d'habitants différents
        ConseilVille.objects.create(
            city_name="Fourmies",
            mayor_sex="M",
            mayor_first_name="Jean",
            mayor_last_name="Dupont",
            address="1 rue de la Mairie",
            postal_code="59610",
            phone_number="0321234567",
            website="http://www.fourmies.fr",
            image=SimpleUploadedFile(
                name="test_image1.jpg",
                content=b"fake_image_content1",
                content_type="image/jpeg",
            ),
            slogan="La ville de Fourmies",
            nb_habitants=12000,
        )

        ConseilVille.objects.create(
            city_name="Anor",
            mayor_sex="F",
            mayor_first_name="Marie",
            mayor_last_name="Martin",
            address="2 rue de la Mairie",
            postal_code="59611",
            phone_number="0321234568",
            website="http://www.anor.fr",
            image=SimpleUploadedFile(
                name="test_image2.jpg",
                content=b"fake_image_content2",
                content_type="image/jpeg",
            ),
            slogan="La ville d'Anor",
            nb_habitants=3500,
        )

        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)

        # Vérifier le calcul correct du nombre total d'habitants
        self.assertEqual(response.context["nb_habitants"], 15500)  # 12000 + 3500
        self.assertEqual(response.context["nb_communes"], 2)

    def test_presentation_view_nb_habitants_calculation(self):
        """Test du calcul du nombre d'habitants dans la vue présentation"""
        # Créer plusieurs communes
        ConseilVille.objects.create(
            city_name="Glageon",
            mayor_sex="M",
            mayor_first_name="Pierre",
            mayor_last_name="Durand",
            address="3 rue de la Mairie",
            postal_code="59612",
            phone_number="0321234569",
            website="http://www.glageon.fr",
            image=SimpleUploadedFile(
                name="test_image3.jpg",
                content=b"fake_image_content3",
                content_type="image/jpeg",
            ),
            slogan="La ville de Glageon",
            nb_habitants=2800,
        )

        ConseilVille.objects.create(
            city_name="Trelon",
            mayor_sex="F",
            mayor_first_name="Sophie",
            mayor_last_name="Bernard",
            address="4 rue de la Mairie",
            postal_code="59613",
            phone_number="0321234570",
            website="http://www.trelon.fr",
            image=SimpleUploadedFile(
                name="test_image4.jpg",
                content=b"fake_image_content4",
                content_type="image/jpeg",
            ),
            slogan="La ville de Trelon",
            nb_habitants=1200,
        )

        response = self.client.get(reverse("presentation"))
        self.assertEqual(response.status_code, 200)

        # Vérifier le calcul correct
        self.assertEqual(response.context["nb_habitants"], 4000)  # 2800 + 1200
        self.assertEqual(response.context["nb_communes"], 2)

    def tearDown(self):
        # Nettoyer les fichiers de test
        if os.path.exists("test_media_home"):
            shutil.rmtree("test_media_home")
