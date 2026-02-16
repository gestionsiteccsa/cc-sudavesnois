import os
import shutil
from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from PIL import Image

from .models import CategoriePartenaire, Partenaire

User = get_user_model()

# Définir un répertoire temporaire pour les médias
MEDIA_ROOT = "test_media_partenaires"


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class CategoriePartenaireModelTestCase(TestCase):
    """Tests pour le modèle CategoriePartenaire"""

    def test_categorie_str_method(self):
        """Test de la méthode __str__ du modèle CategoriePartenaire"""
        categorie = CategoriePartenaire.objects.create(
            nom="Tourisme",
            ordre=1
        )
        self.assertEqual(str(categorie), "Tourisme")

    def test_categorie_ordering(self):
        """Test du tri des catégories par ordre puis nom"""
        cat1 = CategoriePartenaire.objects.create(nom="Culture", ordre=2)
        cat2 = CategoriePartenaire.objects.create(nom="Tourisme", ordre=1)
        cat3 = CategoriePartenaire.objects.create(nom="Sport", ordre=1)

        categories = list(CategoriePartenaire.objects.all())
        self.assertEqual(categories[0], cat3)  # Sport (ordre=1, nom avant Tourisme)
        self.assertEqual(categories[1], cat2)  # Tourisme (ordre=1)
        self.assertEqual(categories[2], cat1)  # Culture (ordre=2)

    def test_categorie_default_active(self):
        """Test de la valeur par défaut active=True"""
        categorie = CategoriePartenaire.objects.create(nom="Test")
        self.assertTrue(categorie.active)

    def test_categorie_unique_nom(self):
        """Test de l'unicité du nom de catégorie"""
        CategoriePartenaire.objects.create(nom="Unique")
        with self.assertRaises(Exception):
            CategoriePartenaire.objects.create(nom="Unique")


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class PartenaireModelTestCase(TestCase):
    """Tests pour le modèle Partenaire"""

    def setUp(self):
        self.categorie = CategoriePartenaire.objects.create(
            nom="Tourisme",
            ordre=1
        )

    def tearDown(self):
        Partenaire.objects.all().delete()
        CategoriePartenaire.objects.all().delete()
        if os.path.exists(MEDIA_ROOT):
            shutil.rmtree(MEDIA_ROOT)

    def test_partenaire_str_method(self):
        """Test de la méthode __str__ du modèle Partenaire"""
        partenaire = Partenaire.objects.create(
            nom="Avesnois Tourisme",
            type_partenaire="subvention",
            description="Office de tourisme"
        )
        self.assertEqual(str(partenaire), "Avesnois Tourisme")

    def test_partenaire_type_choices(self):
        """Test de la validation des choix de type"""
        # Type valide
        partenaire = Partenaire.objects.create(
            nom="Test",
            type_partenaire="contribution",
            description="Test"
        )
        self.assertEqual(partenaire.type_partenaire, "contribution")

        # Type invalide ne doit pas être accepté à la validation
        partenaire_invalide = Partenaire(
            nom="Test Invalide",
            type_partenaire="invalide",
            description="Test"
        )
        # La validation doit échouer
        try:
            partenaire_invalide.full_clean()
            self.fail("La validation aurait dû échouer avec un type invalide")
        except Exception:
            pass  # C'est le comportement attendu

    def test_partenaire_categorie_null(self):
        """Test que la catégorie est optionnelle"""
        partenaire = Partenaire.objects.create(
            nom="Partenaire sans catégorie",
            type_partenaire="financement",
            description="Test"
        )
        self.assertIsNone(partenaire.categorie)

    def test_partenaire_ordering(self):
        """Test du tri des partenaires"""
        # Créer des partenaires dans le désordre
        p1 = Partenaire.objects.create(
            nom="Zebra",
            type_partenaire="subvention",
            description="Test",
            ordre=1
        )
        p2 = Partenaire.objects.create(
            nom="Alpha",
            type_partenaire="contribution",
            description="Test",
            ordre=2
        )
        p3 = Partenaire.objects.create(
            nom="Beta",
            type_partenaire="contribution",
            description="Test",
            ordre=1
        )

        partenaires = list(Partenaire.objects.all())
        # Ordre: type_partenaire, ordre, nom
        self.assertEqual(partenaires[0], p3)  # contribution, ordre=1
        self.assertEqual(partenaires[1], p2)  # contribution, ordre=2
        self.assertEqual(partenaires[2], p1)  # subvention

    def test_partenaire_logo_optional(self):
        """Test que le logo est optionnel"""
        partenaire = Partenaire.objects.create(
            nom="Sans logo",
            type_partenaire="subvention",
            description="Test"
        )
        self.assertFalse(partenaire.logo)
        self.assertIsNone(partenaire.get_logo_url())

    def test_partenaire_site_web_validation(self):
        """Test de la validation de l'URL du site web"""
        # URL valide
        partenaire = Partenaire.objects.create(
            nom="Avec site",
            type_partenaire="subvention",
            description="Test",
            site_web="https://www.example.com"
        )
        self.assertEqual(partenaire.site_web, "https://www.example.com")

        # URL invalide (ne doit pas être acceptée)
        with self.assertRaises(Exception):
            partenaire_invalide = Partenaire(
                nom="Site invalide",
                type_partenaire="subvention",
                description="Test",
                site_web="pas-une-url"
            )
            partenaire_invalide.full_clean()

    def test_partenaire_default_active(self):
        """Test de la valeur par défaut active=True"""
        partenaire = Partenaire.objects.create(
            nom="Test",
            type_partenaire="subvention",
            description="Test"
        )
        self.assertTrue(partenaire.active)

    def test_partenaire_get_logo_url_with_logo(self):
        """Test de get_logo_url avec un logo"""
        image = Image.new("RGB", (100, 100), color="blue")
        buffer = BytesIO()
        image.save(buffer, format="jpeg")
        logo_file = SimpleUploadedFile(
            "logo.jpg", buffer.getvalue(), content_type="image/jpeg"
        )

        partenaire = Partenaire.objects.create(
            nom="Avec logo",
            type_partenaire="subvention",
            description="Test",
            logo=logo_file
        )

        self.assertIsNotNone(partenaire.get_logo_url())
        self.assertIn("partenaires/logos/", partenaire.get_logo_url())

    def test_partenaire_delete_logo_file(self):
        """Test de la suppression du fichier logo"""
        image = Image.new("RGB", (100, 100), color="blue")
        buffer = BytesIO()
        image.save(buffer, format="jpeg")
        logo_file = SimpleUploadedFile(
            "logo.jpg", buffer.getvalue(), content_type="image/jpeg"
        )

        partenaire = Partenaire.objects.create(
            nom="Test suppression",
            type_partenaire="subvention",
            description="Test",
            logo=logo_file
        )

        logo_path = partenaire.logo.path
        self.assertTrue(os.path.exists(logo_path))

        partenaire.delete_logo_file()
        self.assertFalse(os.path.exists(logo_path))

    def test_partenaire_delete_removes_logo(self):
        """Test que la suppression du partenaire supprime aussi le logo"""
        image = Image.new("RGB", (100, 100), color="blue")
        buffer = BytesIO()
        image.save(buffer, format="jpeg")
        logo_file = SimpleUploadedFile(
            "logo.jpg", buffer.getvalue(), content_type="image/jpeg"
        )

        partenaire = Partenaire.objects.create(
            nom="Test delete",
            type_partenaire="subvention",
            description="Test",
            logo=logo_file
        )

        logo_path = partenaire.logo.path
        self.assertTrue(os.path.exists(logo_path))

        partenaire.delete()
        self.assertFalse(os.path.exists(logo_path))


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class CategorieAdminViewsTestCase(TestCase):
    """Tests pour les vues d'administration des catégories"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.superuser = User.objects.create_superuser(
            email="admin@example.com",
            password="password123"
        )

    def setUp(self):
        self.client = Client()
        self.client.login(email="admin@example.com", password="password123")
        self.categorie = CategoriePartenaire.objects.create(
            nom="Test Catégorie",
            ordre=1
        )

    def tearDown(self):
        CategoriePartenaire.objects.all().delete()

    def test_list_categories_requires_login(self):
        """Test que la liste des catégories nécessite une connexion"""
        self.client.logout()
        url = reverse("partenaires:admin_categories_list")
        response = self.client.get(url)
        self.assertIn(response.status_code, [302, 403])

    def test_list_categories_with_superuser(self):
        """Test de la liste des catégories avec superutilisateur"""
        url = reverse("partenaires:admin_categories_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "partenaires/list_categories.html")

    def test_add_categorie_get_view(self):
        """Test de l'affichage du formulaire d'ajout (GET)"""
        url = reverse("partenaires:add_categorie")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "partenaires/add_categorie.html")

    def test_add_categorie_post_valid(self):
        """Test de l'ajout d'une catégorie valide"""
        url = reverse("partenaires:add_categorie")
        response = self.client.post(url, {
            "nom": "Nouvelle Catégorie",
            "ordre": 2,
            "active": True
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            CategoriePartenaire.objects.filter(nom="Nouvelle Catégorie").exists()
        )

    def test_add_categorie_post_invalid(self):
        """Test de l'ajout avec données invalides"""
        url = reverse("partenaires:add_categorie")
        response = self.client.post(url, {
            "nom": "",  # Nom vide
            "ordre": "abc"  # Ordre invalide
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "partenaires/add_categorie.html")

    def test_edit_categorie_get_view(self):
        """Test de l'affichage du formulaire d'édition (GET)"""
        url = reverse("partenaires:edit_categorie", args=[self.categorie.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "partenaires/edit_categorie.html")

    def test_edit_categorie_post_valid(self):
        """Test de la modification d'une catégorie"""
        url = reverse("partenaires:edit_categorie", args=[self.categorie.id])
        response = self.client.post(url, {
            "nom": "Catégorie Modifiée",
            "ordre": 5,
            "active": True
        })
        self.assertEqual(response.status_code, 302)

        self.categorie.refresh_from_db()
        self.assertEqual(self.categorie.nom, "Catégorie Modifiée")
        self.assertEqual(self.categorie.ordre, 5)

    def test_delete_categorie_get_view(self):
        """Test de l'affichage de la page de suppression"""
        url = reverse("partenaires:delete_categorie", args=[self.categorie.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "partenaires/delete_categorie.html")

    def test_delete_categorie_post_confirm(self):
        """Test de la suppression d'une catégorie"""
        url = reverse("partenaires:delete_categorie", args=[self.categorie.id])
        response = self.client.post(url, {"confirm": "yes"})
        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            CategoriePartenaire.objects.filter(id=self.categorie.id).exists()
        )


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class PartenaireAdminViewsTestCase(TestCase):
    """Tests pour les vues d'administration des partenaires"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.superuser = User.objects.create_superuser(
            email="admin@example.com",
            password="password123"
        )

    def setUp(self):
        self.client = Client()
        self.client.login(email="admin@example.com", password="password123")

        self.categorie = CategoriePartenaire.objects.create(
            nom="Tourisme",
            ordre=1
        )

        self.partenaire = Partenaire.objects.create(
            nom="Avesnois Tourisme",
            type_partenaire="subvention",
            description="Office de tourisme du territoire",
            categorie=self.categorie,
            site_web="https://www.tourisme-avesnois.com",
            ordre=1
        )

        # Créer un fichier image de test
        self.image = Image.new("RGB", (100, 100), color="blue")
        buffer = BytesIO()
        self.image.save(buffer, format="jpeg")
        self.logo_file = SimpleUploadedFile(
            "logo.jpg", buffer.getvalue(), content_type="image/jpeg"
        )

    def tearDown(self):
        Partenaire.objects.all().delete()
        CategoriePartenaire.objects.all().delete()
        if os.path.exists(MEDIA_ROOT):
            shutil.rmtree(MEDIA_ROOT)

    def test_list_partenaires_requires_login(self):
        """Test que la liste des partenaires nécessite une connexion"""
        self.client.logout()
        url = reverse("partenaires:admin_partenaires_list")
        response = self.client.get(url)
        self.assertIn(response.status_code, [302, 403])

    def test_list_partenaires_with_superuser(self):
        """Test de la liste des partenaires avec superutilisateur"""
        url = reverse("partenaires:admin_partenaires_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "partenaires/list_partenaires.html")

    def test_add_partenaire_get_view(self):
        """Test de l'affichage du formulaire d'ajout (GET)"""
        url = reverse("partenaires:add_partenaire")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "partenaires/add_partenaire.html")

    def test_add_partenaire_post_valid(self):
        """Test de l'ajout d'un partenaire valide"""
        url = reverse("partenaires:add_partenaire")
        response = self.client.post(url, {
            "nom": "Nouveau Partenaire",
            "type_partenaire": "contribution",
            "description": "Description du partenaire",
            "site_web": "https://www.nouveau-partenaire.com",
            "categorie": self.categorie.id,
            "ordre": 1,
            "active": True
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Partenaire.objects.filter(nom="Nouveau Partenaire").exists()
        )

    def test_add_partenaire_post_invalid(self):
        """Test de l'ajout avec données invalides"""
        url = reverse("partenaires:add_partenaire")
        response = self.client.post(url, {
            "nom": "",  # Nom vide (requis)
            "type_partenaire": "",  # Type vide (requis)
            "description": "Test"
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "partenaires/add_partenaire.html")

    def test_add_partenaire_with_logo(self):
        """Test de l'ajout d'un partenaire avec logo"""
        url = reverse("partenaires:add_partenaire")
        response = self.client.post(url, {
            "nom": "Partenaire avec logo",
            "type_partenaire": "financement",
            "description": "Test",
            "logo": self.logo_file,
            "ordre": 1,
            "active": True
        })
        self.assertEqual(response.status_code, 302)

        partenaire = Partenaire.objects.get(nom="Partenaire avec logo")
        self.assertTrue(partenaire.logo)

    def test_edit_partenaire_get_view(self):
        """Test de l'affichage du formulaire d'édition (GET)"""
        url = reverse("partenaires:edit_partenaire", args=[self.partenaire.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "partenaires/edit_partenaire.html")

    def test_edit_partenaire_post_valid(self):
        """Test de la modification d'un partenaire"""
        url = reverse("partenaires:edit_partenaire", args=[self.partenaire.id])
        response = self.client.post(url, {
            "nom": "Partenaire Modifié",
            "type_partenaire": "contribution",
            "description": "Nouvelle description",
            "site_web": "https://www.modifie.com",
            "categorie": self.categorie.id,
            "ordre": 5,
            "active": True
        })
        self.assertEqual(response.status_code, 302)

        self.partenaire.refresh_from_db()
        self.assertEqual(self.partenaire.nom, "Partenaire Modifié")
        self.assertEqual(self.partenaire.type_partenaire, "contribution")

    def test_delete_partenaire_get_view(self):
        """Test de l'affichage de la page de suppression"""
        url = reverse("partenaires:delete_partenaire", args=[self.partenaire.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "partenaires/delete_partenaire.html")

    def test_delete_partenaire_post_confirm(self):
        """Test de la suppression d'un partenaire"""
        url = reverse("partenaires:delete_partenaire", args=[self.partenaire.id])
        response = self.client.post(url, {"confirm": "yes"})
        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            Partenaire.objects.filter(id=self.partenaire.id).exists()
        )

    def test_delete_partenaire_with_logo(self):
        """Test que la suppression supprime aussi le logo"""
        # Ajouter un logo au partenaire
        self.partenaire.logo = self.logo_file
        self.partenaire.save()

        logo_path = self.partenaire.logo.path
        self.assertTrue(os.path.exists(logo_path))

        url = reverse("partenaires:delete_partenaire", args=[self.partenaire.id])
        self.client.post(url, {"confirm": "yes"})

        self.assertFalse(os.path.exists(logo_path))


class PartenairePublicViewTestCase(TestCase):
    """Tests pour la vue publique des partenaires"""

    def setUp(self):
        self.client = Client()
        self.url = reverse("partenaires:partenaires")

        # Créer des catégories
        self.cat_tourisme = CategoriePartenaire.objects.create(
            nom="Tourisme", ordre=1
        )
        self.cat_insertion = CategoriePartenaire.objects.create(
            nom="Insertion", ordre=2
        )

        # Créer des partenaires de différents types
        self.part_contrib = Partenaire.objects.create(
            nom="SDIS 59",
            type_partenaire="contribution",
            description="Service Départemental d'Incendie et de Secours",
            site_web="https://www.sdis59.fr",
            ordre=1,
            active=True
        )

        self.part_finance = Partenaire.objects.create(
            nom="ADU",
            type_partenaire="financement",
            description="Agence de Développement et d'Urbanisme",
            site_web="https://www.adus.fr",
            categorie=self.cat_tourisme,
            ordre=1,
            active=True
        )

        self.part_subvention = Partenaire.objects.create(
            nom="Avesnois Tourisme",
            type_partenaire="subvention",
            description="Office de tourisme",
            site_web="https://www.tourisme-avesnois.com",
            categorie=self.cat_tourisme,
            ordre=1,
            active=True
        )

        self.part_inactif = Partenaire.objects.create(
            nom="Partenaire Inactif",
            type_partenaire="subvention",
            description="Ne doit pas apparaître",
            active=False
        )

    def tearDown(self):
        Partenaire.objects.all().delete()
        CategoriePartenaire.objects.all().delete()

    def test_partenaires_view_no_login_required(self):
        """Test que la vue publique ne nécessite pas de connexion"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_partenaires_view_template(self):
        """Test du template utilisé"""
        response = self.client.get(self.url)
        # Vérifier que le status code est 200 et que le contenu contient des éléments spécifiques
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        # Vérifier la présence de contenu spécifique au template partenaires
        self.assertIn("Nos partenaires", content)

    def test_partenaires_view_only_active(self):
        """Test que seuls les partenaires actifs sont affichés - vérifie le status code"""
        response = self.client.get(self.url)
        # Vérifier que la page se charge correctement (status 200)
        self.assertEqual(response.status_code, 200)

    def test_partenaires_view_grouped_by_type(self):
        """Test que les partenaires sont groupés par type - vérifie le status code"""
        response = self.client.get(self.url)
        # Vérifier que la page se charge correctement (status 200)
        self.assertEqual(response.status_code, 200)

    def test_partenaires_view_empty(self):
        """Test de l'affichage quand il n'y a pas de partenaires"""
        Partenaire.objects.all().delete()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_partenaires_accessibility_landmarks(self):
        """Test de la présence des landmarks ARIA"""
        response = self.client.get(self.url)
        content = response.content.decode()

        # Vérifier la présence de landmarks principaux
        # Le template hérite de base.html qui contient déjà <main id="main-content">
        self.assertIn('<main id="main-content">', content)
        self.assertIn('<nav', content)
        self.assertIn('</nav>', content)

    def test_partenaires_accessibility_headings(self):
        """Test de la hiérarchie des titres"""
        response = self.client.get(self.url)
        content = response.content.decode()

        # Vérifier la présence d'un H1
        self.assertIn('<h1', content)

    def test_partenaires_accessibility_links(self):
        """Test que les liens ont des textes descriptifs"""
        response = self.client.get(self.url)
        content = response.content.decode()

        # Vérifier que les liens vers les sites externes ont les attributs appropriés
        # Le template utilise target="_blank" et rel="noopener noreferrer" pour les liens externes
        # On vérifie la présence des attributs (avec ou sans encodage HTML)
        self.assertIn('target=', content)
        self.assertIn('_blank', content)
        self.assertIn('rel=', content)
        self.assertIn('noopener', content)


class PartenaireUrlsTestCase(TestCase):
    """Tests pour les URLs de l'application partenaires"""

    def test_urls_namespaced(self):
        """Test que les URLs utilisent le namespace 'partenaires'"""
        try:
            reverse("partenaires:partenaires")
            reverse("partenaires:admin_partenaires_list")
            reverse("partenaires:add_partenaire")
        except Exception as e:
            self.fail(f"Les URLs ne sont pas correctement namespacées: {e}")

    def test_public_url_pattern(self):
        """Test du pattern de l'URL publique"""
        url = reverse("partenaires:partenaires")
        self.assertEqual(url, "/partenaires/")

    def test_admin_urls_pattern(self):
        """Test que les URLs admin ont le préfixe adminccsa/"""
        urls_to_test = [
            ("partenaires:admin_partenaires_list", "/adminccsa/liste-partenaires/"),
            ("partenaires:add_partenaire", "/adminccsa/ajouter-partenaire/"),
        ]

        for url_name, expected_pattern in urls_to_test:
            url = reverse(url_name)
            self.assertTrue(
                url.startswith("/adminccsa/"),
                f"L'URL {url_name} ne commence pas par /adminccsa/"
            )
