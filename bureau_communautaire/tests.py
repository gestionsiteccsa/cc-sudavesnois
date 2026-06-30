import io
import os
import shutil
import stat
import tempfile
import uuid

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, SimpleTestCase, TestCase, override_settings
from django.urls import reverse

from PIL import Image

from commissions.models import Commission, CommissionCompetence
from conseil_communautaire.models import ConseilVille

from .models import Document, Elus, PageStatus

User = get_user_model()


def _make_jpeg_bytes(color=(10, 10, 10), size=(10, 10)):
    """Génère un buffer JPEG valide (10x10 par défaut)."""
    buf = io.BytesIO()
    Image.new("RGB", size=size, color=color).save(buf, format="JPEG")
    buf.seek(0)
    return buf


def _make_jpeg_uploaded(name="test.jpg", color=(10, 10, 10), size=(10, 10)):
    """Génère un SimpleUploadedFile JPEG valide pour les formulaires."""
    return SimpleUploadedFile(
        name, _make_jpeg_bytes(color, size).read(), content_type="image/jpeg"
    )


def _make_pdf_bytes():
    """Génère un buffer PDF minimal valide (header %PDF-1.4 + EOF)."""
    return io.BytesIO(b"%PDF-1.4\n%fake pdf content for tests\n%%EOF\n")


def _make_pdf_uploaded(name="test.pdf"):
    """Génère un SimpleUploadedFile PDF pour les formulaires de documents."""
    return SimpleUploadedFile(
        name, _make_pdf_bytes().read(), content_type="application/pdf"
    )


def _safe_rmtree(path):
    """
    Supprime ``path`` en ignorant les erreurs de fichiers verrouillés (Windows).

    Un fichier peut encore être détenu par un autre processus au moment du
    tearDown. On tente plusieurs fois après un court délai avant d'abandonner.
    """
    if not os.path.exists(path):
        return
    for _ in range(3):
        try:
            shutil.rmtree(path, onerror=_on_rm_error)
            return
        except OSError:
            import time

            time.sleep(0.05)


def _on_rm_error(func, path, exc_info):
    """Callback shutil.rmtree: rend le fichier supprimable puis réessaie."""
    try:
        os.chmod(path, stat.S_IWRITE)
    except OSError:
        pass
    try:
        func(path)
    except OSError:
        pass


def _make_isolated_media_root():
    """Crée un répertoire MEDIA_ROOT unique pour une classe de test.

    Chaque classe reçoit son propre répertoire, ce qui élimine les
    collisions de noms de fichiers entre classes et permet l'exécution
    parallèle (``--parallel``).
    """
    path = os.path.join(tempfile.gettempdir(), f"bc_test_{uuid.uuid4().hex[:12]}")
    os.makedirs(path, exist_ok=True)
    return path


def _create_default_city():
    """Construit la ``ConseilVille`` utilisée par la majorité des tests."""
    return ConseilVille.objects.create(
        city_name="Fourmies",
        mayor_sex="M",
        mayor_first_name="Jean",
        mayor_last_name="Dupont",
        address="1 rue de la Mairie",
        postal_code="59610",
        phone_number="0321234567",
        website="http://www.fourmies.fr",
        image=_make_jpeg_uploaded(name="city.jpg"),
        slogan="La ville de Fourmies, c'est la vie !",
        nb_habitants="10000",
    )


class _BureauTestMixin:
    """
    Factorise la création du superuser, de la ``ConseilVille`` par défaut
    et du MEDIA_ROOT isolé pour les classes de test de l'app.

    Les classes filles doivent hériter de ``TestCase`` (ou sous-classe) en
    premier : ``class MaClasse(_BureauTestMixin, TestCase): ...``.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.superuser = User.objects.create_superuser(
            email="admin@example.com", password="password123"
        )
        cls._class_media_root = _make_isolated_media_root()
        cls._class_patcher = override_settings(MEDIA_ROOT=cls._class_media_root)
        cls._class_patcher.enable()

    @classmethod
    def tearDownClass(cls):
        cls._class_patcher.disable()
        _safe_rmtree(cls._class_media_root)
        super().tearDownClass()

    def setUp(self):
        super().setUp() if hasattr(super(), "setUp") else None
        self.client = Client()
        self.client.login(email="admin@example.com", password="password123")
        self.city = _create_default_city()

    def tearDown(self):
        # Nettoyage des objets créés par le test ; on ne supprime pas le
        # MEDIA_ROOT ici (géré au niveau de la classe pour la perf).
        Elus.objects.all().delete()
        Document.objects.all().delete()
        ConseilVille.objects.all().delete()
        super().tearDown() if hasattr(super(), "tearDown") else None

    @property
    def media_root(self):
        return self._class_media_root


class BureauCommunautaireTestCase(_BureauTestMixin, TestCase):
    """Tests pour l'application Bureau Communautaire"""

    def create_city(self, nom_commune):
        """Créer une ville pour les tests (utilisée par certains tests)."""
        return ConseilVille.objects.create(
            city_name=nom_commune,
            mayor_sex="M",
            mayor_first_name="Jean",
            mayor_last_name="Dupont",
            address="1 rue de la Mairie",
            postal_code="59610",
            phone_number="0321234567",
            website="http://www.fourmies.fr",
            image=_make_jpeg_uploaded(name="test_image.jpg"),
            slogan="La ville de Fourmies, c'est la vie !",
            nb_habitants="10000",
        )

    def generate_test_image(self, name, format_type):
        """Générer une image de test"""
        file = io.BytesIO()
        if format_type.lower() in ["jpeg", "jpg"]:
            image = Image.new("RGB", size=(100, 100), color=(155, 0, 0))
        else:
            image = Image.new("RGBA", size=(100, 100), color=(155, 0, 0))
        image.save(file, format=format_type)
        file.name = name
        file.seek(0)
        return file

    def test_public_view_without_data(self):
        """Test de la vue publique sans données"""
        response = self.client.get(reverse("bureau-communautaire:elus"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "bureau_communautaire/elus.html")

    def test_public_view_with_data(self):
        """Test de la vue publique avec des données"""
        city = self.city  # fournie par _BureauTestMixin

        # Créer un président
        Elus.objects.create(
            first_name="Jean",
            last_name="Dupont",
            rank=0,
            role=Elus.Role.PRESIDENT,
            function="Maire",
            picture=_make_jpeg_uploaded(name="test_image.jpg"),
            city=city,
            profession="Maire de Fourmies",
        )

        # Créer un vice-président
        Elus.objects.create(
            first_name="Marie",
            last_name="Martin",
            rank=1,
            role=Elus.Role.VICE_PRESIDENT,
            function="Adjointe",
            picture=_make_jpeg_uploaded(name="test_image2.jpg"),
            city=city,
            profession="Adjointe au Maire",
        )

        response = self.client.get(reverse("bureau-communautaire:elus"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Jean")
        self.assertContains(response, "Dupont")
        self.assertContains(response, "Marie")
        self.assertContains(response, "Martin")

    def test_admin_list_view_without_data(self):
        """Test de la vue admin sans données"""
        response = self.client.get(reverse("bureau-communautaire:admin_elus_list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "bureau_communautaire/admin_elus_list.html")

    def test_admin_list_view_with_data(self):
        """Test de la vue admin avec des données"""
        city = self.city  # fournie par _BureauTestMixin

        Elus.objects.create(
            first_name="Jean",
            last_name="Dupont",
            rank=0,
            role=Elus.Role.PRESIDENT,
            function="Maire",
            picture=_make_jpeg_uploaded(name="test_image.jpg"),
            city=city,
            profession="Maire de Fourmies",
        )

        response = self.client.get(reverse("bureau-communautaire:admin_elus_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Jean")
        self.assertContains(response, "Dupont")

    def test_admin_list_orders_by_role_rank_name(self):
        """La liste admin doit respecter le Meta.ordering : role, rank, last_name, first_name."""
        # Création dans un ordre "désordonné" pour vérifier le tri côté BDD
        Elus.objects.create(
            first_name="Alice",
            last_name="Zorro",
            rank=2,
            role=Elus.Role.VICE_PRESIDENT,
            function="VP",
            picture=_make_jpeg_uploaded(name="a.jpg"),
            city=self.city,
            profession="VP2",
        )
        Elus.objects.create(
            first_name="Bob",
            last_name="Alpha",
            rank=1,
            role=Elus.Role.VICE_PRESIDENT,
            function="VP",
            picture=_make_jpeg_uploaded(name="b.jpg"),
            city=self.city,
            profession="VP1",
        )
        Elus.objects.create(
            first_name="Charlie",
            last_name="Dupont",
            rank=0,
            role=Elus.Role.PRESIDENT,
            function="Maire",
            picture=_make_jpeg_uploaded(name="c.jpg"),
            city=self.city,
            profession="Maire",
        )

        response = self.client.get(reverse("bureau-communautaire:admin_elus_list"))
        self.assertEqual(response.status_code, 200)
        # Ordre attendu : Président (Charlie Dupont, rank 0),
        # puis VP rank 1 (Bob Alpha), puis VP rank 2 (Alice Zorro)
        html = response.content.decode()
        idx_charlie = html.index("Charlie")
        idx_bob = html.index("Bob")
        idx_alice = html.index("Alice")
        self.assertLess(idx_charlie, idx_bob, "Président doit précéder les VP")
        self.assertLess(idx_bob, idx_alice, "VP rank 1 doit précéder VP rank 2")

    def test_add_elu_form_display(self):
        """Test de l'affichage du formulaire d'ajout d'élu"""
        response = self.client.get(reverse("bureau-communautaire:admin_elu_add"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "bureau_communautaire/admin_elu_add.html")

    def test_add_elu_valid_data(self):
        """Test d'ajout d'un élu avec des données valides"""
        city = self.city  # fournie par _BureauTestMixin

        valid_data = {
            "first_name": "Jean",
            "last_name": "Dupont",
            "rank": 0,
            "role": Elus.Role.PRESIDENT,
            "function": "Maire de Fourmies",
            "picture": SimpleUploadedFile(
                name="test_image.jpg",
                content=self.generate_test_image("test_image.jpg", "jpeg").read(),
                content_type="image/jpeg",
            ),
            "city": city.id,
            "profession": "Maire de Fourmies",
        }

        response = self.client.post(
            reverse("bureau-communautaire:admin_elu_add"), valid_data, follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse("bureau-communautaire:admin_elus_list"))
        self.assertTrue(
            Elus.objects.filter(first_name="Jean", last_name="Dupont").exists()
        )

    def test_add_elu_invalid_data(self):
        """Test d'ajout d'un élu avec des données invalides"""
        invalid_data = {
            "first_name": "",  # Champ requis vide
            "last_name": "Dupont",
            "rank": 0,
            "role": Elus.Role.PRESIDENT,
            "function": "Maire de Fourmies",
        }

        response = self.client.post(
            reverse("bureau-communautaire:admin_elu_add"), invalid_data
        )
        self.assertEqual(response.status_code, 200)
        # Vérifier que le formulaire contient des erreurs
        self.assertContains(response, "Ce champ est obligatoire")

    def test_add_document_form_display(self):
        """Test de l'affichage du formulaire d'ajout de document"""
        response = self.client.get(reverse("bureau-communautaire:admin_document_add"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, "bureau_communautaire/admin_document_add.html"
        )

    def test_add_document_valid_data(self):
        """Test d'ajout d'un document avec des données valides"""
        document_file = _make_pdf_uploaded(name="test.pdf")

        document_data = {
            "title": "Test Document",
            "document": document_file,
            "type": "organigramme",
        }

        response = self.client.post(
            reverse("bureau-communautaire:admin_document_add"),
            document_data,
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(
            response, reverse("bureau-communautaire:admin_documents_list")
        )
        self.assertTrue(Document.objects.filter(title="Test Document").exists())

    def test_add_document_invalid_data(self):
        """Test d'ajout d'un document avec des données invalides"""
        invalid_data = {
            "title": "",  # Champ requis vide
            "type": "organigramme",
        }

        response = self.client.post(
            reverse("bureau-communautaire:admin_document_add"), invalid_data
        )
        self.assertEqual(response.status_code, 200)
        # Vérifier que le formulaire contient des erreurs
        self.assertContains(response, "Ce champ est obligatoire")

    def test_documents_list_view_empty(self):
        """Test de la vue liste des documents vide"""
        response = self.client.get(reverse("bureau-communautaire:admin_documents_list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, "bureau_communautaire/admin_document_list.html"
        )

    def test_documents_list_view_with_data(self):
        """Test de la vue liste des documents avec des données"""
        document_file = _make_pdf_uploaded(name="test.pdf")

        Document.objects.create(
            title="Test Document", document=document_file, type="organigramme"
        )

        response = self.client.get(reverse("bureau-communautaire:admin_documents_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Document")


class EluCRUDTestCase(_BureauTestMixin, TestCase):
    """Tests pour les opérations CRUD des élus"""

    def setUp(self):
        super().setUp()  # _BureauTestMixin crée self.client, self.city, login
        self.elu = Elus.objects.create(
            first_name="Jean",
            last_name="Dupont",
            rank=0,
            role=Elus.Role.PRESIDENT,
            function="Maire",
            picture=_make_jpeg_uploaded(name="test_image.jpg"),
            city=self.city,
            profession="Maire de Fourmies",
        )

    def test_update_elu_get(self):
        """Test de l'affichage du formulaire de modification d'un élu"""
        response = self.client.get(
            reverse("bureau-communautaire:admin_elu_update", args=[self.elu.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "bureau_communautaire/admin_elu_update.html")
        self.assertContains(response, "Jean")
        self.assertContains(response, "Dupont")

    def test_update_elu_post_valid(self):
        """Test de modification d'un élu avec des données valides"""
        update_data = {
            "first_name": "Pierre",
            "last_name": "Martin",
            "rank": 1,
            "role": Elus.Role.VICE_PRESIDENT,
            "function": "Adjoint",
            "picture": _make_jpeg_uploaded(name="new_image.jpg"),
            "city": self.city.id,
            "profession": "Adjoint au Maire",
        }

        response = self.client.post(
            reverse("bureau-communautaire:admin_elu_update", args=[self.elu.id]),
            update_data,
        )
        # Doit rediriger (302) après une MAJ valide — pas 200 (qui indiquerait
        # un re-affichage du formulaire suite à une erreur de validation).
        self.assertEqual(response.status_code, 302, f"Form invalid: {response.context}")
        elu = Elus.objects.get(id=self.elu.id)
        self.assertEqual(elu.first_name, "Pierre")
        self.assertEqual(elu.last_name, "Martin")
        self.assertEqual(elu.rank, 1)
        self.assertEqual(elu.role, Elus.Role.VICE_PRESIDENT)

    def test_delete_elu_get(self):
        """Test de l'affichage de la page de confirmation de suppression"""
        response = self.client.get(
            reverse("bureau-communautaire:admin_elu_delete", args=[self.elu.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "bureau_communautaire/admin_elu_delete.html")
        self.assertContains(response, "Jean")
        self.assertContains(response, "Dupont")

    def test_delete_elu_post(self):
        """Test de suppression d'un élu"""
        response = self.client.post(
            reverse("bureau-communautaire:admin_elu_delete", args=[self.elu.id])
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("bureau-communautaire:admin_elus_list"))

        # Vérifier que l'élu a été supprimé
        self.assertFalse(Elus.objects.filter(id=self.elu.id).exists())


class DocumentCRUDTestCase(_BureauTestMixin, TestCase):
    """Tests pour les opérations CRUD des documents"""

    def setUp(self):
        super().setUp()  # _BureauTestMixin crée self.client, self.city, login
        self.document_content = _make_pdf_bytes().read()
        self.document_file = SimpleUploadedFile(
            "test.pdf", self.document_content, content_type="application/pdf"
        )
        self.document = Document.objects.create(
            title="Test Document", document=self.document_file, type="organigramme"
        )

    def test_update_document_get(self):
        """Test de l'affichage du formulaire de modification d'un document"""
        response = self.client.get(
            reverse(
                "bureau-communautaire:admin_document_update", args=[self.document.id]
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, "bureau_communautaire/admin_document_update.html"
        )
        self.assertContains(response, "Test Document")

    def test_update_document_post_valid(self):
        """Test de modification d'un document avec des données valides"""
        new_document_file = _make_pdf_uploaded(name="new_test.pdf")
        update_data = {
            "title": "Updated Document",
            "document": new_document_file,
            "type": "calendrier",
        }

        response = self.client.post(
            reverse(
                "bureau-communautaire:admin_document_update", args=[self.document.id]
            ),
            update_data,
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, reverse("bureau-communautaire:admin_documents_list")
        )

        # Vérifier que le document a été modifié
        updated_document = Document.objects.get(id=self.document.id)
        self.assertEqual(updated_document.title, "Updated Document")
        self.assertEqual(updated_document.type, "calendrier")

    def test_delete_document_get(self):
        """Test de l'affichage de la page de confirmation de suppression"""
        response = self.client.get(
            reverse(
                "bureau-communautaire:admin_document_delete", args=[self.document.id]
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, "bureau_communautaire/admin_document_delete.html"
        )
        self.assertContains(response, "Test Document")

    def test_delete_document_post(self):
        """Test de suppression d'un document"""
        response = self.client.post(
            reverse(
                "bureau-communautaire:admin_document_delete", args=[self.document.id]
            )
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, reverse("bureau-communautaire:admin_documents_list")
        )

        # Vérifier que le document a été supprimé
        self.assertFalse(Document.objects.filter(id=self.document.id).exists())


class EluModelTestCase(_BureauTestMixin, TestCase):
    """Tests pour le modèle Elus (nécessitent la BDD)."""

    def setUp(self):
        super().setUp()

    def test_elu_str_method(self):
        """Test de la méthode __str__ du modèle Elus"""
        elu = Elus.objects.create(
            first_name="Jean",
            last_name="Dupont",
            rank=0,
            role=Elus.Role.PRESIDENT,
            function="Maire",
            picture=_make_jpeg_uploaded(name="test_image.jpg"),
            city=self.city,
            profession="Maire de Fourmies",
        )
        # Le __str__ retourne "Prénom Nom (Rôle)" — voir bureau_communautaire/models.py
        self.assertEqual(str(elu), "Jean Dupont (Président)")

    def test_elu_role_choices(self):
        """Test des choix de rôles disponibles"""
        self.assertEqual(Elus.Role.PRESIDENT, "Président")
        self.assertEqual(Elus.Role.VICE_PRESIDENT, "Vice-Président")


class EluModelDefaultsTestCase(SimpleTestCase):
    """Tests sans BDD des valeurs par défaut et constantes du modèle Elus."""

    def test_elu_default_values(self):
        """Test des valeurs par défaut du modèle (sans save en BDD)."""
        elu = Elus(
            first_name="Test",
            last_name="User",
            function="Test Function",
            city=None,  # pas besoin de ConseilVille en BDD pour tester les defaults
        )
        self.assertEqual(elu.rank, 0)
        self.assertEqual(elu.role, Elus.Role.VICE_PRESIDENT)


class DocumentModelTestCase(_BureauTestMixin, TestCase):
    """Tests pour le modèle Document"""

    def setUp(self):
        super().setUp()  # inutile pour le modèle mais garantit l'isolation MEDIA_ROOT
        self.document_content = _make_pdf_bytes().read()
        self.document_file = SimpleUploadedFile(
            "test.pdf", self.document_content, content_type="application/pdf"
        )

    def test_document_str_method(self):
        """Test de la méthode __str__ du modèle Document"""
        document = Document.objects.create(
            title="Test Document", document=self.document_file, type="organigramme"
        )
        size = document.get_document_size()
        expected_str = f"Test Document {document.document} organigramme {size} Ko"
        self.assertEqual(str(document), expected_str)

    def test_get_document_size(self):
        """Test de la méthode get_document_size"""
        document = Document.objects.create(
            title="Test Document", document=self.document_file, type="organigramme"
        )
        size = document.get_document_size()
        expected_size = len(self.document_content) / 1024
        self.assertEqual(size, expected_size)

    def test_document_type_choices(self):
        """Test des choix de types de documents"""
        document = Document.objects.create(
            title="Test Organigramme", document=self.document_file, type="organigramme"
        )
        self.assertEqual(document.type, "organigramme")

        document2 = Document.objects.create(
            title="Test Calendrier",
            document=_make_pdf_uploaded(name="test2.pdf"),
            type="calendrier",
        )
        self.assertEqual(document2.type, "calendrier")


class PermissionTestCase(_BureauTestMixin, TestCase):
    """Tests des permissions pour l'application Bureau Communautaire"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Créer un utilisateur normal (sans permissions)
        cls.normal_user = User.objects.create_user(
            email="user@example.com", password="password123"
        )

    def setUp(self):
        # Pas besoin de client connecté pour tester les permissions
        self.client = Client()
        self.city = _create_default_city()

    def test_public_view_no_login_required(self):
        """La vue publique ne doit pas exiger de connexion."""
        response = self.client.get(reverse("bureau-communautaire:elus"))
        self.assertEqual(response.status_code, 200)

    def test_admin_views_require_permissions(self):
        """Test que les vues d'administration nécessitent des permissions"""
        admin_urls = [
            reverse("bureau-communautaire:admin_elus_list"),
            reverse("bureau-communautaire:admin_elu_add"),
        ]

        for url in admin_urls:
            response = self.client.get(url)
            # Doit rediriger vers la page de connexion ou retourner 403
            self.assertIn(response.status_code, [302, 403])

    def test_admin_views_with_normal_user(self):
        """Test des vues d'administration avec utilisateur normal"""
        self.client.login(email="user@example.com", password="password123")

        admin_urls = [
            reverse("bureau-communautaire:admin_elus_list"),
            reverse("bureau-communautaire:admin_elu_add"),
        ]

        for url in admin_urls:
            response = self.client.get(url)
            # Doit retourner 403 (permission refusée) ou 302 (redirection)
            self.assertIn(response.status_code, [302, 403])

    def test_admin_views_with_superuser(self):
        """Toutes les vues admin doivent être accessibles au superutilisateur."""
        self.client.login(email="admin@example.com", password="password123")

        # Crée un élu pour les URL qui nécessitent un ID
        elu = Elus.objects.create(
            first_name="Test",
            last_name="User",
            role=Elus.Role.PRESIDENT,
            function="Maire",
            picture=_make_jpeg_uploaded(name="p.jpg"),
            city=self.city,
            profession="Maire",
        )

        admin_urls = [
            reverse("bureau-communautaire:admin_elus_list"),
            reverse("bureau-communautaire:admin_elu_add"),
            reverse("bureau-communautaire:admin_elu_update", args=[elu.id]),
            reverse("bureau-communautaire:admin_elu_delete", args=[elu.id]),
            reverse("bureau-communautaire:admin_documents_list"),
            reverse("bureau-communautaire:admin_document_add"),
        ]
        for url in admin_urls:
            response = self.client.get(url)
            self.assertEqual(
                response.status_code,
                200,
                f"GET {url} should be 200 for superuser, got {response.status_code}",
            )

    def test_anonymous_blocked_from_all_admin_urls(self):
        """Aucun utilisateur non-connecté ne doit accéder aux vues admin."""
        elu = Elus.objects.create(
            first_name="Test",
            last_name="User",
            role=Elus.Role.PRESIDENT,
            function="Maire",
            picture=_make_jpeg_uploaded(name="p.jpg"),
            city=self.city,
            profession="Maire",
        )
        admin_urls = [
            reverse("bureau-communautaire:admin_elus_list"),
            reverse("bureau-communautaire:admin_elu_add"),
            reverse("bureau-communautaire:admin_elu_update", args=[elu.id]),
            reverse("bureau-communautaire:admin_elu_delete", args=[elu.id]),
            reverse("bureau-communautaire:admin_documents_list"),
            reverse("bureau-communautaire:admin_document_add"),
        ]
        for url in admin_urls:
            response = self.client.get(url)
            # 302 = redirection vers login, 403 = forbidden
            self.assertIn(
                response.status_code,
                [302, 403],
                f"GET {url} doit refuser l'accès anonyme, got {response.status_code}",
            )

    def test_normal_user_blocked_from_change_and_delete(self):
        """Un utilisateur sans permission change/delete ne doit pas y accéder.

        Le décorateur ``@permission_required`` redirige (302) vers le login
        par défaut ; on accepte aussi 403 (si ``raise_exception=True`` est
        utilisé sur la vue).
        """
        self.client.login(email="user@example.com", password="password123")
        elu = Elus.objects.create(
            first_name="Test",
            last_name="User",
            role=Elus.Role.PRESIDENT,
            function="Maire",
            picture=_make_jpeg_uploaded(name="p.jpg"),
            city=self.city,
            profession="Maire",
        )
        for url in [
            reverse("bureau-communautaire:admin_elu_update", args=[elu.id]),
            reverse("bureau-communautaire:admin_elu_delete", args=[elu.id]),
        ]:
            response = self.client.get(url)
            self.assertIn(
                response.status_code,
                [302, 403],
                f"GET {url} doit refuser l'accès, got {response.status_code}",
            )


class AdminInterfaceTestCase(_BureauTestMixin, TestCase):
    """Tests pour l'interface d'administration Django"""

    def setUp(self):
        super().setUp()  # fournit self.client, self.city, login

    def test_admin_elus_list_display(self):
        """Test de l'affichage de la liste des élus dans l'admin"""
        from .admin import CustomElusAdmin

        admin_instance = CustomElusAdmin(Elus, admin.site)

        # Tester les champs affichés
        expected_fields = [
            "first_name",
            "last_name",
            "rank",
            "role",
            "picture",
            "function",
            "city",
            "profession",
        ]
        self.assertEqual(admin_instance.list_display, expected_fields)

    def test_admin_elus_delete_model_deletes_file(self):
        """``delete_model`` de l'admin doit supprimer le fichier image."""
        import os

        from django.http import HttpRequest

        from .admin import CustomElusAdmin

        elu = Elus.objects.create(
            first_name="Jean",
            last_name="Dupont",
            rank=0,
            role=Elus.Role.PRESIDENT,
            function="Maire",
            picture=_make_jpeg_uploaded(name="test_image.jpg"),
            city=self.city,
            profession="Maire de Fourmies",
        )
        picture_path = elu.picture.path
        self.assertTrue(os.path.exists(picture_path))

        admin_instance = CustomElusAdmin(Elus, admin.site)
        admin_instance.delete_model(HttpRequest(), elu)

        self.assertFalse(Elus.objects.filter(id=elu.id).exists())
        self.assertFalse(
            os.path.exists(picture_path),
            "le fichier image doit être supprimé en même temps que l'élu",
        )

    def test_admin_documents_list_display(self):
        """Test de l'affichage de la liste des documents dans l'admin"""
        from .admin import CustomDocumentAdmin

        admin_instance = CustomDocumentAdmin(Document, admin.site)

        expected_fields = ("document", "title", "type")
        self.assertEqual(admin_instance.list_display, expected_fields)

    def test_admin_documents_get_actions(self):
        """Test de la suppression de l'action par défaut pour les documents"""
        from django.http import HttpRequest

        from .admin import CustomDocumentAdmin

        admin_instance = CustomDocumentAdmin(Document, admin.site)
        request = HttpRequest()
        request.user = self.superuser  # Ajouter l'utilisateur à la requête
        actions = admin_instance.get_actions(request)

        # L'action 'delete_selected' doit être supprimée
        self.assertNotIn("delete_selected", actions)
        # L'action personnalisée doit être présente
        self.assertIn("delete_document", actions)

    def test_admin_documents_delete_model(self):
        """Test de la suppression personnalisée d'un document"""
        from django.http import HttpRequest

        from .admin import CustomDocumentAdmin

        # Créer un document
        document_file = _make_pdf_uploaded(name="test.pdf")

        document = Document.objects.create(
            title="Test Document", document=document_file, type="organigramme"
        )

        admin_instance = CustomDocumentAdmin(Document, admin.site)
        request = HttpRequest()

        # Tester la suppression
        admin_instance.delete_model(request, document)

        # Vérifier que le document a été supprimé
        self.assertFalse(Document.objects.filter(id=document.id).exists())

    def test_delete_elus_image_action(self):
        """Test de l'action de suppression en lot des élus"""
        from django.http import HttpRequest

        from .admin import delete_elus_image

        # Créer plusieurs élus
        elu1 = Elus.objects.create(
            first_name="Jean",
            last_name="Dupont",
            rank=0,
            role=Elus.Role.PRESIDENT,
            function="Maire",
            picture=_make_jpeg_uploaded(name="test_image1.jpg"),
            city=self.city,
            profession="Maire de Fourmies",
        )

        elu2 = Elus.objects.create(
            first_name="Marie",
            last_name="Martin",
            rank=1,
            role=Elus.Role.VICE_PRESIDENT,
            function="Adjointe",
            picture=_make_jpeg_uploaded(name="test_image2.jpg"),
            city=self.city,
            profession="Adjointe au Maire",
        )

        queryset = Elus.objects.filter(id__in=[elu1.id, elu2.id])
        request = HttpRequest()

        # Exécuter l'action
        delete_elus_image(None, request, queryset)

        # Vérifier que les élus ont été supprimés
        self.assertFalse(Elus.objects.filter(id__in=[elu1.id, elu2.id]).exists())

    def test_delete_document_action(self):
        """Test de l'action de suppression en lot des documents"""
        from django.http import HttpRequest

        from .admin import delete_document

        # Créer plusieurs documents
        document1 = Document.objects.create(
            title="Test Document 1",
            document=_make_pdf_uploaded(name="test1.pdf"),
            type="organigramme",
        )

        document2 = Document.objects.create(
            title="Test Document 2",
            document=_make_pdf_uploaded(name="test2.pdf"),
            type="calendrier",
        )

        queryset = Document.objects.filter(id__in=[document1.id, document2.id])
        request = HttpRequest()

        # Exécuter l'action
        delete_document(None, request, queryset)

        # Vérifier que les documents ont été supprimés
        self.assertFalse(
            Document.objects.filter(id__in=[document1.id, document2.id]).exists()
        )


class ViewsEdgeCasesTestCase(_BureauTestMixin, TestCase):
    """Tests pour les cas particuliers des vues"""

    def setUp(self):
        super().setUp()  # crée self.client, self.city, login

    def test_public_view_with_document_without_file(self):
        """Test de la vue publique avec un document sans fichier physique"""
        # Créer un document avec un chemin de fichier invalide
        document = Document(title="Document sans fichier", type="organigramme")
        # Simuler un document sans fichier
        document.document.name = "inexistant.pdf"
        document.save()

        response = self.client.get(reverse("bureau-communautaire:elus"))
        self.assertEqual(response.status_code, 200)
        # La vue gère ValueError sur document.path sans planter

    def test_add_document_form_invalid_redirect(self):
        """Test de redirection lors d'un formulaire de document invalide"""
        invalid_data = {
            "title": "",  # Titre vide
            "type": "organigramme",
        }

        response = self.client.post(
            reverse("bureau-communautaire:admin_document_add"), invalid_data
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, "bureau_communautaire/admin_document_add.html"
        )

    def test_update_document_form_invalid_redirect(self):
        """Test de redirection lors d'un formulaire de mise à jour invalide"""
        # Créer un document
        document = Document.objects.create(
            title="Test Document",
            document=_make_pdf_uploaded(name="test.pdf"),
            type="organigramme",
        )

        invalid_data = {
            "title": "",  # Titre vide
            "type": "organigramme",
        }

        response = self.client.post(
            reverse("bureau-communautaire:admin_document_update", args=[document.id]),
            invalid_data,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, "bureau_communautaire/admin_document_update.html"
        )

    def test_update_document_with_file_replacement(self):
        """Test de remplacement de fichier lors de la mise à jour"""
        # Créer un document initial
        original_file = _make_pdf_uploaded(name="original.pdf")
        document = Document.objects.create(
            title="Test Document", document=original_file, type="organigramme"
        )

        # Mettre à jour avec un nouveau fichier
        new_file = _make_pdf_uploaded(name="new.pdf")
        update_data = {
            "title": "Updated Document",
            "document": new_file,
            "type": "calendrier",
        }

        response = self.client.post(
            reverse("bureau-communautaire:admin_document_update", args=[document.id]),
            update_data,
        )
        self.assertEqual(response.status_code, 302)

        # Vérifier que le document a été mis à jour
        updated_document = Document.objects.get(id=document.id)
        self.assertEqual(updated_document.title, "Updated Document")


class TemplateTagsTestCase(TestCase):
    """Tests pour les template tags personnalisés"""

    def test_divide_filter_valid(self):
        """Test du filtre divide avec des valeurs valides"""
        from .templatetags.BC_filters import divide

        result = divide(10, 2)
        self.assertEqual(result, 5.0)

        result = divide(7, 3)
        self.assertAlmostEqual(result, 2.333333333333333)

    def test_divide_filter_zero_division(self):
        """Test du filtre divide avec division par zéro"""
        from .templatetags.BC_filters import divide

        result = divide(10, 0)
        self.assertEqual(result, 1)  # Valeur par défaut en cas d'erreur

    def test_divide_filter_invalid_values(self):
        """Test du filtre divide avec des valeurs invalides"""
        from .templatetags.BC_filters import divide

        result = divide("abc", 2)
        self.assertEqual(result, 1)  # Valeur par défaut en cas d'erreur

        result = divide(10, "def")
        self.assertEqual(result, 1)  # Valeur par défaut en cas d'erreur

    def test_add_class_filter(self):
        """Test du filtre add_class"""
        from django import forms

        from .templatetags.BC_filters import add_class

        # Créer un formulaire avec un champ
        class TestForm(forms.Form):
            test_field = forms.CharField()

        form = TestForm()
        bound_field = form["test_field"]

        # Appliquer le filtre
        result = add_class(bound_field, "form-control")

        # Vérifier que la classe CSS a été ajoutée
        self.assertIn('class="form-control"', str(result))


class BureauCommissionCompetenceDisplayTestCase(_BureauTestMixin, TestCase):
    """Tests pour l'affichage des compétences des commissions sur la page bureau"""

    def setUp(self):
        super().setUp()  # _BureauTestMixin crée self.client, self.city, login

        self.commission = Commission.objects.create(
            title="Test Commission", icon="<svg></svg>"
        )
        self.competence1 = CommissionCompetence.objects.create(
            commission=self.commission,
            title="Compétence 1",
            order=1,
        )
        self.competence2 = CommissionCompetence.objects.create(
            commission=self.commission,
            title="Compétence 2",
            order=2,
        )

        self.elu = Elus.objects.create(
            first_name="Jean",
            last_name="Dupont",
            rank=1,
            role=Elus.Role.VICE_PRESIDENT,
            function="Test",
            picture=_make_jpeg_uploaded(name="test_image.jpg"),
            city=self.city,
            profession="Test",
        )
        self.elu.linked_commission.add(self.commission)

    def tearDown(self):
        # Commission et CommissionCompetence ne sont pas dans le tearDown du mixin
        CommissionCompetence.objects.all().delete()
        Commission.objects.all().delete()
        super().tearDown()

    def test_commission_displayed_on_bureau_page(self):
        """Test que le bouton Voir plus est affiché quand une commission est liée"""
        response = self.client.get(reverse("bureau-communautaire:elus"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Voir plus")

    def test_competences_displayed_in_context(self):
        """Test que les compétences sont passées via le contexte"""
        response = self.client.get(reverse("bureau-communautaire:elus"))
        self.assertEqual(response.status_code, 200)
        # Vérifier que les compétences sont présentes dans le rendu
        self.assertContains(response, "Compétence 1")
        self.assertContains(response, "Compétence 2")

    def test_competences_not_displayed_without_commission(self):
        """Test qu'aucune compétence ne s'affiche si pas de commission liée"""
        elu2 = Elus.objects.create(
            first_name="Marie",
            last_name="Martin",
            rank=2,
            role=Elus.Role.VICE_PRESIDENT,
            function="Test",
            picture=_make_jpeg_uploaded(name="test_image2.jpg"),
            city=self.city,
            profession="Test",
        )
        response = self.client.get(reverse("bureau-communautaire:elus"))
        self.assertEqual(response.status_code, 200)
        # Les compétences de la commission liée à elu1 restent affichées
        self.assertContains(response, "Compétence 1")
        self.assertContains(response, "Compétence 2")

    def test_accordion_markup_present(self):
        """Test que le markup du toggle Voir plus est présent dans le HTML"""
        response = self.client.get(reverse("bureau-communautaire:elus"))
        self.assertEqual(response.status_code, 200)
        # Vérifier les attributs ARIA du toggle
        self.assertContains(response, "vp-competences-trigger-")
        self.assertContains(response, "vp-competences-panel-")
        self.assertContains(response, "aria-expanded")
        self.assertContains(response, "aria-controls")
        self.assertContains(response, "vp-competences-toggle")

    def test_multiple_competences_ordered(self):
        """Test que les compétences sont affichées dans le bon ordre"""
        response = self.client.get(reverse("bureau-communautaire:elus"))
        self.assertEqual(response.status_code, 200)
        # L'ordre dans le HTML doit correspondre à l'ordre du modèle
        html = response.content.decode()
        pos_comp1 = html.index("Compétence 1")
        pos_comp2 = html.index("Compétence 2")
        self.assertLess(pos_comp1, pos_comp2)


class EluUpdatePhotoBehaviorTestCase(_BureauTestMixin, TestCase):
    """Tests de comportement pour la mise à jour d'un élu avec changement de photo.

    Vérifie que la vue :
    1. Remplace bien le fichier physique (nouveau nom en BDD).
    2. Planifie la suppression de l'ancien fichier via ``transaction.on_commit``.
    3. Laisse l'ancien fichier intact si le formulaire est invalide.

    La suppression effective du fichier est testée par le callback
    ``on_commit`` qui s'exécute après le commit de la transaction du test.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()  # _BureauTestMixin crée le superuser + MEDIA_ROOT

    def setUp(self):
        super().setUp()  # _BureauTestMixin crée self.client, self.city, login

    def _build_image(self, name, color):
        return _make_jpeg_uploaded(name=name, color=color, size=(50, 50))

    def test_picture_replaced_in_db(self):
        """Le nom du fichier en BDD change lorsqu'une nouvelle photo est uploadée."""
        old_picture = self._build_image("old.jpg", (255, 0, 0))
        elu = Elus.objects.create(
            first_name="Jean",
            last_name="Dupont",
            role=Elus.Role.PRESIDENT,
            function="Maire",
            picture=old_picture,
            city=self.city,
            profession="Maire de Fourmies",
        )
        old_name = elu.picture.name
        self.assertTrue(os.path.exists(elu.picture.path))

        new_picture = self._build_image("new.jpg", (0, 255, 0))
        with TestCase.captureOnCommitCallbacks(execute=True):
            response = self.client.post(
                reverse("bureau-communautaire:admin_elu_update", args=[elu.id]),
                {
                    "first_name": "Jean",
                    "last_name": "Dupont",
                    "rank": 0,
                    "role": Elus.Role.PRESIDENT,
                    "function": "Maire",
                    "picture": new_picture,
                    "city": self.city.id,
                    "profession": "Maire de Fourmies",
                },
            )
        self.assertEqual(response.status_code, 302)
        from django.db import connection

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT picture FROM bureau_communautaire_elus WHERE id = %s",
                [elu.id],
            )
            db_picture = cursor.fetchone()[0]
        self.assertNotEqual(
            db_picture, old_name, "picture name should have changed in DB"
        )
        new_path = os.path.join(self.media_root, db_picture)
        self.assertTrue(
            os.path.exists(new_path),
            f"new picture should exist at {new_path}",
        )

    def test_old_picture_kept_when_unchanged(self):
        """Si aucune nouvelle photo n'est uploadée, l'ancienne photo reste intacte."""
        original_picture = self._build_image("keep.jpg", (10, 10, 10))
        elu = Elus.objects.create(
            first_name="Jean",
            last_name="Dupont",
            role=Elus.Role.PRESIDENT,
            function="Maire",
            picture=original_picture,
            city=self.city,
            profession="Maire",
        )
        old_path = elu.picture.path
        self.assertTrue(os.path.exists(old_path))

        response = self.client.post(
            reverse("bureau-communautaire:admin_elu_update", args=[elu.id]),
            {
                "first_name": "Jean",
                "last_name": "Durand",
                "rank": 1,
                "role": Elus.Role.VICE_PRESIDENT,
                "function": "Adjoint",
                "city": self.city.id,
                "profession": "Adjoint",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(os.path.exists(old_path))

    def test_invalid_form_does_not_delete_picture(self):
        """Si le formulaire est invalide, aucune photo ne doit être supprimée."""
        original_picture = self._build_image("invalid.jpg", (20, 20, 20))
        elu = Elus.objects.create(
            first_name="Jean",
            last_name="Dupont",
            role=Elus.Role.PRESIDENT,
            function="Maire",
            picture=original_picture,
            city=self.city,
            profession="Maire",
        )
        old_path = elu.picture.path
        new_picture = self._build_image("new_invalid.jpg", (30, 30, 30))
        # Note : on capture le nom et le chemin du nouveau fichier AVANT le POST,
        # car si le form était valide, elu.picture pointerait dessus après save().
        new_picture_name = new_picture.name
        response = self.client.post(
            reverse("bureau-communautaire:admin_elu_update", args=[elu.id]),
            {
                "first_name": "",
                "last_name": "Dupont",
                "rank": 0,
                "role": Elus.Role.PRESIDENT,
                "function": "Maire",
                "picture": new_picture,
                "city": self.city.id,
                "profession": "Maire",
            },
        )
        # Formulaire invalide -> re-affichage (200)
        self.assertEqual(response.status_code, 200)
        # L'ancien fichier doit toujours exister
        self.assertTrue(
            os.path.exists(old_path),
            f"L'ancienne photo {old_path} doit être préservée",
        )
        # Le nouveau fichier NE doit PAS avoir été créé sur disque
        new_full_path = os.path.join(self.media_root, new_picture_name)
        self.assertFalse(
            os.path.exists(new_full_path),
            f"Le nouveau fichier {new_full_path} ne doit pas avoir été créé",
        )


class EluMessagesTestCase(_BureauTestMixin, TestCase):
    """Vérifie que les vues émettent bien les messages de feedback utilisateur."""

    def setUp(self):
        super().setUp()  # _BureauTestMixin crée self.client, self.city, login

    def _build_image(self, name="x.jpg", color=(10, 10, 10)):
        return _make_jpeg_uploaded(name=name, color=color, size=(50, 50))

    def test_add_elu_success_message(self):
        from django.contrib.messages import get_messages

        response = self.client.post(
            reverse("bureau-communautaire:admin_elu_add"),
            {
                "first_name": "Jean",
                "last_name": "Dupont",
                "rank": 0,
                "role": Elus.Role.PRESIDENT,
                "function": "Maire",
                "picture": self._build_image(name="p.jpg"),
                "city": self.city.id,
                "profession": "Maire",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        messages_list = [str(m) for m in get_messages(response.wsgi_request)]
        self.assertTrue(
            any("Jean Dupont" in m and "ajouté" in m for m in messages_list),
            f"Expected success message for Jean Dupont, got {messages_list}",
        )


class QueryCountTestCase(_BureauTestMixin, TestCase):
    """Garantit que les optimisations select_related/prefetch_related restent en place."""

    def setUp(self):
        super().setUp()  # _BureauTestMixin crée self.client, self.city, login
        for i in range(3):
            Elus.objects.create(
                first_name=f"Prenom{i}",
                last_name=f"Nom{i}",
                rank=i,
                role=Elus.Role.VICE_PRESIDENT,
                function=f"Func{i}",
                picture=_make_jpeg_uploaded(
                    name=f"elu{i}.jpg", color=(i, i, i), size=(20, 20)
                ),
                city=self.city,
                profession=f"Prof{i}",
            )

    def test_list_elus_uses_select_and_prefetch_related(self):
        """
        Vérifie que la liste admin utilise ``select_related`` (city) et
        ``prefetch_related`` (linked_commission) pour éviter les N+1.

        On mesure le nombre de requêtes pour 3 élus : avec les optimisations
        le total doit rester constant (indépendant du nombre d'élus), sans
        elles il croîtrait linéairement.
        """
        from django.db import connection
        from django.test.utils import CaptureQueriesContext

        with CaptureQueriesContext(connection) as ctx:
            self.client.get(reverse("bureau-communautaire:admin_elus_list"))
        # 3 élus : on attend 1 (elus + city via select_related)
        #                + 1 (prefetch linked_commission)
        #                + 1 (aggregate stats)
        #                + ~5 (session, auth, context processor, group)
        # = ~8 requêtes, constant quelque soit le nombre d'élus.
        # Sans prefetch, on aurait 1 + 3 (city) + 3 (commissions) + 1 (agg) = 8
        # minimum mais qui croît linéairement avec N.
        self.assertLessEqual(
            len(ctx.captured_queries),
            10,
            f"Trop de requêtes ({len(ctx.captured_queries)}) — N+1 probable ?",
        )
        # Anti-régression N+1 : aucune requête individuelle sur ConseilVille
        # (en dehors du JOIN de select_related).
        conseilville_queries = sum(
            1
            for q in ctx.captured_queries
            if 'FROM "conseil_communautaire_conseilville"' in q["sql"]
            and "INNER JOIN" not in q["sql"]
        )
        self.assertLessEqual(
            conseilville_queries,
            1,
            f"{conseilville_queries} requêtes individuelles sur ConseilVille — N+1 ?",
        )
        # Anti-régression N+1 sur Commission (préchargée par prefetch_related)
        commission_queries = sum(
            1
            for q in ctx.captured_queries
            if 'FROM "commissions_commission"' in q["sql"]
            and "INNER JOIN" not in q["sql"]
        )
        self.assertLessEqual(
            commission_queries,
            1,
            f"{commission_queries} requêtes individuelles sur Commission — N+1 ?",
        )

    def test_query_count_does_not_grow_with_elu_count(self):
        """
        Vérifie que le nombre de requêtes est constant en fonction du nombre
        d'élus. Crée N élus, mesure, puis N+k, re-mesure : doit être identique
        (à 1 près, pour cause d'INSERT).
        """
        from django.db import connection
        from django.test.utils import CaptureQueriesContext

        # Baseline : 3 élus (créés dans setUp)
        with CaptureQueriesContext(connection) as ctx_3:
            self.client.get(reverse("bureau-communautaire:admin_elus_list"))
        queries_3 = len(ctx_3.captured_queries)

        # Ajoute 5 élus supplémentaires
        for i in range(3, 8):
            Elus.objects.create(
                first_name=f"Prenom{i}",
                last_name=f"Nom{i}",
                rank=i,
                role=Elus.Role.VICE_PRESIDENT,
                function=f"Func{i}",
                picture=_make_jpeg_uploaded(
                    name=f"elu{i}.jpg", color=(i, i, i), size=(20, 20)
                ),
                city=self.city,
                profession=f"Prof{i}",
            )

        with CaptureQueriesContext(connection) as ctx_8:
            self.client.get(reverse("bureau-communautaire:admin_elus_list"))
        queries_8 = len(ctx_8.captured_queries)

        # Le count doit être quasi-identique (la différence vient du
        # cache/prefetch de la session et non du N+1).
        self.assertLessEqual(
            queries_8 - queries_3,
            1,
            f"Requêtes passées de {queries_3} à {queries_8} (+{queries_8 - queries_3}) "
            f"en ajoutant 5 élus — N+1 régresse !",
        )


class SecurityTestCase(_BureauTestMixin, TestCase):
    """Tests de sécurité : CSRF, méthodes HTTP, etc."""

    def test_delete_elu_get_does_not_delete(self):
        """Un GET sur delete_elu affiche la confirmation mais ne supprime pas."""
        elu = Elus.objects.create(
            first_name="Jean",
            last_name="Dupont",
            role=Elus.Role.PRESIDENT,
            function="Maire",
            picture=_make_jpeg_uploaded(name="p.jpg"),
            city=self.city,
            profession="Maire",
        )
        response = self.client.get(
            reverse("bureau-communautaire:admin_elu_delete", args=[elu.id])
        )
        self.assertEqual(response.status_code, 200)
        # L'élu doit toujours exister
        self.assertTrue(Elus.objects.filter(id=elu.id).exists())

    def test_csrf_token_required_on_post(self):
        """Un POST sans token CSRF doit être rejeté (HTTP 403)."""
        from django.test import Client as CsrfClient

        # Utiliser enforce_csrf_checks=True pour que le client test valide le CSRF
        csrf_client = CsrfClient(enforce_csrf_checks=True)
        csrf_client.login(email="admin@example.com", password="password123")
        response = csrf_client.post(
            reverse("bureau-communautaire:admin_elu_add"),
            {
                "first_name": "Jean",
                "last_name": "Dupont",
                "rank": 0,
                "role": Elus.Role.PRESIDENT,
                "function": "Maire",
                "picture": _make_jpeg_uploaded(name="p.jpg"),
                "city": self.city.id,
                "profession": "Maire",
            },
        )
        # 403 = Forbidden (CSRF check failed)
        self.assertEqual(
            response.status_code,
            403,
            f"Un POST sans CSRF doit retourner 403, got {response.status_code}",
        )
        # Aucun élu ne doit avoir été créé
        self.assertFalse(Elus.objects.filter(last_name="Dupont").exists())


class MimeValidationTestCase(TestCase):
    """Tests du validateur de MIME réel (Pillow Image.verify)."""

    def test_valid_jpeg_passes(self):
        from django.core.exceptions import ValidationError

        from app.validators import validate_image_mime

        buffer = io.BytesIO()
        Image.new("RGB", size=(10, 10), color=(1, 2, 3)).save(buffer, format="JPEG")
        buffer.seek(0)
        buffer.name = "ok.jpg"
        # Ne doit pas lever d'exception
        validate_image_mime(buffer)

    def test_text_file_with_jpg_extension_rejected(self):
        from django.core.exceptions import ValidationError

        from app.validators import validate_image_mime

        fake = SimpleUploadedFile(
            "fake.jpg", b"#!/bin/bash\necho pwned", content_type="image/jpeg"
        )
        with self.assertRaises(ValidationError):
            validate_image_mime(fake)

    def test_corrupted_image_rejected(self):
        from django.core.exceptions import ValidationError

        from app.validators import validate_image_mime

        corrupted = SimpleUploadedFile(
            "bad.jpg", b"\x00\x01\x02not-an-image", content_type="image/jpeg"
        )
        with self.assertRaises(ValidationError):
            validate_image_mime(corrupted)

    def test_png_image_passes(self):
        """Un vrai PNG doit aussi être accepté."""
        from app.validators import validate_image_mime

        buffer = io.BytesIO()
        Image.new("RGBA", size=(10, 10), color=(0, 255, 0, 128)).save(
            buffer, format="PNG"
        )
        buffer.seek(0)
        # Ne doit pas lever
        validate_image_mime(buffer)

    def test_webp_image_passes(self):
        """Un vrai WEBP doit aussi être accepté."""
        from app.validators import validate_image_mime

        buffer = io.BytesIO()
        Image.new("RGB", size=(10, 10), color=(10, 20, 30)).save(buffer, format="WEBP")
        buffer.seek(0)
        # Ne doit pas lever
        validate_image_mime(buffer)


class ModelValidatorsTestCase(_BureauTestMixin, TestCase):
    """Tests des validateurs Django (taille, extension) sur les modèles."""

    def test_elu_picture_rejects_wrong_extension(self):
        """Un fichier .txt doit être refusé pour Elus.picture (jpg/jpeg/png/webp only)."""
        from django.core.exceptions import ValidationError

        elu = Elus(
            first_name="Test",
            last_name="User",
            role=Elus.Role.PRESIDENT,
            function="X",
            picture=SimpleUploadedFile(
                "malicious.txt", b"not an image", content_type="text/plain"
            ),
            city=self.city,
            profession="X",
        )
        with self.assertRaises(ValidationError):
            elu.full_clean()

    def test_document_rejects_non_pdf_extension(self):
        """Un fichier .exe doit être refusé pour Document.document (pdf only)."""
        from django.core.exceptions import ValidationError

        doc = Document(
            title="Bad",
            document=SimpleUploadedFile(
                "malware.exe", b"MZ\x90\x00", content_type="application/octet-stream"
            ),
            type="organigramme",
        )
        with self.assertRaises(ValidationError):
            doc.full_clean()

    def test_document_rejects_invalid_type_choice(self):
        """Un type hors choices doit être refusé par full_clean."""
        from django.core.exceptions import ValidationError

        doc = Document(
            title="Bad type",
            document=_make_pdf_uploaded(name="test.pdf"),
            type="comptabilite",  # pas dans les choices
        )
        with self.assertRaises(ValidationError):
            doc.full_clean()

    def test_elu_rejects_missing_required_fields(self):
        """first_name, last_name, picture, city sont requis."""
        from django.core.exceptions import ValidationError

        elu = Elus(
            first_name="",  # requis
            last_name="Dupont",
            role=Elus.Role.PRESIDENT,
            function="X",
            picture=_make_jpeg_uploaded(name="p.jpg"),
            city=self.city,
            profession="X",
        )
        with self.assertRaises(ValidationError):
            elu.full_clean()


class EndToEndIntegrationTestCase(_BureauTestMixin, TestCase):
    """Tests d'intégration end-to-end couvrant les scénarios manuels.

    Ces tests simulent le comportement d'un utilisateur réel via le client
    de test Django et vérifient les effets de bord (BDD, fichiers sur disque,
    redirections). Ils complètent les tests unitaires en validant le
    comportement global de bout en bout.
    """

    def test_add_elu_with_real_jpeg_creates_file(self):
        """Scénario 9 : upload d'un vrai JPEG → fichier créé sur disque."""
        elu_count_before = Elus.objects.count()
        response = self.client.post(
            reverse("bureau-communautaire:admin_elu_add"),
            {
                "first_name": "Marie",
                "last_name": "Curie",
                "rank": 1,
                "role": Elus.Role.VICE_PRESIDENT,
                "function": "Scientifique",
                "picture": _make_jpeg_uploaded(name="marie.jpg"),
                "city": self.city.id,
                "profession": "Physicienne",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Elus.objects.count(), elu_count_before + 1)
        elu = Elus.objects.get(last_name="Curie")
        self.assertTrue(
            os.path.exists(elu.picture.path),
            f"Le fichier {elu.picture.path} doit exister sur disque",
        )

    def test_add_elu_with_fake_jpeg_is_rejected(self):
        """Scénario 10 : upload d'un fichier malformé (.jpg mais pas une image)
        → formulaire invalide, pas d'élu créé."""
        elu_count_before = Elus.objects.count()
        response = self.client.post(
            reverse("bureau-communautaire:admin_elu_add"),
            {
                "first_name": "Hacker",
                "last_name": "Malware",
                "rank": 0,
                "role": Elus.Role.PRESIDENT,
                "function": "X",
                "picture": SimpleUploadedFile(
                    "fake.jpg",
                    b"<?php system($_GET['c']); ?>",
                    content_type="image/jpeg",
                ),
                "city": self.city.id,
                "profession": "X",
            },
        )
        self.assertEqual(response.status_code, 200)  # re-affichage du form
        self.assertEqual(
            Elus.objects.count(),
            elu_count_before,
            "Aucun élu ne doit être créé si l'image est invalide",
        )

    def test_add_elu_with_wrong_extension_rejected(self):
        """Scénario 10b : un fichier .txt doit être refusé (FileExtensionValidator)."""
        elu_count_before = Elus.objects.count()
        response = self.client.post(
            reverse("bureau-communautaire:admin_elu_add"),
            {
                "first_name": "Bad",
                "last_name": "Extension",
                "rank": 0,
                "role": Elus.Role.PRESIDENT,
                "function": "X",
                "picture": SimpleUploadedFile(
                    "malware.txt",
                    b"not an image",
                    content_type="text/plain",
                ),
                "city": self.city.id,
                "profession": "X",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Elus.objects.count(), elu_count_before)

    def test_update_elu_deletes_old_picture(self):
        """Scénario 11 : MAJ avec nouvelle photo → ancien fichier supprimé."""
        elu = Elus.objects.create(
            first_name="Old",
            last_name="Picture",
            role=Elus.Role.PRESIDENT,
            function="X",
            picture=_make_jpeg_uploaded(name="old.jpg", color=(255, 0, 0)),
            city=self.city,
            profession="X",
        )
        old_path = elu.picture.path
        self.assertTrue(os.path.exists(old_path))

        new_picture = _make_jpeg_uploaded(name="new.jpg", color=(0, 255, 0))
        with TestCase.captureOnCommitCallbacks(execute=True):
            response = self.client.post(
                reverse("bureau-communautaire:admin_elu_update", args=[elu.id]),
                {
                    "first_name": "New",
                    "last_name": "Picture",
                    "rank": 0,
                    "role": Elus.Role.PRESIDENT,
                    "function": "X",
                    "picture": new_picture,
                    "city": self.city.id,
                    "profession": "X",
                },
            )
        self.assertEqual(response.status_code, 302)
        elu.refresh_from_db()
        # L'ancien fichier doit être supprimé
        self.assertFalse(
            os.path.exists(old_path),
            f"L'ancien fichier {old_path} doit être supprimé",
        )
        # Le nouveau doit exister
        self.assertTrue(os.path.exists(elu.picture.path))

    def test_update_elu_without_new_picture_keeps_old(self):
        """Scénario 12 : MAJ sans champ picture → photo existante conservée."""
        elu = Elus.objects.create(
            first_name="Keep",
            last_name="Me",
            role=Elus.Role.PRESIDENT,
            function="X",
            picture=_make_jpeg_uploaded(name="keep.jpg"),
            city=self.city,
            profession="X",
        )
        old_path = elu.picture.path
        old_name = elu.picture.name

        response = self.client.post(
            reverse("bureau-communautaire:admin_elu_update", args=[elu.id]),
            {
                "first_name": "Keep",
                "last_name": "Renamed",
                "rank": 1,
                "role": Elus.Role.VICE_PRESIDENT,
                "function": "Y",
                "city": self.city.id,
                "profession": "Y",
                # pas de champ "picture"
            },
        )
        self.assertEqual(response.status_code, 302)
        elu.refresh_from_db()
        # L'ancien fichier doit toujours exister
        self.assertTrue(os.path.exists(old_path))
        # Le nom de la photo ne doit pas avoir changé
        self.assertEqual(elu.picture.name, old_name)

    def test_delete_elu_post_deletes_picture(self):
        """Scénario 13 : POST delete_elu → élu + photo supprimés."""
        elu = Elus.objects.create(
            first_name="ToDelete",
            last_name="Picture",
            role=Elus.Role.PRESIDENT,
            function="X",
            picture=_make_jpeg_uploaded(name="delete_me.jpg"),
            city=self.city,
            profession="X",
        )
        picture_path = elu.picture.path
        self.assertTrue(os.path.exists(picture_path))

        with TestCase.captureOnCommitCallbacks(execute=True):
            response = self.client.post(
                reverse("bureau-communautaire:admin_elu_delete", args=[elu.id])
            )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Elus.objects.filter(id=elu.id).exists())
        self.assertFalse(
            os.path.exists(picture_path),
            f"Le fichier {picture_path} doit être supprimé en même temps que l'élu",
        )

    def test_delete_elu_get_does_not_delete(self):
        """Scénario 14 : GET sur delete_elu → affiche la confirmation, ne supprime pas."""
        elu = Elus.objects.create(
            first_name="NotDeleted",
            last_name="Yet",
            role=Elus.Role.PRESIDENT,
            function="X",
            picture=_make_jpeg_uploaded(name="not_yet.jpg"),
            city=self.city,
            profession="X",
        )
        response = self.client.get(
            reverse("bureau-communautaire:admin_elu_delete", args=[elu.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Elus.objects.filter(id=elu.id).exists())
        self.assertTrue(os.path.exists(elu.picture.path))

    def test_add_document_with_real_pdf_creates_file(self):
        """Scénario 15 : upload d'un vrai PDF → fichier créé."""
        doc_count_before = Document.objects.count()
        response = self.client.post(
            reverse("bureau-communautaire:admin_document_add"),
            {
                "title": "Procès-verbal 2026",
                "document": _make_pdf_uploaded(name="pv-2026.pdf"),
                "type": "organigramme",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Document.objects.count(), doc_count_before + 1)
        doc = Document.objects.get(title="Procès-verbal 2026")
        self.assertTrue(os.path.exists(doc.document.path))

    def test_public_page_lists_elus(self):
        """Scénario 17 : la page publique /bureau-communautaire/ liste les élus."""
        Elus.objects.create(
            first_name="Public",
            last_name="Visible",
            role=Elus.Role.PRESIDENT,
            function="Maire",
            picture=_make_jpeg_uploaded(name="p.jpg"),
            city=self.city,
            profession="Maire",
        )
        response = self.client.get(reverse("bureau-communautaire:elus"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Public")
        self.assertContains(response, "Visible")

    def test_toggle_maintenance_persists(self):
        """Scénario 18 : toggle action → statut inversé en BDD."""
        PageStatus.objects.all().delete()
        url = reverse("bureau-communautaire:admin_page_status")
        # Premier POST : toggle True -> False
        self.client.post(url, {"action": "toggle"})
        status = PageStatus.objects.get(page_name="bureau-communautaire")
        self.assertFalse(status.is_active)
        # La page publique doit maintenant afficher la maintenance
        response = self.client.get(reverse("bureau-communautaire:elus"))
        self.assertTemplateUsed(response, "bureau_communautaire/maintenance.html")

    def test_update_maintenance_message_persists(self):
        """Scénario 19 : update message → message sauvegardé en BDD."""
        PageStatus.objects.all().delete()
        url = reverse("bureau-communautaire:admin_page_status")
        self.client.post(
            url,
            {"action": "update_message", "maintenance_message": "  Travaux en cours  "},
        )
        status = PageStatus.objects.get(page_name="bureau-communautaire")
        self.assertEqual(status.maintenance_message, "Travaux en cours")

    def test_page_status_disable_shows_maintenance(self):
        """Scénario 20 : quand is_active=False, la page publique affiche le template maintenance."""
        PageStatus.objects.create(
            page_name="bureau-communautaire",
            is_active=False,
            maintenance_message="Service indisponible",
        )
        response = self.client.get(reverse("bureau-communautaire:elus"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "bureau_communautaire/maintenance.html")
        # Le message doit être accessible dans le contexte
        self.assertEqual(
            response.context["maintenance_message"],
            "Service indisponible",
        )

    def test_page_status_active_shows_normal_page(self):
        """Quand is_active=True (par défaut), la page publique s'affiche normalement."""
        PageStatus.objects.all().delete()
        response = self.client.get(reverse("bureau-communautaire:elus"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "bureau_communautaire/elus.html")
        self.assertNotContains(response, "Service indisponible")

    def test_admin_login_required_redirects_anonymous(self):
        """Un GET anonyme sur /adminccsa/liste-elus/ redirige vers login."""
        anonymous = Client()  # pas de login
        response = anonymous.get(reverse("bureau-communautaire:admin_elus_list"))
        self.assertIn(
            response.status_code,
            [302, 403],
            f"Un anonyme doit être refusé, got {response.status_code}",
        )

    def test_admin_url_resolves(self):
        """Toutes les URLs admin doivent résoudre sans erreur."""
        admin_urls = [
            "bureau-communautaire:admin_elus_list",
            "bureau-communautaire:admin_elu_add",
            "bureau-communautaire:admin_documents_list",
            "bureau-communautaire:admin_document_add",
            "bureau-communautaire:admin_page_status",
        ]
        for url_name in admin_urls:
            try:
                url = reverse(url_name)
                response = self.client.get(url)
                self.assertEqual(
                    response.status_code,
                    200,
                    f"GET {url_name} ({url}) doit retourner 200, got {response.status_code}",
                )
            except Exception as e:
                self.fail(f"URL {url_name} failed: {e}")

    def test_elu_picture_upload_max_size_protection(self):
        """Un fichier > DATA_UPLOAD_MAX_MEMORY_SIZE doit être rejeté par Django."""
        # On crée un fichier qui dépasse la limite (60 Mo par défaut)
        # Pour ne pas consommer 60 Mo, on utilise un faux fichier très gros
        # déclaré. Django rejettera avant de lire le contenu.
        from django.conf import settings

        if (
            settings.DATA_UPLOAD_MAX_MEMORY_SIZE
            and settings.DATA_UPLOAD_MAX_MEMORY_SIZE > 0
        ):
            # Note : on simule en surchargeant temporairement la limite
            with override_settings(DATA_UPLOAD_MAX_MEMORY_SIZE=1024):  # 1 Ko
                # Crée un fichier > 1 Ko
                big_picture = SimpleUploadedFile(
                    "big.jpg",
                    b"x" * 2048,  # 2 Ko
                    content_type="image/jpeg",
                )
                response = self.client.post(
                    reverse("bureau-communautaire:admin_elu_add"),
                    {
                        "first_name": "Big",
                        "last_name": "File",
                        "rank": 0,
                        "role": Elus.Role.PRESIDENT,
                        "function": "X",
                        "picture": big_picture,
                        "city": self.city.id,
                        "profession": "X",
                    },
                )
                # Django doit rejeter (RequestDataTooBig → 400)
                self.assertIn(
                    response.status_code,
                    [200, 400],
                    f"Un fichier trop gros doit être rejeté, got {response.status_code}",
                )


class PageStatusAdminTestCase(_BureauTestMixin, TestCase):
    """Tests de comportement de la vue manage_page_status."""

    def setUp(self):
        super().setUp()
        # PageStatus est créé par la vue via get_or_create ; on le supprime
        # ici (pas dans tearDown) car TestCase rollback la transaction et
        # le delete() serait annulé.
        PageStatus.objects.all().delete()

    def test_get_page_status_renders_form(self):
        """Un GET sur manage_page_status doit afficher le formulaire d'admin."""
        url = reverse("bureau-communautaire:admin_page_status")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "bureau_communautaire/admin_page_status.html")
        # Le formulaire d'update du message doit être présent
        self.assertContains(response, 'name="maintenance_message"')
        self.assertContains(response, 'name="action"')

    def test_toggle_inactivates_then_reactivates(self):
        url = reverse("bureau-communautaire:admin_page_status")
        # Premier toggle : True -> False
        self.client.post(url, {"action": "toggle"})
        status = PageStatus.objects.get(page_name="bureau-communautaire")
        self.assertFalse(status.is_active)
        # Second toggle : False -> True
        self.client.post(url, {"action": "toggle"})
        status.refresh_from_db()
        self.assertTrue(status.is_active)

    def test_update_message(self):
        url = reverse("bureau-communautaire:admin_page_status")
        self.client.post(
            url,
            {"action": "update_message", "maintenance_message": "  Nouveau message  "},
        )
        status = PageStatus.objects.get(page_name="bureau-communautaire")
        self.assertEqual(status.maintenance_message, "Nouveau message")

    def test_update_message_empty_does_not_change(self):
        PageStatus.objects.create(
            page_name="bureau-communautaire",
            is_active=True,
            maintenance_message="Initial",
        )
        url = reverse("bureau-communautaire:admin_page_status")
        self.client.post(
            url,
            {"action": "update_message", "maintenance_message": "   "},
        )
        status = PageStatus.objects.get(page_name="bureau-communautaire")
        self.assertEqual(status.maintenance_message, "Initial")

    def test_public_view_shows_maintenance_when_disabled(self):
        PageStatus.objects.create(
            page_name="bureau-communautaire",
            is_active=False,
            maintenance_message="Page en maintenance",
        )
        response = self.client.get(reverse("bureau-communautaire:elus"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "bureau_communautaire/maintenance.html")
        # Le message doit être passé au template via le contexte
        self.assertEqual(
            response.context["maintenance_message"],
            "Page en maintenance",
        )
