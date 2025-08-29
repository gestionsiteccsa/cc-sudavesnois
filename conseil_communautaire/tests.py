import os
import shutil

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from PIL import Image

from conseil_communautaire.models import ConseilMembre, ConseilVille

User = get_user_model()
MEDIA_ROOT = "test_media_conseil"  # Répertoire de test pour les fichiers médias


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class ConseilVilleViewsTestCase(TestCase):
    """
    Tests pour les vues de la partie Conseil Ville
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.superuser = User.objects.create_superuser(
            email="admin@exemple.com", password="adminpassword"
        )

    def setUp(self):
        self.client = Client()
        self.client.login(email="admin@exemple.com", password="adminpassword")

        # Crée une image temporaire dans le dossier MEDIA_ROOT
        if not os.path.exists(MEDIA_ROOT):
            os.makedirs(MEDIA_ROOT)
        self.temp_image_path = os.path.join(MEDIA_ROOT, "test_image.jpg")
        with open(self.temp_image_path, "wb") as temp_image_file:
            # Crée une image rouge 100x100
            image = Image.new("RGB", (100, 100), color="red")
            # Sauvegarde l'image au format JPEG
            image.save(temp_image_file, format="JPEG")

        self.city = ConseilVille.objects.create(
            city_name="First City",
            postal_code="12345",
            address="123 Test St",
            phone_number="0123456789",
            website="https://www.firstcity.com",
            mayor_sex=ConseilVille.Sexe.Monsieur,
            mayor_first_name="John",
            mayor_last_name="Doe",
            image=self.temp_image_path,
            slogan=None,
            nb_habitants=1000,
        )

    def tearDown(self):
        self.client.logout()
        # Supprimez le répertoire de test des médias après chaque test
        if os.path.exists(MEDIA_ROOT):
            shutil.rmtree(MEDIA_ROOT)
        ConseilVille.objects.all().delete()
        ConseilMembre.objects.all().delete()

    # Tests vues d'accueil
    def test_general_view_with_data(self):
        """
        Teste la vue de la liste des conseils de ville avec données
        """
        response = self.client.get(reverse("conseil_communautaire:conseil"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "conseil_communautaire/conseil.html")
        # Utilisez le nom de la ville créée dans setUp
        self.assertContains(response, "First City")

    def test_general_view_without_data(self):
        """
        Teste la vue de la liste des conseils de ville sans données
        """
        ConseilVille.objects.all().delete()
        response = self.client.get(reverse("conseil_communautaire:conseil"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "conseil_communautaire/conseil.html")
        self.assertContains(
            response, "Aucune commune ni membre n'est disponible pour le moment."
        )

    # Tests vues d'ajout de ville
    def test_add_conseil_ville_view(self):
        """
        Teste la vue d'ajout de Conseil Ville
        """
        self.data = {
            "city_name": "Test City",
            "postal_code": "12345",
            "address": "123 Test St",
            "meeting_place": "Test Hall",
            "phone_number": "0123456789",
            "website": "https://www.testcity.com",
            "mayor_sex": ConseilVille.Sexe.Monsieur,
            "mayor_first_name": "John",
            "mayor_last_name": "Doe",
            "nb_habitants": 1000,
            "slogan": "test",
            "image": SimpleUploadedFile(
                name="test_image.jpg",
                content=open(self.temp_image_path, "rb").read(),
                content_type="image/jpeg",
            ),
        }

        response = self.client.post(
            reverse("conseil_communautaire:admin_add_city"), data=self.data, follow=True
        )
        # On suit la redirection (si elle avait eu lieu)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(
            response, reverse("conseil_communautaire:admin_list_cities")
        )
        # Vérifie que le nom de la ville est présent dans la réponse
        self.assertContains(response, "Test City")
        # Vérifie qu'on arrive bien sur la liste
        self.assertTemplateUsed(
            response, "conseil_communautaire/admin_cities_list.html"
        )

        self.assertTrue(ConseilVille.objects.filter(city_name="Test City").exists())
        city = ConseilVille.objects.get(city_name="Test City")
        self.assertTrue(os.path.exists(city.image.path))

    def test_add_conseil_ville_view_invalid_data(self):
        """
        Teste la vue d'ajout de Conseil Ville avec des données invalides
        """
        self.data = {
            "city_name": "Test City",
            "postal_code": "12345",
            "address": "123 Test St",
            "meeting_place": "Test Hall",
            "phone_number": "0123456789",
            "website": "https://www.testcity.com",
            "mayor_sex": ConseilVille.Sexe.Monsieur,
            "mayor_first_name": "John",
            "mayor_last_name": "Doe",
            "nb_habitants": 1000,
            "slogan": "test",
            "image": SimpleUploadedFile(
                name="test_image.jpg",
                content=open(self.temp_image_path, "rb").read(),
                content_type="image/jpeg",
            ),
        }
        invalid_data = self.data
        invalid_data["city_name"] = ""
        response = self.client.post(
            reverse("conseil_communautaire:admin_add_city"), data=invalid_data
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "conseil_communautaire/admin_city_add.html")
        self.assertFalse(ConseilVille.objects.filter(city_name="").exists())

    # Tests vues de modifications de villes
    def test_edit_conseil_ville_view(self):
        """
        Teste la vue de modification de Conseil Ville
        """
        response = self.client.get(
            reverse("conseil_communautaire:admin_edit_city", args=[self.city.id])
        )
        self.assertContains(response, self.city.city_name)
        self.assertContains(response, self.city.postal_code)
        self.assertContains(response, self.city.address)
        self.assertContains(response, self.city.phone_number)
        self.assertContains(response, self.city.website)
        self.assertContains(response, self.city.mayor_sex)
        self.assertContains(response, self.city.mayor_first_name)
        self.assertContains(response, self.city.mayor_last_name)
        if self.city.slogan:
            self.assertContains(response, self.city.slogan)
        self.assertContains(response, self.city.nb_habitants)
        self.assertContains(response, self.city.image.url)
        self.assertTemplateUsed(response, "conseil_communautaire/admin_city_edit.html")

        updated_data = {
            "city_name": "Updated City",
            "postal_code": "54321",
            "address": "321 Updated St",
            "meeting_place": "Updated Hall",
            "phone_number": "9876543210",
            "website": "https://www.updatedcity.com",
            "mayor_sex": ConseilVille.Sexe.Monsieur,
            "mayor_first_name": "Jane",
            "mayor_last_name": "Smith",
            "nb_habitants": 1500,
            "slogan": "Updated slogan",
            "image": SimpleUploadedFile(
                name="updated_image.jpg",
                content=open(self.temp_image_path, "rb").read(),
                content_type="image/jpeg",
            ),
        }
        # Envoie une requête POST pour mettre à jour la ville
        response = self.client.post(
            reverse("conseil_communautaire:admin_edit_city", args=[self.city.id]),
            data=updated_data,
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(
            response, reverse("conseil_communautaire:admin_list_cities")
        )
        self.assertContains(response, "Updated City")
        self.assertTrue(ConseilVille.objects.filter(city_name="Updated City").exists())
        self.assertFalse(ConseilVille.objects.filter(city_name="First City").exists())

    def test_edit_conseil_ville_view_invalid_data(self):
        """
        Teste la vue de modification de Conseil Ville avec des données invalides
        """
        invalid_data = {
            "city_name": "",  # Nom de la ville invalide (vide)
            "postal_code": "54321",
            "address": "321 Updated St",
            "meeting_place": "Updated Hall",
            "phone_number": "9876543210",
            "website": "https://www.updatedcity.com",
            "mayor_sex": ConseilVille.Sexe.Monsieur,
            "mayor_first_name": "Jane",
            "mayor_last_name": "Smith",
            "nb_habitants": 1500,
            "slogan": "Updated slogan",
            "image": SimpleUploadedFile(
                name="updated_image.jpg",
                content=open(self.temp_image_path, "rb").read(),
                content_type="image/jpeg",
            ),
        }
        response = self.client.post(
            reverse("conseil_communautaire:admin_edit_city", args=[self.city.id]),
            data=invalid_data,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "conseil_communautaire/admin_city_edit.html")
        # Vérifie la présence d'un message d'erreur
        self.assertContains(response, "Ce champ est obligatoire.")
        # La ville initiale doit toujours exister
        self.assertTrue(ConseilVille.objects.filter(city_name="First City").exists())
        # La ville avec un nom vide ne doit pas exister
        self.assertFalse(ConseilVille.objects.filter(city_name="").exists())

    # Tests vues de suppression de villes
    def test_delete_conseil_ville_view(self):
        """
        Teste la vue de suppression de Conseil Ville
        """
        response = self.client.get(
            reverse("conseil_communautaire:admin_delete_city", args=[self.city.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, "conseil_communautaire/admin_city_delete.html"
        )
        self.assertContains(response, "Êtes-vous certain de vouloir supprimer : ")
        self.assertContains(response, self.city.city_name)

        # Envoie une requête POST pour supprimer la ville
        response = self.client.post(
            reverse("conseil_communautaire:admin_delete_city", args=[self.city.id]),
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(
            response, reverse("conseil_communautaire:admin_list_cities")
        )
        self.assertFalse(ConseilVille.objects.filter(city_name="First City").exists())


# Tests vues de la partie Conseil Membre
@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class ConseilMembreViewsTestCase(TestCase):
    """
    Tests pour les vues de la partie Conseil Membre
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.superuser = User.objects.create_superuser(
            email="admin@exemple.com", password="adminpassword"
        )

    def setUp(self):
        self.client = Client()
        self.client.login(email="admin@exemple.com", password="adminpassword")

        # Crée une image temporaire dans le dossier MEDIA_ROOT
        if not os.path.exists(MEDIA_ROOT):
            os.makedirs(MEDIA_ROOT)
        self.temp_image_path = os.path.join(MEDIA_ROOT, "test_image.jpg")
        with open(self.temp_image_path, "wb") as temp_image_file:
            # Crée une image rouge 100x100
            image = Image.new("RGB", (100, 100), color="red")
            # Sauvegarde l'image au format JPEG
            image.save(temp_image_file, format="JPEG")

    def init_test_data(self):
        self.city = ConseilVille.objects.create(
            city_name="First City",
            postal_code="12345",
            address="123 Test St",
            phone_number="0123456789",
            website="https://www.firstcity.com",
            mayor_sex=ConseilVille.Sexe.Monsieur,
            mayor_first_name="John",
            mayor_last_name="Doe",
            image=self.temp_image_path,
            slogan=None,
            nb_habitants=1000,
        )
        self.member = ConseilMembre.objects.create(
            first_name="Jane",
            last_name="Smith",
            city=self.city,
            is_suppleant=False,
            sexe=ConseilMembre.Sexe.Madame,
        )
        self.member2 = ConseilMembre.objects.create(
            first_name="John",
            last_name="Doe",
            city=self.city,
            is_suppleant=True,
            sexe=ConseilMembre.Sexe.Monsieur,
        )

    def tearDown(self):
        self.client.logout()
        # Supprimez le répertoire de test des médias après chaque test
        if os.path.exists(MEDIA_ROOT):
            shutil.rmtree(MEDIA_ROOT)
        ConseilVille.objects.all().delete()
        ConseilMembre.objects.all().delete()

    # Tests vues d'accueil et admin
    def test_view_list_conseil_membre(self):
        """
        Teste la vue de la liste des membres du conseil avec données
        """
        self.init_test_data()
        response = self.client.get(reverse("conseil_communautaire:admin_membres_list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, "conseil_communautaire/admin_members_list.html"
        )
        self.assertContains(response, "Jane")

    def test_view_list_conseil_membre_without_data(self):
        """
        Teste la vue de la liste des membres du conseil sans données
        """
        response = self.client.get(reverse("conseil_communautaire:admin_membres_list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, "conseil_communautaire/admin_members_list.html"
        )
        self.assertNotContains(response, "Jane")

    def test_main_view_conseil_membre(self):
        """
        Teste la vue principale de Conseil Membre
        """
        self.init_test_data()
        response = self.client.get(reverse("conseil_communautaire:conseil"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "conseil_communautaire/conseil.html")
        self.assertContains(response, "Jane")
        self.assertContains(response, "SMITH")
        self.assertContains(response, "John")
        self.assertContains(response, "DOE")
        self.assertContains(response, "First City")

    def test_main_view_conseil_membre_without_data(self):
        """
        Teste la vue principale de Conseil Membre sans données
        """
        response = self.client.get(reverse("conseil_communautaire:conseil"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "conseil_communautaire/conseil.html")
        self.assertContains(
            response, "Aucune commune ni membre n'est disponible pour le moment."
        )

    # Tests vues d'ajout de membre
    def test_add_conseil_membre_view_valid_data(self):
        """
        Teste la vue d'ajout de Conseil Membre
        """
        self.init_test_data()
        self.data = {
            "first_name": "Test",
            "last_name": "Member",
            "city": self.city.id,
            "is_suppleant": False,
            "sexe": ConseilMembre.Sexe.Monsieur,
        }

        response = self.client.post(
            reverse("conseil_communautaire:admin_member_add"),
            data=self.data,
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        # Vérifie que le nom du membre est présent dans la réponse
        self.assertContains(response, "Test")
        self.assertRedirects(
            response, reverse("conseil_communautaire:admin_list_cities")
        )
        self.assertTemplateUsed(
            response, "conseil_communautaire/admin_cities_list.html"
        )  # Vérifie qu'on arrive bien sur la liste

    def test_add_conseil_membre_view_invalid_data(self):
        """
        Teste la vue d'ajout de Conseil Membre avec des données invalides
        """
        self.init_test_data()
        self.invalid_data = {
            "first_name": "Test",
            "last_name": "",
            "city": self.city.id,
            "is_suppleant": False,
            "sexe": ConseilMembre.Sexe.Monsieur,
        }
        response = self.client.post(
            reverse("conseil_communautaire:admin_member_add"), data=self.invalid_data
        )
        self.assertEqual(response.status_code, 200)
        # Vérifie que le membre n'a pas été ajouté
        self.assertEqual(ConseilMembre.objects.count(), 2)
        self.assertTemplateUsed(response, "conseil_communautaire/admin_member_add.html")
        self.assertContains(response, "Ce champ est obligatoire.")

    # Tests vues de modification de membre
    def test_edit_conseil_membre_view(self):
        """
        Teste la vue de modification de Conseil Membre
        """
        self.init_test_data()
        response = self.client.get(
            reverse("conseil_communautaire:admin_member_edit", args=[self.member.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, "conseil_communautaire/admin_member_edit.html"
        )
        self.assertContains(response, "Jane")
        self.assertContains(response, "SMITH")
        self.assertContains(response, "Monsieur")

        updated_data = {
            "first_name": "Updated",
            "last_name": "Member",
            "city": self.city.id,
            "is_suppleant": True,
            "sexe": ConseilMembre.Sexe.Monsieur,
        }
        # Envoie une requête POST pour mettre à jour le membre
        response = self.client.post(
            reverse("conseil_communautaire:admin_member_edit", args=[self.member.id]),
            data=updated_data,
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(
            response, reverse("conseil_communautaire:admin_list_cities")
        )
        self.assertTemplateUsed(
            response, "conseil_communautaire/admin_cities_list.html"
        )
        self.assertContains(response, "Updated")
        self.assertContains(response, "MEMBER")
        self.assertTrue(ConseilMembre.objects.filter(first_name="Updated").exists())
        self.assertFalse(ConseilMembre.objects.filter(first_name="Jane").exists())

    def test_edit_conseil_membre_view_invalid_data(self):
        """
        Teste la vue de modification de Conseil Membre avec des données invalides
        """
        self.init_test_data()
        invalid_data = {
            "first_name": "Updated",
            "last_name": "",
            "city": self.city.id,
            "is_suppleant": True,
            "sexe": ConseilMembre.Sexe.Monsieur,
        }
        response = self.client.post(
            reverse("conseil_communautaire:admin_member_edit", args=[self.member.id]),
            data=invalid_data,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, "conseil_communautaire/admin_member_edit.html"
        )
        self.assertContains(response, "Ce champ est obligatoire.")
        self.assertTrue(ConseilMembre.objects.filter(first_name="Jane").exists())
        self.assertFalse(ConseilMembre.objects.filter(first_name="").exists())

    # Tests vues de suppression de membre
    def test_delete_conseil_membre_view(self):
        """
        Teste la vue de suppression de Conseil Membre
        """
        self.init_test_data()
        response = self.client.get(
            reverse("conseil_communautaire:admin_member_delete", args=[self.member.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, "conseil_communautaire/admin_member_delete.html"
        )
        self.assertContains(response, "Êtes-vous certain de vouloir supprimer : ")
        self.assertContains(response, "Jane")
        self.assertContains(response, "SMITH")

        # Envoie une requête POST pour supprimer le membre
        response = self.client.post(
            reverse("conseil_communautaire:admin_member_delete", args=[self.member.id]),
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(
            response, reverse("conseil_communautaire:admin_list_cities")
        )
        self.assertTemplateUsed(
            response, "conseil_communautaire/admin_cities_list.html"
        )
        self.assertFalse(ConseilMembre.objects.filter(first_name="Jane").exists())
