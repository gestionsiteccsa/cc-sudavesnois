from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from competences.models import Competence

User = get_user_model()

MEDIA_ROOT = "test_competences_media"  # Répertoire temporaire pour les fichiers médias


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class CompetenceViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Créer un superutilisateur personnalisé
        cls.superuser = User.objects.create_superuser(
            email="admin@example.com",  # Utiliser l'email comme nom d'utilisateur
            password="password123",
        )

    def setUp(self):
        # print("Connexion avec le compte super_user\n")
        self.client = Client()
        self.client.login(
            email="admin@example.com", password="password123"
        )  # Se connecter avec l'email

    # Test de la vue de la liste public des compétences
    def test_competence_list_view_without_data(self):
        """
        Test de la vue de la liste public des compétences
        """
        response = self.client.get(reverse("competences:competences"))
        # Vérifier que la réponse est 200 OK
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "competences/competences.html")

        # Vérifier qu'aucune compétence n'est affichée
        self.assertContains(response, "Aucune compétence facultative n'est disponible.")
        self.assertContains(response, "Aucune compétence obligatoire n'est disponible.")
        self.assertContains(response, "Aucune compétence optionnelle n'est disponible.")

    # Test de la vue de la liste admin des compétences
    def test_competence_list_view_admin_without_data(self):
        """
        Test de la vue de la liste admin des compétences
        """
        # print("Test de la vue de la liste admin des compétences\n")
        response = self.client.get(reverse("competences:admin_competences_list"))
        # Vérifier que la réponse est 200 OK
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "competences/admin_competences_list.html")

        # Vérifier qu'aucune compétence n'est affichée
        self.assertContains(response, "Aucune compétence trouvée.")

    # Test de la vue de la liste public des compétences avec des données
    def test_competence_list_view_with_data(self):
        """
        Test de la vue de la liste public des compétences avec des données
        """
        # Créer une compétence pour le test
        competence_ob = Competence.objects.create(
            title="Test Compétence Obligatoire",
            icon='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2L2 7h20L12 2zM2 17l10 5 10-5V7H2v10z"/></svg>',
            description="Ceci est une compétence obligatoire de test.",
            category=Competence.Category.OBLIGATOIRE,
            is_big=False,
        )

        competence_f = Competence.objects.create(
            title="Test Compétence Facultative",
            icon='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2L2 7h20L12 2zM2 17l10 5 10-5V7H2v10z"/></svg>',
            description="Ceci est une compétence facultative de test.",
            category=Competence.Category.FACULTATIVE,
            is_big=False,
        )

        competence_op = Competence.objects.create(
            title="Test Compétence Optionnelle",
            icon='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2L2 7h20L12 2zM2 17l10 5 10-5V7H2v10z"/></svg>',
            description="Ceci est une compétence optionnelle de test.",
            category=Competence.Category.OPTIONNELLE,
            is_big=False,
        )

        response = self.client.get(reverse("competences:competences"))
        # Vérifier que la réponse est 200 OK
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "competences/competences.html")

        # Vérifier que les compétences sont affichées
        self.assertContains(response, competence_ob.title)
        self.assertContains(response, competence_f.title)
        self.assertContains(response, competence_op.title)
        self.assertContains(response, competence_ob.description)
        self.assertContains(response, competence_f.description)
        self.assertContains(response, competence_op.description)
        self.assertContains(response, competence_ob.icon)
        self.assertContains(response, competence_f.icon)
        self.assertContains(response, competence_op.icon)

    # Test de la vue de la liste admin des compétences avec des données
    def test_competence_list_view_admin_with_data(self):
        """
        Test de la vue de la liste admin des compétences avec des données
        """
        # Créer une compétence pour le test
        competence_ob = Competence.objects.create(
            title="Test Compétence Obligatoire",
            icon='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2L2 7h20L12 2zM2 17l10 5 10-5V7H2v10z"/></svg>',
            description="Ceci est une compétence obligatoire de test.",
            category=Competence.Category.OBLIGATOIRE,
            is_big=False,
        )

        competence_f = Competence.objects.create(
            title="Test Compétence Facultative",
            icon='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2L2 7h20L12 2zM2 17l10 5 10-5V7H2v10z"/></svg>',
            description="Ceci est une compétence facultative de test.",
            category=Competence.Category.FACULTATIVE,
            is_big=False,
        )

        competence_op = Competence.objects.create(
            title="Test Compétence Optionnelle",
            icon='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2L2 7h20L12 2zM2 17l10 5 10-5V7H2v10z"/></svg>',
            description="Ceci est une compétence optionnelle de test.",
            category=Competence.Category.OPTIONNELLE,
            is_big=False,
        )

        response = self.client.get(reverse("competences:admin_competences_list"))
        # Vérifier que la réponse est 200 OK
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "competences/admin_competences_list.html")

        # Vérifier que les compétences sont affichées
        self.assertContains(response, competence_ob.title)
        self.assertContains(response, competence_f.title)
        self.assertContains(response, competence_op.title)
        self.assertContains(response, competence_ob.description)
        self.assertContains(response, competence_f.description)
        self.assertContains(response, competence_op.description)
        self.assertContains(response, competence_ob.icon)
        self.assertContains(response, competence_f.icon)
        self.assertContains(response, competence_op.icon)

    # Test de la vue d'ajout de compétence
    def test_add_competence_view(self):
        """
        Test de la vue d'ajout de compétence
        """
        response = self.client.get(reverse("competences:add_competence"))
        # Vérifier que la réponse est 200 OK
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "competences/admin_competence_add.html")
        # Vérifier que le bouton "Publier" est présent
        self.assertContains(response, "Publier")

    def test_add_competence_view_post_valid_data(self):
        """
        Test de la vue d'ajout de compétence avec des données valides
        """
        response = self.client.post(
            reverse("competences:add_competence"),
            {
                "title": "Test Compétence",
                "icon": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2L2 7h20L12 2zM2 17l10 5 10-5V7H2v10z"/></svg>',
                "description": "Ceci est une compétence de test.",
                "category": Competence.Category.OBLIGATOIRE,
                "is_big": False,
            },
        )
        # Vérifier que la réponse est une redirection
        self.assertEqual(response.status_code, 302)
        # Vérifier que la compétence a été créée
        competence = Competence.objects.get(title="Test Compétence")
        self.assertEqual(competence.title, "Test Compétence")
        self.assertEqual(
            competence.icon,
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2L2 7h20L12 2zM2 17l10 5 10-5V7H2v10z"/></svg>',
        )
        self.assertEqual(competence.description, "Ceci est une compétence de test.")
        self.assertEqual(competence.category, Competence.Category.OBLIGATOIRE)
        self.assertEqual(competence.is_big, False)

    def test_add_competence_view_post_invalid_data(self):
        """
        Test de la vue d'ajout de compétence avec des données invalides
        """
        response = self.client.post(
            reverse("competences:add_competence"),
            {
                "title": "",
                "icon": "",
                "description": "",
                "category": "",
                "is_big": False,
            },
        )
        # Vérifier que la réponse est 200 OK
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "competences/admin_competence_add.html")
        self.assertEqual(
            Competence.objects.count(), 0
        )  # Vérifier qu'aucune compétence n'a été créée

    # Test de la vue de modification de compétence
    def test_edit_competence_view(self):
        """
        Test de la vue de modification de compétence
        """
        # Créer une compétence pour le test
        competence = Competence.objects.create(
            title="Test Compétence",
            icon='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2L2 7h20L12 2zM2 17l10 5 10-5V7H2v10z"/></svg>',
            description="Ceci est une compétence de test.",
            category=Competence.Category.OBLIGATOIRE,
            is_big=False,
        )

        response = self.client.get(
            reverse("competences:edit_competence", args=[competence.id])
        )
        # Vérifier que la réponse est 200 OK
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "competences/admin_competence_edit.html")
        # Vérifier que le bouton est présent
        self.assertContains(response, "Appliquer")
        # Vérifier que le formulaire contient les données de la compétence
        self.assertContains(response, competence.title)
        self.assertContains(response, competence.description)

    def test_edit_competence_view_post_valid_data(self):
        """
        Test de la vue de modification de compétence avec des données valides
        """
        # Créer une compétence pour le test
        competence = Competence.objects.create(
            title="Test Compétence",
            icon='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2L2 7h20L12 2zM2 17l10 5 10-5V7H2v10z"/></svg>',
            description="Ceci est une compétence de test.",
            category=Competence.Category.OBLIGATOIRE,
            is_big=False,
        )

        response = self.client.post(
            reverse("competences:edit_competence", args=[competence.id]),
            {
                "title": "Test Compétence Modifiée",
                "icon": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2L2 7h20L12 2zM2 17l10 5 10-5V7H2v10z"/></svg>',
                "description": "Ceci est une compétence modifiée de test.",
                "category": Competence.Category.FACULTATIVE,
                "is_big": True,
            },
        )
        # Vérifier que la réponse est une redirection
        self.assertEqual(response.status_code, 302)
        # Vérifier que la compétence a été modifiée
        competence.refresh_from_db()
        self.assertEqual(competence.title, "Test Compétence Modifiée")
        self.assertEqual(
            competence.icon,
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2L2 7h20L12 2zM2 17l10 5 10-5V7H2v10z"/></svg>',
        )
        self.assertEqual(
            competence.description, "Ceci est une compétence modifiée de test."
        )
        self.assertEqual(competence.category, Competence.Category.FACULTATIVE)
        self.assertEqual(competence.is_big, True)

    def test_edit_competence_view_post_invalid_data(self):
        """
        Test de la vue de modification de compétence avec des données invalides
        """
        # Créer une compétence pour le test
        competence = Competence.objects.create(
            title="Test Compétence",
            icon='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2L2 7h20L12 2zM2 17l10 5 10-5V7H2v10z"/></svg>',
            description="Ceci est une compétence de test.",
            category=Competence.Category.OBLIGATOIRE,
            is_big=False,
        )

        response = self.client.post(
            reverse("competences:edit_competence", args=[competence.id]),
            {
                "title": "",
                "icon": "",
                "description": "",
                "category": "",
                "is_big": False,
            },
        )
        # Vérifier que la réponse est 200 OK
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "competences/admin_competence_edit.html")
        self.assertEqual(competence.title, "Test Compétence")
        self.assertEqual(
            competence.icon,
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2L2 7h20L12 2zM2 17l10 5 10-5V7H2v10z"/></svg>',
        )
        self.assertEqual(competence.description, "Ceci est une compétence de test.")
        self.assertEqual(competence.category, Competence.Category.OBLIGATOIRE)

    # Test de la vue de suppression de compétence
    def test_delete_competence_view(self):
        """
        Test de la vue de suppression de compétence
        """
        # Créer une compétence pour le test
        competence = Competence.objects.create(
            title="Test Compétence",
            icon='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2L2 7h20L12 2zM2 17l10 5 10-5V7H2v10z"/></svg>',
            description="Ceci est une compétence de test.",
            category=Competence.Category.OBLIGATOIRE,
            is_big=False,
        )

        response = self.client.get(
            reverse("competences:delete_competence", args=[competence.id])
        )
        # Vérifier que la réponse est 200 OK
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "competences/admin_competence_delete.html")
        # Vérifier que le bouton est présent
        self.assertContains(response, "Supprimer")

    def test_delete_competence_view_post(self):
        """
        Test de la vue de suppression de compétence
        """
        # Créer une compétence pour le test
        competence = Competence.objects.create(
            title="Test Compétence",
            icon='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2L2 7h20L12 2zM2 17l10 5 10-5V7H2v10z"/></svg>',
            description="Ceci est une compétence de test.",
            category=Competence.Category.OBLIGATOIRE,
            is_big=False,
        )

        response = self.client.post(
            reverse("competences:delete_competence", args=[competence.id])
        )
        # Vérifier que la réponse est une redirection
        self.assertEqual(response.status_code, 302)
        # Vérifier que la compétence a été supprimée
        self.assertFalse(Competence.objects.filter(id=competence.id).exists())


# ============================================================================
# NOUVEAUX TESTS AJOUTÉS POUR AMÉLIORER LA COUVERTURE
# ============================================================================

from unittest.mock import MagicMock, patch

from django.contrib.admin.sites import site
from django.contrib.auth.models import Permission
from django.core.exceptions import ValidationError

from competences.admin import CustomCompetenceAdmin
from competences.forms import CompetenceForm


class BaseCompetencesTestCase(TestCase):
    """Classe de base pour tous les tests avec configuration commune."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.superuser = User.objects.create_superuser(
            email="admin@exemple.com", password="adminpassword"
        )

        # Créer un utilisateur staff avec permissions
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

        # Ajouter les permissions nécessaires
        permissions = [
            "add_competence",
            "change_competence",
            "delete_competence",
            "view_competence",
        ]
        for perm_name in permissions:
            try:
                permission = Permission.objects.get(codename=perm_name)
                cls.staff_user_with_perms.user_permissions.add(permission)
            except Permission.DoesNotExist:
                pass


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class CompetenceModelTestCase(BaseCompetencesTestCase):
    """Tests pour le modèle Competence."""

    def test_competence_creation(self):
        """Test de création d'une compétence."""
        competence = Competence.objects.create(
            title="Développement économique",
            icon="<svg>test</svg>",
            description="Description test",
            category=Competence.Category.OBLIGATOIRE,
            is_big=False,
        )

        self.assertEqual(competence.title, "Développement économique")
        self.assertEqual(competence.category, Competence.Category.OBLIGATOIRE)
        self.assertFalse(competence.is_big)
        self.assertEqual(Competence.objects.count(), 1)

    def test_competence_str_method(self):
        """Test de la méthode __str__ du modèle."""
        competence = Competence.objects.create(
            title="Test Compétence",
            icon="<svg>icon</svg>",
            description="Description de test",
            category=Competence.Category.FACULTATIVE,
            is_big=True,
        )

        expected_str = "Test Compétence (FACULTATIVE) - Description de test) - True"
        self.assertEqual(str(competence), expected_str)

    def test_competence_categories(self):
        """Test des différentes catégories de compétences."""
        # Test OBLIGATOIRE
        comp_obligatoire = Competence.objects.create(
            title="Compétence obligatoire",
            icon="<svg>ob</svg>",
            description="Description obligatoire",
            category=Competence.Category.OBLIGATOIRE,
            is_big=False,
        )

        # Test OPTIONNELLE
        comp_optionnelle = Competence.objects.create(
            title="Compétence optionnelle",
            icon="<svg>op</svg>",
            description="Description optionnelle",
            category=Competence.Category.OPTIONNELLE,
            is_big=False,
        )

        # Test FACULTATIVE (par défaut)
        comp_facultative = Competence.objects.create(
            title="Compétence facultative",
            icon="<svg>fa</svg>",
            description="Description facultative",
        )

        self.assertEqual(comp_obligatoire.category, Competence.Category.OBLIGATOIRE)
        self.assertEqual(comp_optionnelle.category, Competence.Category.OPTIONNELLE)
        self.assertEqual(comp_facultative.category, Competence.Category.FACULTATIVE)

    def test_competence_is_big_field(self):
        """Test du champ is_big."""
        # Test avec is_big=True
        comp_big = Competence.objects.create(
            title="Grande compétence",
            icon="<svg>big</svg>",
            description="Description grande",
            category=Competence.Category.FACULTATIVE,
            is_big=True,
        )

        # Test avec is_big=False (par défaut)
        comp_normal = Competence.objects.create(
            title="Compétence normale",
            icon="<svg>normal</svg>",
            description="Description normale",
            category=Competence.Category.OBLIGATOIRE,
        )

        self.assertTrue(comp_big.is_big)
        self.assertFalse(comp_normal.is_big)

    def test_competence_required_fields(self):
        """Test des champs obligatoires."""
        # Test sans titre
        with self.assertRaises(ValidationError):
            competence = Competence(
                icon="<svg>test</svg>",
                description="Description test",
                category=Competence.Category.OBLIGATOIRE,
            )
            competence.full_clean()

        # Test sans description
        with self.assertRaises(ValidationError):
            competence = Competence(
                title="Test",
                icon="<svg>test</svg>",
                category=Competence.Category.OBLIGATOIRE,
            )
            competence.full_clean()

    def test_competence_verbose_names(self):
        """Test des verbose names du modèle."""
        meta = Competence._meta
        self.assertEqual(meta.verbose_name, "Compétence")
        self.assertEqual(meta.verbose_name_plural, "Compétences")


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class CompetenceFormTestCase(BaseCompetencesTestCase):
    """Tests pour le formulaire CompetenceForm."""

    def test_form_valid_data(self):
        """Test du formulaire avec des données valides."""
        form_data = {
            "title": "Compétence test",
            "icon": "<svg>icon</svg>",
            "description": "Description de test",
            "category": Competence.Category.OBLIGATOIRE,
            "is_big": False,
        }
        form = CompetenceForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_missing_required_fields(self):
        """Test du formulaire avec des champs obligatoires manquants."""
        # Test sans titre
        form_data = {
            "icon": "<svg>icon</svg>",
            "description": "Description de test",
            "category": Competence.Category.OBLIGATOIRE,
            "is_big": False,
        }
        form = CompetenceForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)

    def test_form_optional_description(self):
        """Test que la description est optionnelle dans le formulaire."""
        form_data = {
            "title": "Compétence test",
            "icon": "<svg>icon</svg>",
            "description": "",  # Description vide
            "category": Competence.Category.OBLIGATOIRE,
            "is_big": False,
        }
        form = CompetenceForm(data=form_data)
        # Le formulaire devrait être valide même avec description vide
        # car required=False est défini dans le formulaire
        self.assertTrue(form.is_valid())

    def test_form_widgets(self):
        """Test des widgets du formulaire."""
        form = CompetenceForm()

        # Vérifier les widgets personnalisés
        self.assertIn("placeholder", form.fields["title"].widget.attrs)
        self.assertIn("placeholder", form.fields["icon"].widget.attrs)
        self.assertEqual(
            form.fields["category"].widget.attrs.get("class"), "form-select"
        )
        self.assertEqual(
            form.fields["is_big"].widget.attrs.get("class"), "form-check-input"
        )

    def test_form_labels(self):
        """Test des labels du formulaire."""
        form = CompetenceForm()

        expected_labels = {
            "title": "Titre de la compétence",
            "icon": "Icone correspondante",
            "description": "Description",
            "category": "Catégorie de la compétence",
            "is_big": "Necéssite plus grand format ? (Facultative uniquement)",
        }

        for field_name, expected_label in expected_labels.items():
            self.assertEqual(form.fields[field_name].label, expected_label)

    def test_form_help_text(self):
        """Test du texte d'aide du formulaire."""
        form = CompetenceForm()
        self.assertEqual(
            form.fields["description"].help_text, "Description de la compétence"
        )

    def test_form_save(self):
        """Test de la sauvegarde du formulaire."""
        form_data = {
            "title": "Compétence sauvegardée",
            "icon": "<svg>save</svg>",
            "description": "Description sauvegardée",
            "category": Competence.Category.OPTIONNELLE,
            "is_big": True,
        }

        form = CompetenceForm(data=form_data)
        self.assertTrue(form.is_valid())

        competence = form.save()
        self.assertEqual(competence.title, "Compétence sauvegardée")
        self.assertEqual(competence.category, Competence.Category.OPTIONNELLE)
        self.assertTrue(competence.is_big)


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class CompetencePermissionsTestCase(BaseCompetencesTestCase):
    """Tests pour les permissions de l'application competences."""

    def setUp(self):
        """Configuration de l'environnement de test."""
        self.client = Client()

    def test_superuser_access(self):
        """Test qu'un superutilisateur peut accéder à toutes les vues."""
        self.client.login(email=self.superuser.email, password="adminpassword")

        urls = [
            reverse("competences:admin_competences_list"),
            reverse("competences:add_competence"),
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
            reverse("competences:admin_competences_list"),
            reverse("competences:add_competence"),
        ]

        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

    def test_staff_user_without_permissions(self):
        """Test qu'un utilisateur staff sans permissions ne peut pas accéder."""
        self.client.login(
            email=self.staff_user_no_perms.email, password="staffpassword"
        )

        response = self.client.get(reverse("competences:add_competence"))
        # Django redirige vers la page de login au lieu de retourner 403
        self.assertEqual(response.status_code, 302)

    def test_regular_user_no_access(self):
        """Test qu'un utilisateur normal ne peut pas accéder."""
        self.client.login(email=self.regular_user.email, password="userpassword")

        response = self.client.get(reverse("competences:add_competence"))
        # Django redirige vers la page de login au lieu de retourner 403
        self.assertEqual(response.status_code, 302)

    def test_anonymous_user_redirect(self):
        """Test qu'un utilisateur anonyme est redirigé."""
        response = self.client.get(reverse("competences:add_competence"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_public_view_accessible_to_all(self):
        """Test que la vue publique est accessible à tous."""
        # Test utilisateur anonyme
        response = self.client.get(reverse("competences:competences"))
        self.assertEqual(response.status_code, 200)

        # Test utilisateur connecté
        self.client.login(email=self.regular_user.email, password="userpassword")
        response = self.client.get(reverse("competences:competences"))
        self.assertEqual(response.status_code, 200)


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class CompetenceAdminTestCase(BaseCompetencesTestCase):
    """Tests pour l'interface d'administration de Competence."""

    def setUp(self):
        """Configuration de l'environnement de test."""
        self.client = Client()
        self.client.login(email=self.superuser.email, password="adminpassword")

    def test_admin_model_registered(self):
        """Test que le modèle est enregistré dans l'admin."""
        self.assertIn(Competence, site._registry)
        admin_class = site._registry[Competence]
        self.assertIsInstance(admin_class, CustomCompetenceAdmin)

    def test_admin_list_display(self):
        """Test de la configuration list_display."""
        admin_class = site._registry[Competence]
        expected_fields = ("title", "description", "is_big", "category")
        self.assertEqual(admin_class.list_display, expected_fields)

    def test_admin_list_filter(self):
        """Test de la configuration list_filter."""
        admin_class = site._registry[Competence]
        expected_filters = ("title", "description", "category")
        self.assertEqual(admin_class.list_filter, expected_filters)

    def test_admin_search_fields(self):
        """Test de la configuration search_fields."""
        admin_class = site._registry[Competence]
        expected_fields = ("title", "description")
        self.assertEqual(admin_class.search_fields, expected_fields)

    def test_admin_ordering(self):
        """Test de la configuration ordering."""
        admin_class = site._registry[Competence]
        expected_ordering = ("title",)
        self.assertEqual(admin_class.ordering, expected_ordering)

    def test_admin_form_class(self):
        """Test que le formulaire personnalisé est utilisé."""
        admin_class = site._registry[Competence]
        self.assertEqual(admin_class.form, CompetenceForm)


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class CompetenceIntegrationTestCase(BaseCompetencesTestCase):
    """Tests d'intégration pour l'application competences."""

    def setUp(self):
        """Configuration de l'environnement de test."""
        self.client = Client()
        self.client.login(email=self.superuser.email, password="adminpassword")

    def test_complete_competence_workflow(self):
        """Test du workflow complet : création → modification → suppression."""
        # 1. Créer une compétence
        response = self.client.post(
            reverse("competences:add_competence"),
            {
                "title": "Compétence workflow",
                "icon": "<svg>workflow</svg>",
                "description": "Description workflow",
                "category": Competence.Category.OBLIGATOIRE,
                "is_big": False,
            },
        )

        self.assertEqual(response.status_code, 302)
        competence = Competence.objects.get(title="Compétence workflow")

        # 2. Vérifier dans la liste d'administration
        response = self.client.get(reverse("competences:admin_competences_list"))
        self.assertContains(response, "Compétence workflow")

        # 3. Modifier la compétence
        response = self.client.post(
            reverse("competences:edit_competence", args=[competence.id]),
            {
                "title": "Compétence workflow modifiée",
                "icon": "<svg>modified</svg>",
                "description": "Description modifiée",
                "category": Competence.Category.FACULTATIVE,
                "is_big": True,
            },
        )

        self.assertEqual(response.status_code, 302)

        # Recharger la compétence depuis la base de données
        competence.refresh_from_db()
        self.assertEqual(competence.title, "Compétence workflow modifiée")

        # 4. Vérifier que la modification a bien été appliquée
        self.assertEqual(competence.category, Competence.Category.FACULTATIVE)
        self.assertTrue(competence.is_big)

        # 5. Supprimer la compétence
        response = self.client.post(
            reverse("competences:delete_competence", args=[competence.id])
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Competence.objects.count(), 0)

    def test_public_view_with_all_categories(self):
        """Test de la vue publique avec toutes les catégories."""
        # Créer des compétences de chaque catégorie
        Competence.objects.create(
            title="1. Compétence obligatoire",
            icon="<svg>ob</svg>",
            description="Description obligatoire",
            category=Competence.Category.OBLIGATOIRE,
            is_big=False,
        )

        Competence.objects.create(
            title="1. Compétence optionnelle",
            icon="<svg>op</svg>",
            description="Description optionnelle",
            category=Competence.Category.OPTIONNELLE,
            is_big=False,
        )

        Competence.objects.create(
            title="Actions et subventions communautaires",
            icon="<svg>fa</svg>",
            description="Description facultative",
            category=Competence.Category.FACULTATIVE,
            is_big=True,
        )

        response = self.client.get(reverse("competences:competences"))
        self.assertEqual(response.status_code, 200)

        # Vérifier que toutes les catégories sont présentes
        self.assertIsNotNone(response.context["c_obligatoires"])
        self.assertIsNotNone(response.context["c_optionnelles"])
        self.assertIsNotNone(response.context["c_facultatives"])

        # Vérifier le contenu
        self.assertContains(response, "1. Compétence obligatoire")
        self.assertContains(response, "1. Compétence optionnelle")
        self.assertContains(response, "Actions et subventions communautaires")


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class CompetenceEdgeCasesTestCase(BaseCompetencesTestCase):
    """Tests pour les cas limites et erreurs."""

    def setUp(self):
        """Configuration de l'environnement de test."""
        self.client = Client()
        self.client.login(email=self.superuser.email, password="adminpassword")

    def test_competence_with_very_long_title(self):
        """Test avec un titre très long."""
        long_title = "A" * 255  # Titre de 255 caractères (limite du modèle)

        competence = Competence.objects.create(
            title=long_title,
            icon="<svg>long</svg>",
            description="Description normale",
            category=Competence.Category.OBLIGATOIRE,
            is_big=False,
        )

        self.assertEqual(competence.title, long_title)

    def test_competence_with_very_long_icon(self):
        """Test avec une icône très longue."""
        long_icon = "<svg>" + "x" * 990 + "</svg>"  # Icône de 1000 caractères

        competence = Competence.objects.create(
            title="Titre normal",
            icon=long_icon,
            description="Description normale",
            category=Competence.Category.FACULTATIVE,
            is_big=False,
        )

        self.assertEqual(competence.icon, long_icon)

    def test_competence_with_very_long_description(self):
        """Test avec une description très longue."""
        long_description = "B" * 5000  # Description très longue

        competence = Competence.objects.create(
            title="Titre normal",
            icon="<svg>normal</svg>",
            description=long_description,
            category=Competence.Category.OPTIONNELLE,
            is_big=True,
        )

        self.assertEqual(competence.description, long_description)

    def test_competence_with_special_characters(self):
        """Test avec des caractères spéciaux."""
        special_title = "Compétence n°123 - Développement économique (éàùç)"
        special_description = "Description avec caractères spéciaux : éèàùç - «»"
        special_icon = (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">éàù</svg>'
        )

        competence = Competence.objects.create(
            title=special_title,
            icon=special_icon,
            description=special_description,
            category=Competence.Category.OBLIGATOIRE,
            is_big=False,
        )

        self.assertEqual(competence.title, special_title)
        self.assertEqual(competence.description, special_description)
        self.assertEqual(competence.icon, special_icon)

    def test_view_with_nonexistent_competence(self):
        """Test d'accès à une compétence inexistante."""
        response = self.client.get(reverse("competences:edit_competence", args=[999]))
        self.assertEqual(response.status_code, 404)

        response = self.client.get(reverse("competences:delete_competence", args=[999]))
        self.assertEqual(response.status_code, 404)

    def test_form_with_empty_category(self):
        """Test du formulaire avec catégorie vide."""
        form_data = {
            "title": "Test compétence",
            "icon": "<svg>test</svg>",
            "description": "Description test",
            "category": "",  # Catégorie vide
            "is_big": False,
        }

        form = CompetenceForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("category", form.errors)

    def test_competence_categories_display_logic(self):
        """Test de la logique d'affichage des catégories."""
        # Test avec seulement une catégorie
        Competence.objects.create(
            title="1. Seule compétence",
            icon="<svg>seule</svg>",
            description="Description seule",
            category=Competence.Category.OBLIGATOIRE,
            is_big=False,
        )

        response = self.client.get(reverse("competences:competences"))

        # Vérifier qu'une seule catégorie est remplie
        self.assertIsNotNone(response.context["c_obligatoires"])
        self.assertIsNone(response.context["c_optionnelles"])
        self.assertIsNone(response.context["c_facultatives"])
