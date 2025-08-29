import os
import shutil

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from .models import Commission, Document, Mandat

User = get_user_model()
from django.core.files.uploadedfile import SimpleUploadedFile

MEDIA_ROOT = "test_commission_media"


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class CommissionTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Créer un superutilisateur personnalisé
        cls.superuser = User.objects.create_superuser(
            email="admin@example.com",  # Utiliser l'email comme nom d'utilisateur
            password="password123",
        )

    def setUp(self):
        self.client = Client()
        self.client.login(
            email="admin@example.com", password="password123"
        )  # Se connecter avec l'email

    def tearDown(self):
        # Nettoyer les fichiers uploadés après chaque test
        Commission.objects.all().delete()
        Document.objects.all().delete()
        Mandat.objects.all().delete()
        if os.path.exists(MEDIA_ROOT):
            shutil.rmtree(MEDIA_ROOT)

    def create_commission(self, title, icon):
        return Commission.objects.create(title=title, icon=icon)

    def create_document(self, file_name):
        return Document.objects.create(
            file=SimpleUploadedFile(
                name=file_name, content=b"Test content", content_type="application/pdf"
            )
        )

    def set_mandat(self, start_year, end_year):
        return Mandat.objects.create(start_year=start_year, end_year=end_year)

    # Test d'affichage de la page publique
    def test_public_views_get(self):
        """
        Test d'affichage de la page publique sans données
        """
        response = self.client.get(reverse("commissions:commissions"))
        # Vérifier que la réponse est un succès (code 200)
        self.assertEqual(response.status_code, 200)
        # Vérifier que le bon template est utilisé
        self.assertTemplateUsed(response, "commissions/commissions.html")
        # Vérifier que le bouton n'est pas présent
        self.assertNotContains(response, "Tableau des Commissions")

    # Test d'affichage de la page publique avec les données
    def test_public_views_get_with_data(self):
        """
        Test d'affichage de la page publique avec des données
        """
        commission = self.create_commission(title="Test Commission", icon="icon.png")
        self.create_document(file_name="test.pdf")
        self.set_mandat(start_year=2023, end_year=2024)
        response = self.client.get(reverse("commissions:commissions"))
        # Vérifier que la réponse est un succès (code 200)
        self.assertEqual(response.status_code, 200)
        # Vérifier que le bon template est utilisé
        self.assertTemplateUsed(response, "commissions/commissions.html")
        # Vérifier que les données sont présentes dans le contexte
        self.assertContains(response, commission.title)
        # Vérifier que le document est présent dans le contexte (bouton de téléchargement)
        self.assertContains(response, "Tableau des Commissions")
        # Vérifier que le mandat est présent dans le contexte
        self.assertContains(response, "2023-2024")
        # Vérifier que le compteur de commission est fonctionnel
        self.assertContains(response, "compte 1 commission")

    # Test d'affichage de la page d'administration
    def test_admin_views_get(self):
        """
        Test d'affichage de la page d'administration sans données
        """
        response = self.client.get(reverse("commissions:admin_list_commissions"))
        # Vérifier que la réponse est un succès (code 200)
        self.assertEqual(response.status_code, 200)
        # Vérifier que le bon template est utilisé
        self.assertTemplateUsed(response, "commissions/admin_commissions_list.html")
        # Vérifier que le bouton d'ajout de commission est présent
        self.assertContains(response, "Ajouter une commission")
        # Vérifier que le bouton d'ajout de document est présent
        self.assertContains(response, "Ajouter un document")
        # Vérifier que le bouton de modification de mandat est présent
        self.assertContains(response, "Modifier les dates du mandat")
        # Vérifier que le message d'info est présent
        self.assertContains(response, "Aucune commission trouvée.")

    # Test d'affichage de la page d'administration avec des données
    def test_admin_views_get_with_data(self):
        """
        Test d'affichage de la page d'administration avec des données
        """
        commission = self.create_commission(title="Test Commission", icon="icon.png")
        self.create_document(file_name="test.pdf")
        self.set_mandat(start_year=2023, end_year=2024)
        response = self.client.get(reverse("commissions:admin_list_commissions"))
        # Vérifier que la réponse est un succès (code 200)
        self.assertEqual(response.status_code, 200)
        # Vérifier que le bon template est utilisé
        self.assertTemplateUsed(response, "commissions/admin_commissions_list.html")
        # Vérifier que le bouton d'ajout de commission est présent
        self.assertContains(response, "Ajouter une commission")
        # Vérifier que le bouton d'ajout de document n'est plus présent
        self.assertNotContains(response, "Ajouter un document")
        # Vérifier que le bouton de modification du document est présent
        self.assertContains(response, "Modifier le document")
        # Vérifier que le bouton de suppression du document est présent
        self.assertContains(response, "Supprimer le doc")
        # Vérifier que le bouton de modification de mandat est présent
        self.assertContains(response, "Modifier les dates du mandat")
        # Vérifier que le message d'info n'est pas présent
        self.assertNotContains(response, "Aucune commission trouvée.")

        # Vérifier que la commission est présente dans le contexte
        self.assertContains(response, commission.title)

    # Test d'affichage de la page d'ajout de commission
    def test_admin_views_add_commission_get(self):
        """
        Test d'affichage de la page d'ajout de commission
        """
        response = self.client.get(reverse("commissions:admin_add_commission"))
        # Vérifier que la réponse est un succès (code 200)
        self.assertEqual(response.status_code, 200)
        # Vérifier que le bon template est utilisé
        self.assertTemplateUsed(response, "commissions/admin_commission_add.html")
        # Vérifier que le formulaire est présent
        self.assertContains(response, "Ajouter une commission")
        self.assertContains(response, "Titre de la commission")
        self.assertContains(response, "Icone correspondante")

    # Test de la page d'ajout de commission avec des données valides
    def test_admin_views_add_commission_post(self):
        """
        Test de la page d'ajout de commission avec des données valides
        """
        response = self.client.post(
            reverse("commissions:admin_add_commission"),
            {"title": "Test Commission", "icon": "icon.png"},
        )
        # Vérifier que la réponse est une redirection (code 302)
        self.assertEqual(response.status_code, 302)
        # Vérifier que la redirection est correcte
        self.assertRedirects(response, reverse("commissions:admin_list_commissions"))
        # Vérifier que la commission a été créée
        self.assertTrue(Commission.objects.filter(title="Test Commission").exists())
        # Vérifier que la commission est affichée dans la liste
        response = self.client.get(reverse("commissions:admin_list_commissions"))
        self.assertContains(response, "Test Commission")

    # Test de la page d'ajout de commission avec des données invalides
    def test_admin_views_add_commission_post_invalid(self):
        """
        Test de la page d'ajout de commission avec des données invalides
        """
        response = self.client.post(
            reverse("commissions:admin_add_commission"), {"title": "", "icon": ""}
        )
        # Vérifier que la réponse est un succès (code 200)
        self.assertEqual(response.status_code, 200)
        # Vérifier que le bon template est utilisé
        self.assertTemplateUsed(response, "commissions/admin_commission_add.html")
        # Vérifier que la commission n'a pas été créée
        self.assertFalse(Commission.objects.filter(title="").exists())

    # Test de la page de modification de commission
    def test_admin_views_edit_commission_get(self):
        """
        Test d'affichage de la page de modification de commission
        """
        commission = self.create_commission(title="Test Commission", icon="icon.png")
        response = self.client.get(
            reverse("commissions:admin_edit_commission", args=[commission.id])
        )
        # Vérifier que la réponse est un succès (code 200)
        self.assertEqual(response.status_code, 200)
        # Vérifier que le bon template est utilisé
        self.assertTemplateUsed(response, "commissions/admin_commission_edit.html")
        # Vérifier que le formulaire est présent
        self.assertContains(response, "Modifier la commission")
        self.assertContains(response, "Titre de la commission")
        self.assertContains(response, "Icone correspondante")
        self.assertContains(response, "Appliquer")
        # Vérifier que les données de la commission sont présentes dans le formulaire
        self.assertContains(response, commission.title)
        self.assertContains(response, commission.icon)

    # Test de la page de modification de commission avec des données valides
    def test_admin_views_edit_commission_post(self):
        """
        Test de la page de modification de commission avec des données valides
        """
        commission = self.create_commission(title="Test Commission", icon="icon.png")
        response = self.client.post(
            reverse("commissions:admin_edit_commission", args=[commission.id]),
            {"title": "Modified Commission", "icon": "modified_icon.png"},
        )
        # Vérifier que la réponse est une redirection (code 302)
        self.assertEqual(response.status_code, 302)
        # Vérifier que la redirection est correcte
        self.assertRedirects(response, reverse("commissions:admin_list_commissions"))
        # Vérifier que la commission a été modifiée
        commission.refresh_from_db()
        self.assertEqual(commission.title, "Modified Commission")
        self.assertEqual(commission.icon, "modified_icon.png")

    # Test de la page de modification de commission avec des données invalides
    def test_admin_views_edit_commission_post_invalid(self):
        """
        Test de la page de modification de commission avec des données invalides
        """
        commission = self.create_commission(title="Test Commission", icon="icon.png")
        response = self.client.post(
            reverse("commissions:admin_edit_commission", args=[commission.id]),
            {"title": "", "icon": ""},
        )
        # Vérifier que la réponse est un succès (code 200)
        self.assertEqual(response.status_code, 200)
        # Vérifier que le bon template est utilisé
        self.assertTemplateUsed(response, "commissions/admin_commission_edit.html")
        # Vérifier que la commission n'a pas été modifiée
        commission.refresh_from_db()
        self.assertEqual(commission.title, "Test Commission")

    # Test de la page de suppression de commission
    def test_admin_views_delete_commission(self):
        """
        Test de la page de suppression de commission
        """
        commission = self.create_commission(title="Test Commission", icon="icon.png")
        response = self.client.post(
            reverse("commissions:admin_delete_commission", args=[commission.id])
        )
        # Vérifier que la réponse est une redirection (code 302)
        self.assertEqual(response.status_code, 302)
        # Vérifier que la redirection est correcte
        self.assertRedirects(response, reverse("commissions:admin_list_commissions"))
        # Vérifier que la commission a été supprimée
        self.assertFalse(Commission.objects.filter(title="Test Commission").exists())

    # Test de la page d'ajout de document
    def test_admin_views_add_document_get(self):
        """
        Test d'affichage de la page d'ajout de document
        """
        response = self.client.get(reverse("commissions:upload_commission_doc"))
        # Vérifier que la réponse est un succès (code 200)
        self.assertEqual(response.status_code, 200)
        # Vérifier que le bon template est utilisé
        self.assertTemplateUsed(response, "commissions/admin_commission_add_doc.html")
        # Vérifier que le formulaire est présent
        self.assertContains(response, "Ajouter un document")
        self.assertContains(response, "Document à uploader")
        self.assertContains(response, "Ajouter")

    # Test de la page d'ajout de document avec des données valides
    def test_admin_views_add_document_post(self):
        """
        Test de la page d'ajout de document avec des données valides
        """
        response = self.client.post(
            reverse("commissions:upload_commission_doc"),
            {
                "file": SimpleUploadedFile(
                    name="test.pdf",
                    content=b"Test content",
                    content_type="application/pdf",
                )
            },
        )
        # Vérifier que la réponse est une redirection (code 302)
        self.assertEqual(response.status_code, 302)
        # Vérifier que la redirection est correcte
        self.assertRedirects(response, reverse("commissions:admin_list_commissions"))
        # Vérifier que le document a été créé
        self.assertEqual(Document.objects.count(), 1)
        # Vérifier que le document ajouté dans le répertoire MEDIA_ROOT
        self.assertTrue(
            os.path.exists("test_commission_media/commissions/documents/test.pdf")
        )

    # Test de la page d'ajout de document avec des données invalides
    def test_admin_views_add_document_post_invalid(self):
        """
        Test de la page d'ajout de document avec des données invalides
        """
        response = self.client.post(
            reverse("commissions:upload_commission_doc"), {"file": ""}
        )
        # Vérifier que la réponse est un succès (code 200)
        self.assertEqual(response.status_code, 200)
        # Vérifier que le bon template est utilisé
        self.assertTemplateUsed(response, "commissions/admin_commission_add_doc.html")
        # Vérifier que le document n'a pas été créé
        self.assertEqual(Document.objects.count(), 0)
        # Vérifier qu'aucun fichier n'a été ajouté dans le répertoire MEDIA_ROOT
        self.assertFalse(
            os.path.exists("test_commission_media/commissions/documents/test.pdf")
        )

    # Test de la page de modification de document
    def test_admin_views_edit_document_get(self):
        """
        Test d'affichage de la page de modification de document
        """
        document = self.create_document(file_name="test.pdf")
        response = self.client.get(
            reverse("commissions:edit_document", args=[document.id])
        )
        # Vérifier que la réponse est un succès (code 200)
        self.assertEqual(response.status_code, 200)
        # Vérifier que le bon template est utilisé
        self.assertTemplateUsed(response, "commissions/admin_commission_edit_doc.html")
        # Vérifier que le formulaire est présent
        self.assertContains(response, "Modifier le document")
        self.assertContains(response, "Document à uploader")
        self.assertContains(response, "Appliquer")

    # Test de la page de modification de document avec des données valides
    def test_admin_views_edit_document_post(self):
        """
        Test de la page de modification de document avec des données valides
        """
        document = self.create_document(file_name="test.pdf")
        response = self.client.post(
            reverse("commissions:edit_document", args=[document.id]),
            {
                "file": SimpleUploadedFile(
                    name="modified_test.pdf",
                    content=b"Modified content",
                    content_type="application/pdf",
                )
            },
        )
        # Vérifier que la réponse est une redirection (code 302)
        self.assertEqual(response.status_code, 302)
        # Vérifier que la redirection est correcte
        self.assertRedirects(response, reverse("commissions:admin_list_commissions"))
        # Vérifier que le document a été modifié
        document.refresh_from_db()
        self.assertTrue(
            os.path.exists(
                "test_commission_media/commissions/documents/modified_test.pdf"
            )
        )
        # Vérifier que l'ancien document a été supprimé
        self.assertFalse(
            os.path.exists("test_commission_media/commissions/documents/test.pdf")
        )

    # Test de la page de modification de document avec des données invalides
    def test_admin_views_edit_document_post_invalid(self):
        """
        Test de la page de modification de document avec des données invalides
        """
        document = self.create_document(file_name="test.pdf")
        response = self.client.post(
            reverse("commissions:edit_document", args=[document.id]), {"file": ""}
        )
        # Vérifier que la réponse est une redirection (code 302)
        self.assertEqual(response.status_code, 302)
        # Vérifier que la redirection est correcte
        self.assertRedirects(response, reverse("commissions:admin_list_commissions"))
        # Vérifier que le document n'a pas été modifié
        document.refresh_from_db()
        self.assertTrue(
            os.path.exists("test_commission_media/commissions/documents/test.pdf")
        )
        # Vérifier que le document n'a pas été uploadé
        self.assertFalse(
            os.path.exists(
                "test_commission_media/commissions/documents/modified_test.pdf"
            )
        )

    # Test de la page de suppression de document
    def test_admin_views_delete_document_get(self):
        """
        Test de la page de suppression de document
        """
        document = self.create_document(file_name="test.pdf")
        response = self.client.post(
            reverse("commissions:delete_document", args=[document.id])
        )
        # Vérifier que la réponse est correcte (code 302)
        self.assertEqual(response.status_code, 302)
        # Vérifier que la redirection est correcte
        self.assertRedirects(response, reverse("commissions:admin_list_commissions"))
        # Vérifier que le document a été supprimé
        self.assertFalse(Document.objects.filter(file="test.pdf").exists())

    # Test de la suppression de document
    def test_admin_views_delete_document_post(self):
        """
        Test de la suppression de document
        """
        document = self.create_document(file_name="test.pdf")
        response = self.client.post(
            reverse("commissions:delete_document", args=[document.id])
        )
        # Vérifier que la réponse est correcte (code 302)
        self.assertEqual(response.status_code, 302)
        # Vérifier que la redirection est correcte
        self.assertRedirects(response, reverse("commissions:admin_list_commissions"))
        # Vérifier que le document a été supprimé de la base de données
        self.assertFalse(Document.objects.filter(file="test.pdf").exists())
        # Vérifier que le document a été supprimé du système de fichiers
        self.assertFalse(
            os.path.exists("test_commission_media/commissions/documents/test.pdf")
        )

    # Test de la page de modification de mandat
    def test_admin_views_edit_mandat_get(self):
        """
        Test d'affichage de la page de modification de mandat
        """
        mandat = self.set_mandat(start_year=2023, end_year=2024)
        response = self.client.get(reverse("commissions:edit_mandat", args=[mandat.id]))
        # Vérifier que la réponse est un succès (code 200)
        self.assertEqual(response.status_code, 200)
        # Vérifier que le bon template est utilisé
        self.assertTemplateUsed(
            response, "commissions/admin_commission_edit_mandat.html"
        )
        # Vérifier que le formulaire est présent
        self.assertContains(response, "Modifier le mandat")
        self.assertContains(response, "Année de début")
        self.assertContains(response, "Année de fin")
        self.assertContains(response, "2023")
        self.assertContains(response, "2024")
        # Vérifier que le bouton de modification est présent
        self.assertContains(response, "Appliquer")

    # Test de la page de modification de mandat avec des données valides
    def test_admin_views_edit_mandat_post(self):
        """
        Test de la page de modification de mandat avec des données valides
        """
        mandat = self.set_mandat(start_year=2023, end_year=2024)
        response = self.client.post(
            reverse("commissions:edit_mandat", args=[mandat.id]),
            {"start_year": 2025, "end_year": 2026},
        )
        # Vérifier que la réponse est une redirection (code 302)
        self.assertEqual(response.status_code, 302)
        # Vérifier que la redirection est correcte
        self.assertRedirects(response, reverse("commissions:admin_list_commissions"))
        # Vérifier que le mandat a été modifié
        mandat.refresh_from_db()
        self.assertEqual(mandat.start_year, 2025)
        self.assertEqual(mandat.end_year, 2026)

    # Test de la page de modification de mandat avec des données invalides
    def test_admin_views_edit_mandat_post_invalid(self):
        """
        Test de la page de modification de mandat avec des données invalides
        """
        mandat = self.set_mandat(start_year=2023, end_year=2024)
        response = self.client.post(
            reverse("commissions:edit_mandat", args=[mandat.id]),
            {"start_year": "", "end_year": ""},
        )
        # Vérifier que la réponse est un succès (code 200)
        self.assertEqual(response.status_code, 200)
        # Vérifier que le bon template est utilisé
        self.assertTemplateUsed(
            response, "commissions/admin_commission_edit_mandat.html"
        )
        # Vérifier que le mandat n'a pas été modifié
        mandat.refresh_from_db()
        self.assertEqual(mandat.start_year, 2023)
        self.assertEqual(mandat.end_year, 2024)

    # Test de la page de modification de mandat avec des données invalides
    def test_admin_views_edit_mandat_post_invalid_year(self):
        """
        Test de la page de modification de mandat avec des données invalides
        """
        mandat = self.set_mandat(start_year=2023, end_year=2024)
        response = self.client.post(
            reverse("commissions:edit_mandat", args=[mandat.id]),
            {"start_year": 2025, "end_year": 2024},
        )
        # Vérifier que la réponse est un succès (code 200)
        self.assertEqual(response.status_code, 200)
        # Vérifier que le mandat n'a pas été modifié
        mandat.refresh_from_db()
        self.assertEqual(mandat.start_year, 2023)
        self.assertEqual(mandat.end_year, 2024)
