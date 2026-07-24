import time

from django.conf import settings

from analytics.analytics_data import append
from analytics.device_parser import parse_user_agent
from app.utils import get_client_ip, hash_ip

IGNORE_PREFIXES = frozenset(
    {
        "/adminccsa/",
        "/ccsa-admin/",
        "/static/",
        "/media/",
        "/favicon.ico",
        "/robots.txt",
        "/sitemap.xml",
    }
)


class PageTrackingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path_info
        if self._should_skip(path):
            return self.get_response(request)

        start = time.time()
        response = self.get_response(request)
        elapsed = int((time.time() - start) * 1000)

        try:
            ip = get_client_ip(request)
            ua = request.META.get("HTTP_USER_AGENT", "")
            referrer = request.META.get("HTTP_REFERER", "")
            lang = request.META.get("HTTP_ACCEPT_LANGUAGE", "")

            entry = {
                "url": path,
                "status": response.status_code,
                "response_time_ms": elapsed,
                "ip_hash": hash_ip(ip),
                "session_key": request.session.session_key or "",
                "visitor_id": request.COOKIES.get("visitor_id") or None,
                "user_id": request.user.pk if request.user.is_authenticated else None,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "referrer": referrer,
                "language": lang,
                "device": parse_user_agent(ua),
            }
            append(entry)
        except Exception:
            pass

        return response

    def process_exception(self, request, exception):
        pass

    def _should_skip(self, path: str) -> bool:
        for prefix in IGNORE_PREFIXES:
            if path.startswith(prefix):
                return True
        if getattr(settings, "TESTING", False):
            return True
        return False
