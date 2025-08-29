from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class RegisterPasswordTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_data = {
            "email": "testuser@example.com",
            "username": "testuser",
            "password1": "12345678",
            "password2": "12345678",
        }

    def test_register_short_complex_passwords(self):
        short_complex_passwords = [
            "A1b!c2",
            "xYz#12",
            "Qw3$rT",
            "1aB@cD",
            "P@ss7!",
            "Z9x!Y2",
            "Lm#4nO",
            "Tg5$hJ",
            "Vb6^nM",
        ]
        for password in short_complex_passwords:
            user_data = self.user_data.copy()
            user_data["password1"] = password
            user_data["password2"] = password
            response = self.client.post(reverse("accounts:register"), user_data)
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, "accounts/register.html")
            self.assertContains(
                response,
                "Ce mot de passe est trop court. Il doit contenir au minimum 8 caractères.",
            )

    def test_register_only_digit_passwords(self):
        digit_passwords = [
            "12345678",
            "11111111",
            "00000000",
            "123123123",
            "987654321",
            "22222222",
            "33333333",
            "44444444",
            "55555555",
        ]
        for password in digit_passwords:
            user_data = self.user_data.copy()
            user_data["password1"] = password
            user_data["password2"] = password
            response = self.client.post(reverse("accounts:register"), user_data)
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, "accounts/register.html")
            self.assertContains(response, "Ce mot de passe est trop courant.")

    def test_register_common_passwords(self):
        common_passwords = [
            # English common passwords
            "password",
            "qwerty",
            "abc123",
            "letmein",
            "monkey",
            "111111",
            "iloveyou",
            "admin",
            "welcome",
            "123456",
            "123456789",
            "12345678",
            "12345",
            "123123",
            "sunshine",
            "princess",
            "football",
            "dragon",
            "baseball",
            "superman",
            "batman",
            "trustno1",
            "passw0rd",
            "master",
            "hello",
            "freedom",
            "whatever",
            "qazwsx",
            "654321",
            "1q2w3e4r",
            # French common passwords
            "motdepasse",
            "azerty",
            "soleil",
            "bonjour",
            "chocolat",
            "123soleil",
            "marseille",
            "paris",
            "prenom",
            "azertyuiop",
            "loulou",
            "doudou",
            "toto",
            "papa",
            "maman",
            "fanfan",
            "coucou",
            "amour",
            "secret",
            "ordinateur",
            "fromage",
            "montagne",
            "voiture",
            "camille",
            "julien",
            "sophie",
            "thomas",
            "juillet",
            "octobre",
        ]
        for password in common_passwords:
            # print(f'Testing password: {password}')
            user_data = self.user_data.copy()
            user_data["password1"] = password
            user_data["password2"] = password
            response = self.client.post(reverse("accounts:register"), user_data)
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, "accounts/register.html")
            self.assertNotEqual(response.status_code, 302)


class RegisterPageTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_data = {
            "email": "testuser@example.com",
            "username": "testuser",
            "password1": "testpassword",
            "password2": "testpassword",
        }

    def test_register_page_get_views(self):
        response = self.client.get(reverse("accounts:register"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/register.html")

    def test_register_page_post_views(self):
        response = self.client.post(reverse("accounts:register"), self.user_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("accounts:profile"))
        self.assertTrue(User.objects.filter(username="testuser").exists())
        self.assertTrue(User.objects.get(email="testuser@example.com").is_superuser)

    def test_register_page_if_user_exists(self):
        """
        Test si la page d'inscription n'est pas accessible si un utilisateur existe déjà
        """
        User.objects.create_user(
            username=self.user_data["username"],
            email=self.user_data["email"],
            password=self.user_data["password1"],
        )
        response = self.client.post(reverse("accounts:register"), self.user_data)
        self.assertEqual(response.status_code, 302)
        self.assertTemplateNotUsed(response, "accounts/register.html")


class LoginPageTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_data = {
            "email": "testuser@example.com",
            "username": "testuser",
            "password": "testpassword",
        }

    def test_first_login_page_get_views(self):
        response = self.client.get(reverse("accounts:login"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/login.html")
        self.assertContains(response, "Créer le premier compte administrateur")

    def test_login_page_get_views(self):
        response = self.client.get(reverse("accounts:login"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/login.html")
        self.assertContains(response, "Se connecter")

    def test_login_page_post_views_valid_data(self):
        # Create a user to test login
        User.objects.create_user(
            username=self.user_data["username"],
            email=self.user_data["email"],
            password=self.user_data["password"],
        )
        response = self.client.post(
            reverse("accounts:login"),
            {
                "username": self.user_data["email"],
                "password": self.user_data["password"],
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse("accounts:profile"))

    def test_login_page_post_views_invalid_data(self):
        response = self.client.post(
            reverse("accounts:login"),
            {
                "username": self.user_data["email"],
                "password": "wrongpassword",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/login.html")
        self.assertContains(response, "Adresse email ou mot de passe incorrect.")


class PasswordResetPageTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_data = {
            "email": "testuser@example.com",
            "username": "testuser",
            "password1": "testpassword",
            "password2": "testpassword",
        }
        self.user = User.objects.create_user(
            username=self.user_data["username"],
            email=self.user_data["email"],
            password=self.user_data["password1"],
        )

    def test_password_reset_page_get_views(self):
        """
        Test de la page de réinitialisation de mot de passe
        """
        response = self.client.get(reverse("accounts:password_reset"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/password_reset.html")
        self.assertContains(response, "Réinitialisation du mot de passe")
        self.assertContains(response, "Envoyer le lien de réinitialisation")

    def test_password_reset_page_post_views(self):
        """
        Test de la réinitialisation de mot de passe
        """
        response = self.client.post(
            reverse("accounts:password_reset"), {"email": self.user_data["email"]}
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("accounts:password_reset_done"))


class AdminCreateUserTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_data = {
            "email": "testuser@example.com",
            "username": "testuser",
            "password1": "testpassword",
            "password2": "testpassword",
        }
        self.superuser_data = {
            "email": "superuser@example.com",
            "username": "superuser",
            "password1": "superpassword",
            "password2": "superpassword",
        }
        # Create a superuser for testing
        self.superuser = User.objects.create_superuser(
            username=self.superuser_data["username"],
            email=self.superuser_data["email"],
            password=self.superuser_data["password1"],
        )
        self.client.login(
            username=self.superuser_data["email"],
            password=self.superuser_data["password1"],
        )

    def test_admin_create_user_page_get_views(self):
        """
        Test de la page de création d'utilisateur
        """
        response = self.client.get(reverse("accounts:admin_create_user"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/admin_create_user.html")
        self.assertContains(response, "Créer un utilisateur")

    def test_admin_create_user_page_post_views(self):
        """
        Test de la création d'utilisateur
        """
        response = self.client.post(
            reverse("accounts:admin_create_user"), self.user_data
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("accounts:admin_user_list"))
        self.assertTrue(
            User.objects.filter(username=self.user_data["username"]).exists()
        )
        self.assertFalse(User.objects.get(email=self.user_data["email"]).is_superuser)


class AdminUserListTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_data = {
            "email": "testuser@example.com",
            "username": "testuser",
            "password1": "testpassword",
            "password2": "testpassword",
        }
        self.superuser_data = {
            "email": "superuser@example.com",
            "username": "superuser",
            "password1": "superpassword",
            "password2": "superpassword",
        }
        # Create a superuser for testing
        self.superuser = User.objects.create_superuser(
            username=self.superuser_data["username"],
            email=self.superuser_data["email"],
            password=self.superuser_data["password1"],
        )
        self.client.login(
            username=self.superuser_data["email"],
            password=self.superuser_data["password1"],
        )
        # Create a user for testing
        self.user = User.objects.create_user(
            username=self.user_data["username"],
            email=self.user_data["email"],
            password=self.user_data["password1"],
        )

    def test_admin_user_list_page_get_views(self):
        """
        Test de la page de liste des utilisateurs
        """
        response = self.client.get(reverse("accounts:admin_user_list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/admin_user_list.html")
        self.assertContains(response, "Gestion des utilisateurs")
        self.assertContains(response, "testuser@example.com")
        self.assertContains(response, "superuser@example.com")
