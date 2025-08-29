import re

from django.core import mail
from django.core.cache import cache
from django.test import LiveServerTestCase, override_settings
from django.urls import reverse

import requests

from contact.models import ContactEmail


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    CSRF_COOKIE_SECURE=False,
    SESSION_COOKIE_SECURE=False,
    TESTING=False,
)
class ContactFormRateLimitFunctionalTest(LiveServerTestCase):
    """Tests fonctionnels du rate limiting du formulaire de contact.

    Utilise un serveur de test réel et envoie des requêtes HTTP avec CSRF valide.
    """

    def setUp(self):
        cache.clear()
        ContactEmail.objects.create(email="contact@ccsa.fr", is_active=True)
        self.session = requests.Session()
        self.url = f"{self.live_server_url}{reverse('home')}"

        # Récupération du token CSRF depuis la page d'accueil
        response = self.session.get(self.url)
        assert response.status_code == 200
        match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', response.text)
        assert match, "CSRF token introuvable dans la page d'accueil"
        self.csrf_token = match.group(1)

    def tearDown(self):
        self.session.close()

    def _submit_contact_form(self, ip_address: str):
        data = {
            "first_name": "Jean",
            "last_name": "Dupont",
            "email": "jean.dupont@example.com",
            "phone": "0123456789",
            "message": "Ceci est un message de test",
            "rgpd": "on",
            "csrfmiddlewaretoken": self.csrf_token,
        }
        headers = {"X-Forwarded-For": ip_address, "Referer": self.url}
        return self.session.post(
            self.url, data=data, headers=headers, allow_redirects=False
        )

    def test_rate_limit_blocks_6th_submission_same_ip_functional(self):
        # 5 soumissions autorisées depuis la même IP
        for _ in range(5):
            response = self._submit_contact_form("11.22.33.44")
            self.assertEqual(response.status_code, 302)

        # 2 emails par soumission : 10 emails attendus
        self.assertEqual(len(mail.outbox), 10)

        # 6e soumission : doit être bloquée (toujours 10 emails)
        response = self._submit_contact_form("11.22.33.44")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 10)

        # Une autre IP doit passer et ajouter 2 emails supplémentaires
        response = self._submit_contact_form("11.22.33.45")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 12)
