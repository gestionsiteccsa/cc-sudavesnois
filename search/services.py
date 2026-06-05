import logging

from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.core.validators import URLValidator

from watson import search as watson

logger = logging.getLogger(__name__)


class URLValidatorService:
    DANGEROUS_PROTOCOLS = ("javascript:", "data:", "vbscript:", "file:")

    @classmethod
    def is_safe(cls, url):
        if not url:
            return True
        url_lower = url.lower().strip()
        if any(url_lower.startswith(p) for p in cls.DANGEROUS_PROTOCOLS):
            return False
        if url.startswith("/"):
            return True
        try:
            URLValidator()(url)
            return True
        except ValidationError:
            return False


class SearchLogger:
    @staticmethod
    def log(query, count):
        if not query:
            return
        truncated = query[:100]
        logger.info("Search query='%s' results=%d", truncated, count)


class SearchService:
    @staticmethod
    def execute(raw_query, config):
        query = raw_query.strip()[: config.max_query_length]
        if len(query) < config.min_query_length:
            return None

        raw_results = watson.search(query)

        validated = [r for r in raw_results if URLValidatorService.is_safe(r.url)]

        SearchLogger.log(query, len(validated))

        paginator = Paginator(validated, config.results_per_page)

        return {
            "query": query,
            "results": validated,
            "count": len(validated),
            "paginator": paginator,
        }


class RateLimitService:
    RATE_LIMIT = 30
    WINDOW_SECONDS = 60

    @classmethod
    def is_allowed(cls, client_ip):
        from django.conf import settings

        if getattr(settings, "TESTING", False):
            return True

        key = f"search_rate:{client_ip}"
        try:
            attempts = cache.get(key, 0)
            if attempts >= cls.RATE_LIMIT:
                return False
            cache.set(key, attempts + 1, cls.WINDOW_SECONDS)
            return True
        except Exception as e:
            logger.error("Rate limit cache error: %s", e)
            return True
