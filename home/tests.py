import os
import shutil
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core import mail
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, SimpleTestCase, TestCase, override_settings
from django.urls import reverse

from conseil_communautaire.models import ConseilVille
from contact.models import ContactEmail
from journal.models import Journal
from services.models import Service

from .forms import PLUiModificationForm
from .models import PLUISettings
from .sitemaps import CommunesSitemap, JournalSitemap, StaticViewSitemap

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
    """Tests pour les fonctions utilitaires (Django User standard)."""

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

    def test_user_is_staff_flags(self):
        """Vérifie les flags is_staff et is_superuser sur les modèles Django."""
        self.assertFalse(self.normal_user.is_staff)
        self.assertFalse(self.normal_user.is_superuser)
        self.assertTrue(self.staff_user.is_staff)
        self.assertFalse(self.staff_user.is_superuser)
        self.assertTrue(self.superuser.is_staff)
        self.assertTrue(self.superuser.is_superuser)


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
        # nb_communes/nb_habitants: 0 quand aucun enregistrement
        # (vs None quand la liste est intentionnellement vide)
        self.assertEqual(response.context["nb_communes"], 0)
        self.assertEqual(response.context["nb_habitants"], 0)

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
        # From = DEFAULT_FROM_EMAIL (securite SPF/DKIM)
        self.assertEqual(email_ccsa.from_email, "nepasrepondre@cc-sudavesnois.fr")
        # Reply-To = email du visiteur (pour reponse)
        self.assertIn("jean.dupont@example.com", email_ccsa.reply_to)
        self.assertIn("contact@ccsa.fr", email_ccsa.to)

        # Vérifier le deuxième email (confirmation client)
        email_client = mail.outbox[1]
        self.assertIn("CONFIRMATION DE CONTACT - CCSA", email_client.subject)
        self.assertIn("Jean", email_client.subject)
        self.assertIn("Dupont", email_client.subject)
        # Confirmation envoyee depuis nepasrepondre@cc-sudavesnois.fr
        self.assertIn("nepasrepondre@cc-sudavesnois.fr", email_client.from_email)
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
        """Test du formulaire de contact valide sans email de contact actif.

        L'adresse par defaut ``contact@cc-sudavesnois.fr`` doit etre
        utilisee meme si la table ``ContactEmail`` est vide.
        """
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

        response = self.client.post(reverse("home"), form_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("home"))

        # 2 emails envoyes (CCSA + confirmation) avec l'adresse par defaut
        self.assertEqual(len(mail.outbox), 2)
        self.assertIn("contact@cc-sudavesnois.fr", mail.outbox[0].to)

    def test_home_view_post_invalid_form(self):
        """Test du formulaire de contact invalide: 200 + erreurs, pas 302."""
        form_data = {
            "first_name": "",  # Champ requis vide
            "last_name": "Dupont",
            "email": "invalid-email",  # Email invalide
            "phone": "0123456789",
            "message": "Ceci est un message de test",
        }

        response = self.client.post(reverse("home"), form_data)
        # Comportement RGAA-friendly: on re-rend la page avec les erreurs
        # au lieu d'un redirect POST-redirect-GET silencieux.
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home/index.html")
        self.assertTrue(response.context["form_has_errors"])

        # Vérifier qu'aucun email n'a été envoyé
        self.assertEqual(len(mail.outbox), 0)


@override_settings(MEDIA_ROOT="test_media_home")
class PresentationViewTestCase(TestCase):
    """Tests pour la vue présentation"""

    def setUp(self):
        self.client = Client()
        # @cache_page: on nettoie le cache pour eviter les interferences
        cache.clear()

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
        """Test du sitemap du journal (liste de noms d'URL)."""
        sitemap = JournalSitemap()

        # Vérifier les propriétés
        self.assertEqual(sitemap.priority, 0.6)
        self.assertEqual(sitemap.changefreq, "monthly")

        # Items contient un seul nom d'URL
        items = list(sitemap.items())
        self.assertEqual(items, ["journal:journal"])
        location = sitemap.location("journal:journal")
        self.assertEqual(location, reverse("journal:journal"))

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

    def test_custom_handler500(self):
        """Test du gestionnaire d'erreur 500 personnalisé"""
        from django.http import HttpRequest
        from django.test import RequestFactory

        from .views import custom_handler500

        factory = RequestFactory()
        request = factory.get("/some-url/")
        response = custom_handler500(request)

        self.assertEqual(response.status_code, 500)
        # Juste vérifier que le handler fonctionne
        self.assertIsNotNone(response.content)


@override_settings(MEDIA_ROOT="test_media_home")
class EdgeCasesTestCase(TestCase):
    """Tests pour les cas particuliers et la couverture complète"""

    def setUp(self):
        self.client = Client()

    def test_home_view_with_only_inactive_contact_emails(self):
        """Avec uniquement des ContactEmail inactifs, la liste de destinataires
        doit toujours contenir l'adresse par defaut ``contact@cc-sudavesnois.fr``
        (pas d'IndexError ni de perte de message)."""
        ContactEmail.objects.create(email="inactive@ccsa.fr", is_active=False)

        form_data = {
            "first_name": "Jean",
            "last_name": "Dupont",
            "email": "jean.dupont@example.com",
            "phone": "0123456789",
            "message": "Ceci est un message de test",
            "rgpd": True,
        }

        # Plus d'IndexError : le code utilise l'adresse par defaut
        # et ignore les inactifs.
        response = self.client.post(reverse("home"), form_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("home"))

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


class PLUiModificationFormTestCase(SimpleTestCase):
    """Tests unitaires du formulaire PLUiModificationForm."""

    def _valid_data(self, **overrides):
        data = {
            "nom_prenom": "Jean Dupont",
            "adresse": "1 rue de la Mairie, 59610 Fourmies",
            "email": "jean.dupont@example.com",
            "telephone": "03 27 12 34 56",
            "parcelles": "123, 124",
            "commune": "Fourmies",
            "demande": "Demande de modification du zonage de la parcelle 123.",
        }
        data.update(overrides)
        return data

    def test_valid_form(self):
        form = PLUiModificationForm(self._valid_data())
        self.assertTrue(form.is_valid(), form.errors)

    def test_missing_required_field(self):
        form = PLUiModificationForm(self._valid_data(nom_prenom=""))
        self.assertFalse(form.is_valid())
        self.assertIn("nom_prenom", form.errors)

    def test_invalid_email(self):
        form = PLUiModificationForm(self._valid_data(email="not-an-email"))
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_telephone_too_short(self):
        form = PLUiModificationForm(self._valid_data(telephone="12345"))
        self.assertFalse(form.is_valid())
        self.assertIn("telephone", form.errors)

    def test_telephone_with_authorized_chars(self):
        form = PLUiModificationForm(self._valid_data(telephone="+33 3 27 12 34 56"))
        self.assertTrue(form.is_valid(), form.errors)

    def test_telephone_with_unauthorized_chars(self):
        form = PLUiModificationForm(self._valid_data(telephone="abc;def"))
        self.assertFalse(form.is_valid())
        self.assertIn("telephone", form.errors)

    def test_demande_too_short(self):
        form = PLUiModificationForm(self._valid_data(demande="court"))
        self.assertFalse(form.is_valid())
        self.assertIn("demande", form.errors)

    def test_commune_invalid_choice(self):
        form = PLUiModificationForm(self._valid_data(commune="Atlantis"))
        self.assertFalse(form.is_valid())
        self.assertIn("commune", form.errors)

    def test_communes_loaded_dynamically(self):
        import unicodedata

        form = PLUiModificationForm()
        codes = [c[0] for c in form.fields["commune"].choices if c[0]]
        self.assertIn("Fourmies", codes)
        # Les cles dans city_data peuvent avoir des accents (ex: Trélon)
        normalized = {
            unicodedata.normalize("NFKD", c).encode("ascii", "ignore").decode()
            for c in codes
        }
        self.assertIn("Trelon", normalized)
        self.assertGreater(len(codes), 5)

    def test_aria_required_set(self):
        form = PLUiModificationForm()
        for name, field in form.fields.items():
            if field.required:
                self.assertEqual(
                    field.widget.attrs.get("aria-required"),
                    "true",
                    f"Champ {name} sans aria-required",
                )


class PLUISettingsTestCase(TestCase):
    """Tests pour les paramètres de visibilité PLUi."""

    def setUp(self):
        self.client = Client()
        PLUISettings.clear()

    def test_pluisettings_model_creates_singleton(self):
        settings1 = PLUISettings.load()
        settings2 = PLUISettings.load()
        self.assertEqual(settings1.pk, 1)
        self.assertEqual(settings2.pk, 1)
        self.assertEqual(settings1.pk, settings2.pk)

    def test_pluisettings_default_visibility_false(self):
        settings = PLUISettings.load()
        self.assertFalse(settings.modification_simplifiee_1_visible)

    def test_modification_simplifiee_1_returns_404_by_default(self):
        response = self.client.get(reverse("modification_simplifiee_1"))
        self.assertEqual(response.status_code, 404)

    def test_modification_simplifiee_1_returns_200_when_enabled(self):
        PLUISettings.update_or_create(
            defaults={"modification_simplifiee_1_visible": True}
        )
        response = self.client.get(reverse("modification_simplifiee_1"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home/modification-simplifiee-1.html")

    def test_plui_page_includes_pluisettings_in_context(self):
        response = self.client.get(reverse("plui"))
        self.assertIn("plui_settings", response.context)

    def test_plui_card_hidden_when_visibility_false(self):
        PLUISettings.update_or_create(
            defaults={"modification_simplifiee_1_visible": False}
        )
        response = self.client.get(reverse("plui"))
        self.assertNotContains(response, "Modification Simplifiée n°1")

    def test_plui_card_visible_when_visibility_true(self):
        PLUISettings.update_or_create(
            defaults={"modification_simplifiee_1_visible": True}
        )
        response = self.client.get(reverse("plui"))
        self.assertContains(response, "Modification Simplifiée n°1")


class AdminPLUISettingsTestCase(TestCase):
    """Tests pour la page d'administration PLUi."""

    def setUp(self):
        User = get_user_model()
        self.staff_user = User.objects.create_user(
            email="staff@example.com",
            password="password123",
            is_staff=True,
        )
        self.normal_user = User.objects.create_user(
            email="user@example.com",
            password="password123",
        )
        PLUISettings.clear()

    def test_admin_page_redirects_anonymous(self):
        response = self.client.get(reverse("admin_plui_settings"))
        self.assertEqual(response.status_code, 302)

    def test_admin_page_redirects_non_staff(self):
        self.client.login(email="user@example.com", password="password123")
        response = self.client.get(reverse("admin_plui_settings"))
        self.assertEqual(response.status_code, 302)

    def test_admin_page_accessible_by_staff(self):
        self.client.login(email="staff@example.com", password="password123")
        response = self.client.get(reverse("admin_plui_settings"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home/admin_plui_settings.html")

    def test_admin_page_contains_form(self):
        self.client.login(email="staff@example.com", password="password123")
        response = self.client.get(reverse("admin_plui_settings"))
        self.assertContains(response, "modification_simplifiee_1_visible")
        self.assertContains(response, "Enregistrer")

    def test_admin_page_updates_settings(self):
        self.client.login(email="staff@example.com", password="password123")
        response = self.client.post(
            reverse("admin_plui_settings"),
            {"modification_simplifiee_1_visible": True},
        )
        self.assertEqual(response.status_code, 302)
        settings = PLUISettings.load()
        self.assertTrue(settings.modification_simplifiee_1_visible)

    def test_admin_page_disables_settings(self):
        PLUISettings.update_or_create(
            defaults={"modification_simplifiee_1_visible": True}
        )
        self.client.login(email="staff@example.com", password="password123")
        response = self.client.post(
            reverse("admin_plui_settings"),
            {"modification_simplifiee_1_visible": False},
        )
        self.assertEqual(response.status_code, 302)
        settings = PLUISettings.load()
        self.assertFalse(settings.modification_simplifiee_1_visible)
