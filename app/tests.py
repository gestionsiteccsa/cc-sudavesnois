"""Tests pour les utilitaires partages de l'app ``app``."""

from django.http import HttpRequest
from django.test import SimpleTestCase, override_settings

from app.utils import (
    _is_within_media,
    get_client_ip,
    hash_ip,
    normalize_filename,
    rate_limit,
    remove_accents,
)


class GetClientIpTests(SimpleTestCase):
    """Couvre la detection de l'IP reelle derriere un proxy."""

    def _req(self, **meta):
        request = HttpRequest()
        for k, v in meta.items():
            request.META[k] = v
        return request

    def test_xff_takes_priority(self):
        request = self._req(
            HTTP_X_FORWARDED_FOR="1.2.3.4, 10.0.0.1",
            HTTP_X_REAL_IP="5.6.7.8",
            REMOTE_ADDR="127.0.0.1",
        )
        self.assertEqual(get_client_ip(request), "1.2.3.4")

    def test_x_real_ip_fallback(self):
        request = self._req(HTTP_X_REAL_IP="5.6.7.8", REMOTE_ADDR="127.0.0.1")
        self.assertEqual(get_client_ip(request), "5.6.7.8")

    def test_remote_addr_fallback(self):
        request = self._req(REMOTE_ADDR="127.0.0.1")
        self.assertEqual(get_client_ip(request), "127.0.0.1")

    def test_invalid_ip_falls_through(self):
        request = self._req(
            HTTP_X_FORWARDED_FOR="not-an-ip",
            HTTP_X_REAL_IP="also-not",
            REMOTE_ADDR="127.0.0.1",
        )
        self.assertEqual(get_client_ip(request), "127.0.0.1")

    def test_no_ip_returns_unknown(self):
        request = self._req()
        self.assertEqual(get_client_ip(request), "unknown")


class HashIpTests(SimpleTestCase):
    def test_deterministic(self):
        self.assertEqual(hash_ip("1.2.3.4"), hash_ip("1.2.3.4"))

    def test_different_ips_different_hashes(self):
        self.assertNotEqual(hash_ip("1.2.3.4"), hash_ip("1.2.3.5"))

    def test_unknown_returns_empty(self):
        self.assertEqual(hash_ip("unknown"), "")
        self.assertEqual(hash_ip(""), "")

    def test_custom_salt(self):
        with override_settings(SECRET_KEY="other"):
            self.assertNotEqual(hash_ip("1.2.3.4", salt="a"), hash_ip("1.2.3.4", salt="b"))


class NormalizeFilenameTests(SimpleTestCase):
    def test_basic(self):
        self.assertEqual(normalize_filename("Hello World"), "hello-world")

    def test_accents_and_spaces(self):
        # espaces et caracteres speciaux remplaces par "-"
        # les accents sont aussi remplaces (cohérent avec le helper de PDF)
        self.assertEqual(normalize_filename("  Hello  World  "), "hello-world")
        self.assertEqual(normalize_filename("Cafe-Croissant"), "cafe-croissant")

    def test_special_chars_replaced(self):
        self.assertEqual(normalize_filename("foo/bar:baz"), "foo-bar-baz")

    def test_max_length(self):
        long = "a" * 200
        self.assertLessEqual(len(normalize_filename(long)), 100)

    def test_empty_fallback(self):
        out = normalize_filename("")
        self.assertTrue(out.startswith("file_"))


class IsWithinMediaTests(SimpleTestCase):
    @override_settings(MEDIA_ROOT="/var/media")
    def test_inside(self):
        self.assertTrue(_is_within_media("/var/media/sub/file.pdf"))

    @override_settings(MEDIA_ROOT="/var/media")
    def test_traversal_blocked(self):
        # startswith piège : /var/media_evil commence par /var/media
        self.assertFalse(_is_within_media("/var/media_evil/file.pdf"))

    @override_settings(MEDIA_ROOT="/var/media")
    def test_outside(self):
        self.assertFalse(_is_within_media("/etc/passwd"))


class RemoveAccentsTests(SimpleTestCase):
    def test_strips_accents(self):
        self.assertEqual(remove_accents("Héllo Wörld"), "Hello World")

    def test_empty(self):
        self.assertEqual(remove_accents(""), "")
        self.assertEqual(remove_accents(None), "")


class RateLimitTests(SimpleTestCase):
    """Test du helper rate_limit. Utilise le LocMemCache par defaut."""

    def setUp(self):
        from django.core.cache import cache

        cache.clear()

    def _req(self, ip="1.2.3.4"):
        request = HttpRequest()
        request.META["REMOTE_ADDR"] = ip
        return request

    def test_first_call_allowed(self):
        allowed, current, limit = rate_limit(self._req(), "test_action", 5, 60)
        self.assertTrue(allowed)
        self.assertEqual(current, 1)
        self.assertEqual(limit, 5)

    def test_blocks_after_max(self):
        for _ in range(5):
            rate_limit(self._req(), "test_action", 5, 60)
        allowed, current, limit = rate_limit(self._req(), "test_action", 5, 60)
        self.assertFalse(allowed)
        self.assertGreater(current, limit)

    def test_separate_actions_independent(self):
        for _ in range(5):
            rate_limit(self._req(), "action_a", 5, 60)
        # action_b doit toujours passer
        allowed, _, _ = rate_limit(self._req(), "action_b", 5, 60)
        self.assertTrue(allowed)

    def test_separate_ips_independent(self):
        for _ in range(5):
            rate_limit(self._req(ip="1.1.1.1"), "shared", 5, 60)
        # IP differente doit passer
        allowed, _, _ = rate_limit(self._req(ip="2.2.2.2"), "shared", 5, 60)
        self.assertTrue(allowed)
