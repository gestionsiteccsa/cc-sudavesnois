"""
Tests pour l'application linktree.
"""
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import Client, TestCase
from django.urls import reverse

from .models import Lien

User = get_user_model()


class LienModelTest(TestCase):
    """Tests pour le modèle Lien"""
    
    def setUp(self):
        self.lien = Lien.objects.create(
            titre="Test Facebook",
            url="https://facebook.com/test",
            icone="facebook",
            ordre=1,
            actif=True
        )
    
    def test_str_representation(self):
        """Test la représentation string du modèle"""
        self.assertEqual(
            str(self.lien),
            "Test Facebook (Facebook)"
        )
    
    def test_get_icone_svg_facebook(self):
        """Test la récupération du SVG Facebook"""
        svg = self.lien.get_icone_svg()
        self.assertIn("<svg", svg)
        # Vérifie que le SVG contient bien une icône (path)
        self.assertIn("</svg>", svg)
    
    def test_get_icone_svg_default(self):
        """Test le SVG par défaut pour une icône inexistante"""
        self.lien.icone = "inexistant"
        svg = self.lien.get_icone_svg()
        self.assertIn("<svg", svg)
    
    def test_ordering(self):
        """Test l'ordre des liens"""
        # Créer des liens avec différents ordres
        Lien.objects.create(
            titre="B Lien",
            url="https://test.com/b",
            ordre=3
        )
        Lien.objects.create(
            titre="A Lien",
            url="https://test.com/a",
            ordre=2
        )
        liens = list(Lien.objects.all())
        # Vérifie que l'ordre est respecté (ordre croissant)
        self.assertEqual(liens[0].ordre, 1)  # Le premier créé dans setUp
        self.assertEqual(liens[1].ordre, 2)  # A Lien
        self.assertEqual(liens[2].ordre, 3)  # B Lien


class LinktreePageViewTest(TestCase):
    """Tests pour la vue publique linktree_page"""
    
    def setUp(self):
        self.client = Client()
        self.url = reverse('linktree:linktree_page')
        
        # Créer des liens actifs
        self.lien_actif = Lien.objects.create(
            titre="Facebook",
            url="https://facebook.com/ccsa",
            icone="facebook",
            ordre=1,
            actif=True
        )
        
        # Créer un lien inactif
        Lien.objects.create(
            titre="Instagram",
            url="https://instagram.com/ccsa",
            icone="instagram",
            ordre=2,
            actif=False
        )
    
    def test_page_accessible(self):
        """Test que la page est accessible"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
    
    def test_template_used(self):
        """Test que le bon template est utilisé"""
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'linktree/linktree_page.html')
    
    def test_only_active_links_displayed(self):
        """Test que seuls les liens actifs sont affichés"""
        response = self.client.get(self.url)
        self.assertContains(response, "Facebook")
        self.assertNotContains(response, "Instagram")
    
    def test_meta_description_in_context(self):
        """Test que la meta description est dans le contexte"""
        response = self.client.get(self.url)
        self.assertIn('meta_description', response.context)
    
    def test_logo_displayed(self):
        """Test que le logo est affiché"""
        response = self.client.get(self.url)
        self.assertContains(response, "Logo_S-A.png")
    
    def test_accessibility_skip_link(self):
        """Test que le skip link est présent"""
        response = self.client.get(self.url)
        self.assertContains(response, "Aller au contenu")
    
    def test_external_links_indicated(self):
        """Test que les liens externes sont signalés"""
        response = self.client.get(self.url)
        self.assertContains(response, "(nouvelle fenêtre)")


class AdminViewsTest(TestCase):
    """Tests pour les vues d'administration"""
    
    def setUp(self):
        self.client = Client()
        
        # Créer un utilisateur avec les permissions nécessaires
        self.user = User.objects.create_user(
            email='admin_test@example.com',
            password='testpass123'
        )
        
        # Ajouter les permissions
        permissions = [
            'view_lien',
            'add_lien',
            'change_lien',
            'delete_lien'
        ]
        
        for perm_codename in permissions:
            perm = Permission.objects.get(
                codename=perm_codename,
                content_type__app_label='linktree'
            )
            self.user.user_permissions.add(perm)
        
        self.lien = Lien.objects.create(
            titre="Test",
            url="https://test.com",
            icone="site-web",
            ordre=1
        )
    
    def test_list_view_requires_permission(self):
        """Test que la liste nécessite une permission"""
        # Sans connexion
        response = self.client.get(reverse('linktree:admin_liens_list'))
        self.assertEqual(response.status_code, 302)  # Redirection vers login
        
        # Avec connexion
        self.client.login(email='admin_test@example.com', password='testpass123')
        response = self.client.get(reverse('linktree:admin_liens_list'))
        self.assertEqual(response.status_code, 200)
    
    def test_add_view_requires_permission(self):
        """Test que l'ajout nécessite une permission"""
        self.client.login(email='admin_test@example.com', password='testpass123')
        response = self.client.get(reverse('linktree:admin_lien_add'))
        self.assertEqual(response.status_code, 200)
    
    def test_add_lien_success(self):
        """Test l'ajout réussi d'un lien"""
        self.client.login(email='admin_test@example.com', password='testpass123')
        
        data = {
            'titre': 'Nouveau Lien',
            'url': 'https://nouveau.com',
            'icone': 'facebook',
            'ordre': 5,
            'actif': True
        }
        
        response = self.client.post(
            reverse('linktree:admin_lien_add'),
            data
        )
        
        self.assertEqual(response.status_code, 302)  # Redirection après succès
        self.assertTrue(Lien.objects.filter(titre='Nouveau Lien').exists())
    
    def test_edit_view_requires_permission(self):
        """Test que la modification nécessite une permission"""
        self.client.login(email='admin_test@example.com', password='testpass123')
        response = self.client.get(
            reverse('linktree:admin_lien_edit', kwargs={'pk': self.lien.pk})
        )
        self.assertEqual(response.status_code, 200)
    
    def test_edit_lien_success(self):
        """Test la modification réussie d'un lien"""
        self.client.login(email='admin_test@example.com', password='testpass123')
        
        data = {
            'titre': 'Lien Modifié',
            'url': 'https://modifie.com',
            'icone': 'linkedin',
            'ordre': 10,
            'actif': False
        }
        
        response = self.client.post(
            reverse('linktree:admin_lien_edit', kwargs={'pk': self.lien.pk}),
            data
        )
        
        self.assertEqual(response.status_code, 302)
        self.lien.refresh_from_db()
        self.assertEqual(self.lien.titre, 'Lien Modifié')
        self.assertFalse(self.lien.actif)
    
    def test_delete_view_requires_permission(self):
        """Test que la suppression nécessite une permission"""
        self.client.login(email='admin_test@example.com', password='testpass123')
        response = self.client.get(
            reverse('linktree:admin_lien_delete', kwargs={'pk': self.lien.pk})
        )
        self.assertEqual(response.status_code, 200)
    
    def test_delete_lien_success(self):
        """Test la suppression réussie d'un lien"""
        self.client.login(email='admin_test@example.com', password='testpass123')
        
        lien_id = self.lien.pk
        response = self.client.post(
            reverse('linktree:admin_lien_delete', kwargs={'pk': lien_id}),
            {'confirm': 'yes'}
        )
        
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Lien.objects.filter(pk=lien_id).exists())
    
    def test_delete_cancelled(self):
        """Test l'annulation de la suppression"""
        self.client.login(email='admin_test@example.com', password='testpass123')
        
        lien_id = self.lien.pk
        response = self.client.post(
            reverse('linktree:admin_lien_delete', kwargs={'pk': lien_id}),
            {'confirm': 'no'}
        )
        
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Lien.objects.filter(pk=lien_id).exists())


class LienFormTest(TestCase):
    """Tests pour le formulaire LienForm"""
    
    def test_valid_form(self):
        """Test un formulaire valide"""
        from .forms import LienForm
        
        data = {
            'titre': 'Test Valide',
            'url': 'https://test.com',
            'icone': 'facebook',
            'ordre': 1,
            'actif': True
        }
        
        form = LienForm(data=data)
        self.assertTrue(form.is_valid())
    
    def test_invalid_url(self):
        """Test une URL invalide"""
        from .forms import LienForm
        
        data = {
            'titre': 'Test',
            'url': 'pas-une-url',
            'icone': 'facebook',
            'ordre': 1,
            'actif': True
        }
        
        form = LienForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('url', form.errors)
    
    def test_missing_required_fields(self):
        """Test les champs obligatoires manquants"""
        from .forms import LienForm
        
        data = {}
        form = LienForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('titre', form.errors)
        self.assertIn('url', form.errors)


class IconChoicesTest(TestCase):
    """Tests pour les choix d'icônes"""
    
    def test_all_icons_have_svg(self):
        """Test que toutes les icônes ont un SVG correspondant"""
        from .models import Lien
        
        lien = Lien(titre="Test", url="https://test.com")
        
        for icon_value, icon_name in Lien.ICON_CHOICES:
            lien.icone = icon_value
            svg = lien.get_icone_svg()
            self.assertIn("<svg", svg, f"L'icône {icon_name} n'a pas de SVG")
    
    def test_social_media_icons(self):
        """Test que les icônes de réseaux sociaux sont disponibles"""
        from .models import Lien
        
        social_icons = [
            'facebook', 'instagram', 'linkedin', 'youtube',
            'twitter', 'tiktok', 'snapchat', 'pinterest',
            'whatsapp', 'telegram', 'line', 'discord', 'twitch'
        ]
        
        icon_values = [choice[0] for choice in Lien.ICON_CHOICES]
        
        for icon in social_icons:
            self.assertIn(
                icon, icon_values,
                f"L'icône {icon} devrait être disponible"
            )
