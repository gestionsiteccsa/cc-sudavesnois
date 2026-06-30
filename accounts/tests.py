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


class SessionExpiryTests(TestCase):
    """
    Vérifie la configuration de la durée de session et l'effet de la case
    « Se souvenir de moi » sur ``request.session``.
    """

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="session_user",
            email="session@example.com",
            password="Str0ng-Pa55word!",
        )

    def test_settings_session_cookie_age_is_thirty_days(self):
        from django.conf import settings

        self.assertEqual(settings.SESSION_COOKIE_AGE, 30 * 24 * 60 * 60)

    def test_settings_session_save_every_request_is_true(self):
        from django.conf import settings

        self.assertTrue(settings.SESSION_SAVE_EVERY_REQUEST)

    def test_settings_session_engine_is_db(self):
        from django.conf import settings

        self.assertEqual(
            settings.SESSION_ENGINE,
            "django.contrib.sessions.backends.db",
        )

    def test_login_without_remember_me_uses_browser_session(self):
        self.client.post(
            reverse("accounts:login"),
            {
                "username": self.user.email,
                "password": "Str0ng-Pa55word!",
            },
        )
        # Avec set_expiry(0), la session expire à la fermeture du navigateur
        self.assertTrue(self.client.session.get_expire_at_browser_close())

    def test_login_with_remember_me_extends_session(self):
        self.client.post(
            reverse("accounts:login"),
            {
                "username": self.user.email,
                "password": "Str0ng-Pa55word!",
                "remember_me": "on",
            },
        )
        # Sans expire-at-browser-close, la session dure SESSION_COOKIE_AGE
        self.assertFalse(self.client.session.get_expire_at_browser_close())
        # Tolérance de 10s pour le delta d'exécution
        from django.conf import settings

        self.assertAlmostEqual(
            self.client.session.get_expiry_age(),
            settings.SESSION_COOKIE_AGE,
            delta=10,
        )

    def test_session_is_persisted_in_db(self):
        """Vérifie que la session est bien stockée dans la table django_session."""
        from django.contrib.sessions.models import Session

        self.client.post(
            reverse("accounts:login"),
            {
                "username": self.user.email,
                "password": "Str0ng-Pa55word!",
                "remember_me": "on",
            },
        )
        self.assertGreater(Session.objects.count(), 0)

    def test_sliding_session_refreshes_expiry(self):
        """SESSION_SAVE_EVERY_REQUEST=True : l'expiration est repoussée."""
        from django.conf import settings

        self.client.post(
            reverse("accounts:login"),
            {
                "username": self.user.email,
                "password": "Str0ng-Pa55word!",
                "remember_me": "on",
            },
        )
        initial_age = self.client.session.get_expiry_age()
        # Simule une requête ultérieure via un GET (n'importe quelle vue)
        self.client.get("/")
        new_age = self.client.session.get_expiry_age()
        # L'âge ne doit pas avoir décru
        self.assertGreaterEqual(new_age, initial_age - 5)
        self.assertAlmostEqual(new_age, settings.SESSION_COOKIE_AGE, delta=30)


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
            "password": "Str0ng-Pa55word!",
            "generate_password": "",
        }
        self.superuser_data = {
            "email": "superuser@example.com",
            "username": "superuser",
            "password": "Sup3r-Pa55word!",
        }
        self.superuser = User.objects.create_superuser(
            username=self.superuser_data["username"],
            email=self.superuser_data["email"],
            password=self.superuser_data["password"],
        )
        self.client.login(
            username=self.superuser_data["email"],
            password=self.superuser_data["password"],
        )

    def test_admin_create_user_page_get_views(self):
        response = self.client.get(reverse("accounts:admin_create_user"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/admin_create_user.html")
        self.assertContains(response, "Créer un utilisateur")

    def test_admin_create_user_with_explicit_password(self):
        response = self.client.post(
            reverse("accounts:admin_create_user"), self.user_data
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("accounts:admin_user_list"))
        created = User.objects.get(email=self.user_data["email"])
        self.assertTrue(created.check_password(self.user_data["password"]))
        self.assertFalse(created.is_superuser)
        self.assertFalse(created.is_staff)

    def test_admin_create_user_with_is_staff_flag(self):
        payload = {**self.user_data, "is_staff": "on"}
        response = self.client.post(reverse("accounts:admin_create_user"), payload)
        self.assertEqual(response.status_code, 302)
        created = User.objects.get(email=self.user_data["email"])
        self.assertTrue(created.is_staff)
        self.assertFalse(created.is_superuser)

    def test_admin_create_user_generates_secure_password(self):
        from django.core import mail

        payload = {
            "email": "generated@example.com",
            "username": "generated",
            "password": "",
            "generate_password": "on",
        }
        response = self.client.post(reverse("accounts:admin_create_user"), payload)
        self.assertEqual(response.status_code, 302)
        created = User.objects.get(email="generated@example.com")
        self.assertTrue(created.has_usable_password())
        self.assertFalse(created.check_password(""))
        # Le mot de passe généré doit être marqué comme "non commun"
        # (donc accepté par les validateurs Django par défaut).
        self.assertGreaterEqual(len(created.password), 80)  # hash pbkdf2
        # Email de bienvenue envoyé
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("generated@example.com", mail.outbox[0].to)
        self.assertIn("Mot de passe temporaire", mail.outbox[0].body)

    def test_admin_create_user_requires_password_or_generation(self):
        payload = {
            "email": "nopassword@example.com",
            "username": "nopassword",
            "password": "",
            "generate_password": "",
        }
        response = self.client.post(reverse("accounts:admin_create_user"), payload)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(email="nopassword@example.com").exists())

    def test_admin_create_user_rejects_anonymous(self):
        self.client.logout()
        response = self.client.post(
            reverse("accounts:admin_create_user"), self.user_data
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_admin_create_user_rejects_non_superuser(self):
        User.objects.create_user(
            username="regular", email="regular@example.com", password="Str0ng!"
        )
        self.client.logout()
        self.client.login(username="regular@example.com", password="Str0ng!")
        response = self.client.post(
            reverse("accounts:admin_create_user"), self.user_data
        )
        self.assertEqual(response.status_code, 302)


class AdminUserListTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_data = {
            "email": "testuser@example.com",
            "username": "testuser",
            "password": "Str0ng-Pa55word!",
        }
        self.superuser_data = {
            "email": "superuser@example.com",
            "username": "superuser",
            "password": "Sup3r-Pa55word!",
        }
        self.superuser = User.objects.create_superuser(
            username=self.superuser_data["username"],
            email=self.superuser_data["email"],
            password=self.superuser_data["password"],
        )
        self.user = User.objects.create_user(
            username=self.user_data["username"],
            email=self.user_data["email"],
            password=self.user_data["password"],
        )
        self.client.login(
            username=self.superuser_data["email"],
            password=self.superuser_data["password"],
        )

    def test_admin_user_list_page_get_views(self):
        response = self.client.get(reverse("accounts:admin_user_list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/admin_user_list.html")
        self.assertContains(response, "Gestion des utilisateurs")
        self.assertContains(response, "testuser@example.com")
        self.assertContains(response, "superuser@example.com")

    def test_admin_user_list_search(self):
        response = self.client.get(
            reverse("accounts:admin_user_list"), {"q": "testuser"}
        )
        self.assertEqual(response.status_code, 200)
        # Le tableau ne contient que les utilisateurs correspondant à la recherche
        self.assertEqual(response.context["page"].paginator.count, 1)
        self.assertEqual(
            response.context["page"].object_list[0].email,
            "testuser@example.com",
        )

    def test_admin_user_list_search_no_result(self):
        response = self.client.get(
            reverse("accounts:admin_user_list"), {"q": "no-such-user"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Aucun utilisateur ne correspond")

    def test_admin_user_list_pagination(self):
        # Crée 30 utilisateurs supplémentaires pour déclencher la pagination
        for i in range(30):
            User.objects.create_user(
                username=f"user{i:02d}",
                email=f"user{i:02d}@example.com",
                password="Str0ng-Pa55word!",
            )
        response = self.client.get(reverse("accounts:admin_user_list"), {"page": 2})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Page 2 sur")

    def test_admin_user_list_deactivate_user(self):
        response = self.client.post(
            reverse("accounts:admin_user_list"),
            {"user_id": self.user.id, "action": "deactivate"},
        )
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)

    def test_admin_user_list_activate_user(self):
        self.user.is_active = False
        self.user.save()
        response = self.client.post(
            reverse("accounts:admin_user_list"),
            {"user_id": self.user.id, "action": "activate"},
        )
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)

    def test_admin_user_list_delete_user(self):
        target_id = self.user.id
        response = self.client.post(
            reverse("accounts:admin_user_list"),
            {"user_id": target_id, "action": "delete"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(User.objects.filter(id=target_id).exists())

    def test_admin_cannot_self_deactivate(self):
        response = self.client.post(
            reverse("accounts:admin_user_list"),
            {"user_id": self.superuser.id, "action": "deactivate"},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.superuser.refresh_from_db()
        self.assertTrue(self.superuser.is_active)
        self.assertContains(
            response, "Vous ne pouvez pas désactiver ou supprimer votre propre compte."
        )

    def test_admin_cannot_self_delete(self):
        response = self.client.post(
            reverse("accounts:admin_user_list"),
            {"user_id": self.superuser.id, "action": "delete"},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(id=self.superuser.id).exists())
        self.assertContains(
            response, "Vous ne pouvez pas désactiver ou supprimer votre propre compte."
        )

    def test_admin_cannot_modify_other_superadmin(self):
        User.objects.create_superuser(
            username="other_super",
            email="other_super@example.com",
            password="Sup3r-Pa55word!",
        )
        self.client.logout()
        self.client.login(
            username="other_super@example.com", password="Sup3r-Pa55word!"
        )
        response = self.client.post(
            reverse("accounts:admin_user_list"),
            {"user_id": self.superuser.id, "action": "deactivate"},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.superuser.refresh_from_db()
        self.assertTrue(self.superuser.is_active)
        self.assertContains(
            response, "Vous ne pouvez pas modifier un autre superadministrateur."
        )

    def test_unknown_action_is_rejected(self):
        response = self.client.post(
            reverse("accounts:admin_user_list"),
            {"user_id": self.user.id, "action": "pwn"},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Action inconnue")
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)

    def test_list_rejects_anonymous(self):
        self.client.logout()
        response = self.client.get(reverse("accounts:admin_user_list"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)


class AdminActionAuditLogTests(TestCase):
    """
    Vérifie que chaque action admin (activate/deactivate/delete) est tracée
    dans le logger ``accounts.audit``.
    """

    def setUp(self):
        self.client = Client()
        self.superuser = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="Sup3r-Pa55word!",
        )
        self.user = User.objects.create_user(
            username="target",
            email="target@example.com",
            password="Targ3t-Pa55word!",
        )
        self.client.login(username="admin@example.com", password="Sup3r-Pa55word!")

    def test_activate_is_logged(self):
        with self.assertLogs("accounts.audit", level="INFO") as captured:
            self.client.post(
                reverse("accounts:admin_user_list"),
                {"user_id": self.user.id, "action": "activate"},
            )
        self.assertEqual(len(captured.records), 1)
        self.assertIn("user_activated", captured.records[0].getMessage())
        self.assertIn(
            f"target_user_id={self.user.id}", captured.records[0].getMessage()
        )

    def test_deactivate_is_logged(self):
        with self.assertLogs("accounts.audit", level="INFO") as captured:
            self.client.post(
                reverse("accounts:admin_user_list"),
                {"user_id": self.user.id, "action": "deactivate"},
            )
        self.assertEqual(len(captured.records), 1)
        self.assertIn("user_deactivated", captured.records[0].getMessage())

    def test_delete_is_logged_at_warning_level(self):
        target_pk = self.user.id
        with self.assertLogs("accounts.audit", level="INFO") as captured:
            self.client.post(
                reverse("accounts:admin_user_list"),
                {"user_id": target_pk, "action": "delete"},
            )
        delete_logs = [r for r in captured.records if "user_deleted" in r.getMessage()]
        self.assertEqual(len(delete_logs), 1)
        self.assertEqual(delete_logs[0].levelname, "WARNING")
        self.assertIn(f"target_user_id={target_pk}", delete_logs[0].getMessage())


class CustomUserModelTests(TestCase):
    """Tests des contraintes et index du modèle CustomUser."""

    def test_duplicate_username_is_rejected(self):
        User.objects.create_user(
            username="dup", email="a@example.com", password="Str0ng-Pa55!"
        )
        with self.assertRaises(Exception):
            User.objects.create_user(
                username="dup", email="b@example.com", password="Str0ng-Pa55!"
            )

    def test_empty_username_allows_multiple_users(self):
        """La contrainte unique exclut les usernames vides (blank=True)."""
        u1 = User.objects.create_user(
            username="", email="a@example.com", password="Str0ng-Pa55!"
        )
        u2 = User.objects.create_user(
            username="", email="b@example.com", password="Str0ng-Pa55!"
        )
        self.assertNotEqual(u1.pk, u2.pk)


class RegisterViewSingleSaveTests(TestCase):
    """
    Vérifie que ``register_view`` n'effectue qu'une seule écriture en base
    pour le premier utilisateur (commit=False + save une fois).
    """

    def test_first_user_is_superuser_after_single_request(self):
        from django.db import connection
        from django.test.utils import CaptureQueriesContext

        user_data = {
            "email": "first@example.com",
            "username": "firstadmin",
            "password1": "Str0ng-Pa55word!",
            "password2": "Str0ng-Pa55word!",
        }
        with CaptureQueriesContext(connection) as ctx:
            response = self.client.post(reverse("accounts:register"), user_data)
        self.assertEqual(response.status_code, 302)
        created = User.objects.get(email="first@example.com")
        self.assertTrue(created.is_superuser)
        self.assertTrue(created.is_staff)
        # Filtrer sur la table accounts_customuser uniquement (les sessions
        # et autres tables applicatives peuvent générer des INSERT annexes).
        user_inserts = sum(
            1
            for q in ctx.captured_queries
            if "INSERT INTO" in q["sql"] and "accounts_customuser" in q["sql"]
        )
        user_updates = sum(
            1
            for q in ctx.captured_queries
            if "UPDATE" in q["sql"] and "accounts_customuser" in q["sql"]
        )
        self.assertEqual(
            user_inserts,
            1,
            f"Trop d'INSERT sur accounts_customuser: {ctx.captured_queries}",
        )
        # Avec commit=False, il ne doit pas y avoir d'UPDATE redondant.
        self.assertLessEqual(
            user_updates, 1, f"UPDATE en trop sur accounts_customuser: {user_updates}"
        )


class WelcomeEmailTests(TestCase):
    """Tests du template email de bienvenue."""

    def test_welcome_email_contains_generated_password(self):
        from django.template.loader import render_to_string

        class _StubUser:
            username = "nouveau"
            email = "nouveau@example.com"

        body = render_to_string(
            "accounts/welcome_email.txt",
            {
                "user": _StubUser(),
                "password": "Tmp-Pa55-ABCDEF",
                "domain": "cc-sudavesnois.fr",
                "protocol": "https",
            },
        )
        self.assertIn("nouveau@example.com", body)
        self.assertIn("Tmp-Pa55-ABCDEF", body)
        self.assertIn("cc-sudavesnois.fr", body)


class WelcomeEmailFailureTests(TestCase):
    """
    Vérifie que l'échec d'envoi SMTP ne lève pas d'exception et est tracé
    dans le logger.
    """

    def setUp(self):
        self.client = Client()

    def test_smtp_failure_does_not_crash_view(self):
        import smtplib
        from unittest.mock import patch

        from accounts.forms import AdminUserCreationForm

        form = AdminUserCreationForm(
            data={
                "email": "smtpfail@example.com",
                "username": "smtpfail",
                "password": "",
                "generate_password": "on",
            }
        )
        self.assertTrue(form.is_valid(), form.errors.as_json())
        user = form.save()
        self.assertIsNotNone(form.generated_password)
        self.assertTrue(user.check_password(form.generated_password))

        with patch(
            "accounts.views.send_mail", side_effect=smtplib.SMTPException("boom")
        ) as mock_send, patch("accounts.views.logger.error") as mock_error:
            from accounts.views import _send_welcome_email

            class _StubRequest:
                scheme = "https"

                def get_host(self):
                    return "example.com"

            result = _send_welcome_email(user, form.generated_password, _StubRequest())
        self.assertFalse(result, "Doit retourner False en cas d'échec SMTP")
        mock_send.assert_called_once()
        mock_error.assert_called_once()
        call_args = mock_error.call_args[0]
        self.assertIn("Échec d'envoi", call_args[0])
        self.assertIn("smtpfail@example.com", call_args[1])
