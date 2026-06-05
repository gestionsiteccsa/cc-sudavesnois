import logging
import logging.handlers

from django.core.cache import cache
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse

from search.models import SearchConfigModel
from search.services import SearchLogger, SearchService, URLValidatorService


class SearchConfigModelTest(TestCase):
    def setUp(self):
        cache.clear()

    def test_singleton_creation(self):
        config = SearchConfigModel.get_config()
        self.assertEqual(config.pk, 1)
        self.assertEqual(config.min_query_length, 2)
        self.assertEqual(config.max_query_length, 200)
        self.assertEqual(config.results_per_page, 10)

    def test_singleton_enforced(self):
        config1 = SearchConfigModel.get_config()
        config2 = SearchConfigModel.get_config()
        self.assertEqual(config1.pk, config2.pk)

    def test_save_always_pk_1(self):
        config = SearchConfigModel.get_config()
        config.min_query_length = 5
        config.save()
        config.refresh_from_db()
        self.assertEqual(config.pk, 1)
        self.assertEqual(config.min_query_length, 5)

    def test_str(self):
        config = SearchConfigModel.get_config()
        self.assertEqual(str(config), "Configuration de recherche")


class URLValidatorServiceTest(TestCase):
    def test_valid_relative_url(self):
        self.assertTrue(URLValidatorService.is_safe("/presentation/"))

    def test_valid_absolute_url(self):
        self.assertTrue(URLValidatorService.is_safe("https://example.com/page/"))

    def test_dangerous_javascript(self):
        self.assertFalse(URLValidatorService.is_safe("javascript:alert(1)"))

    def test_dangerous_data(self):
        self.assertFalse(URLValidatorService.is_safe("data:text/html,<h1>test</h1>"))

    def test_dangerous_vbscript(self):
        self.assertFalse(URLValidatorService.is_safe("vbscript:msgbox"))

    def test_dangerous_file(self):
        self.assertFalse(URLValidatorService.is_safe("file:///etc/passwd"))

    def test_empty_url(self):
        self.assertTrue(URLValidatorService.is_safe(""))

    def test_none_url(self):
        self.assertTrue(URLValidatorService.is_safe(None))

    def test_case_insensitive_dangerous(self):
        self.assertFalse(URLValidatorService.is_safe("JavaScript:alert(1)"))
        self.assertFalse(URLValidatorService.is_safe("DATA:text/html,test"))


class SearchServiceTest(TestCase):
    def setUp(self):
        cache.clear()
        self.config = SearchConfigModel.get_config()

    def test_query_too_short(self):
        result = SearchService.execute("a", self.config)
        self.assertIsNone(result)

    def test_empty_query(self):
        result = SearchService.execute("", self.config)
        self.assertIsNone(result)

    def test_whitespace_only_query(self):
        result = SearchService.execute("   ", self.config)
        self.assertIsNone(result)

    def test_query_truncated_to_max(self):
        long_query = "a" * 300
        result = SearchService.execute(long_query, self.config)
        self.assertIsNotNone(result)
        self.assertEqual(len(result["query"]), 200)

    def test_valid_query_returns_structure(self):
        result = SearchService.execute("test", self.config)
        self.assertIsNotNone(result)
        self.assertIn("query", result)
        self.assertIn("results", result)
        self.assertIn("count", result)

    def test_min_query_length_respected(self):
        self.config.min_query_length = 3
        self.config.save()
        result = SearchService.execute("ab", self.config)
        self.assertIsNone(result)
        result = SearchService.execute("abc", self.config)
        self.assertIsNotNone(result)


@override_settings(TESTING=True)
class SearchViewTest(TestCase):
    def setUp(self):
        cache.clear()

    def test_search_page_loads(self):
        response = self.client.get(reverse("search"))
        self.assertEqual(response.status_code, 200)

    def test_search_page_contains_form(self):
        response = self.client.get(reverse("search"))
        self.assertContains(response, 'role="search"')

    def test_search_with_empty_query(self):
        response = self.client.get(reverse("search"), {"q": ""})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["count"], 0)

    def test_search_with_short_query(self):
        response = self.client.get(reverse("search"), {"q": "a"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["count"], 0)
        self.assertIn("too_short", response.context)

    def test_search_with_valid_query(self):
        response = self.client.get(reverse("search"), {"q": "test"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("results", response.context)
        self.assertIn("count", response.context)

    def test_search_strips_whitespace(self):
        response = self.client.get(reverse("search"), {"q": "  test  "})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["query"], "test")

    def test_search_xss_protection(self):
        response = self.client.get(
            reverse("search"), {"q": "<script>alert('xss')</script>"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "<script>alert")

    def test_search_pagination(self):
        response = self.client.get(reverse("search"), {"q": "test", "page": "1"})
        self.assertEqual(response.status_code, 200)

    def test_search_invalid_page(self):
        response = self.client.get(reverse("search"), {"q": "test", "page": "abc"})
        self.assertEqual(response.status_code, 200)

    def test_search_uses_search_config(self):
        config = SearchConfigModel.get_config()
        config.results_per_page = 5
        config.save()
        response = self.client.get(reverse("search"), {"q": "test"})
        self.assertEqual(response.status_code, 200)


@override_settings(TESTING=True)
class SearchRateLimitTest(TestCase):
    def setUp(self):
        cache.clear()

    @override_settings(TESTING=False)
    def test_rate_limit_allows_normal_usage(self):
        for _ in range(5):
            response = self.client.get(reverse("search"), {"q": "test"})
            self.assertEqual(response.status_code, 200)

    @override_settings(TESTING=False)
    def test_rate_limit_blocks_excessive_usage(self):
        response = None
        for i in range(31):
            response = self.client.get(reverse("search"), {"q": f"test{i}"})
        self.assertEqual(response.status_code, 429)


class SearchLoggerTest(TestCase):
    def setUp(self):
        cache.clear()

    def test_log_search(self):
        with self.assertLogs("search.services", level="INFO") as cm:
            SearchLogger.log("test query", 5)
        self.assertTrue(any("test query" in msg for msg in cm.output))

    def test_log_truncates_long_queries(self):
        long_query = "a" * 300
        with self.assertLogs("search.services", level="INFO") as cm:
            SearchLogger.log(long_query, 0)
        self.assertTrue(any("aaa" in msg for msg in cm.output))

    def test_log_does_not_log_empty(self):
        import logging as _logging

        class ListHandler(_logging.Handler):
            def __init__(self):
                super().__init__()
                self.records = []

            def emit(self, record):
                self.records.append(record)

        handler = ListHandler()
        _logger = _logging.getLogger("search.services")
        _logger.addHandler(handler)
        _logger.setLevel(_logging.INFO)
        SearchLogger.log("", 0)
        self.assertEqual(len(handler.records), 0)
        _logger.removeHandler(handler)


class SearchFiltersTest(TestCase):
    def test_highlight_basic(self):
        from home.templatetags.search_filters import highlight

        result = highlight("Bonjour le monde", "monde")
        self.assertIn("<mark", str(result))
        self.assertIn("monde", str(result))

    def test_highlight_case_insensitive(self):
        from home.templatetags.search_filters import highlight

        result = highlight("Bonjour le Monde", "monde")
        self.assertIn("<mark", str(result))

    def test_highlight_empty_query(self):
        from home.templatetags.search_filters import highlight

        result = highlight("Bonjour le monde", "")
        self.assertEqual(result, "Bonjour le monde")

    def test_highlight_empty_text(self):
        from home.templatetags.search_filters import highlight

        result = highlight("", "test")
        self.assertEqual(result, "")

    def test_highlight_none_text(self):
        from home.templatetags.search_filters import highlight

        result = highlight(None, "test")
        self.assertIsNone(result)

    def test_highlight_xss_protection(self):
        from home.templatetags.search_filters import highlight

        result = highlight("<script>alert(1)</script>", "script")
        self.assertNotIn("<script>", str(result))

    def test_split_words_basic(self):
        from home.templatetags.search_filters import split_words

        result = split_words("bonjour le monde")
        self.assertEqual(result, ["bonjour", "le", "monde"])

    def test_split_words_empty(self):
        from home.templatetags.search_filters import split_words

        result = split_words("")
        self.assertEqual(result, [])

    def test_split_words_none(self):
        from home.templatetags.search_filters import split_words

        result = split_words(None)
        self.assertEqual(result, [])
