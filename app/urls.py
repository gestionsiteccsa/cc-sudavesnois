from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path
from django.views.generic import RedirectView, TemplateView
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

from home.sitemaps import CommunesSitemap, JournalSitemap, StaticViewSitemap

sitemaps = {
    "static": StaticViewSitemap,
    "communes": CommunesSitemap,
    "journals": JournalSitemap,
}

urlpatterns = [
    path("ccsa-admin/", admin.site.urls),
    path("", include("home.urls")),
    path("", include("accounts.urls", namespace="accounts")),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    path(
        "robots.txt",
        TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
        name="robots_txt",
    ),
    path("", include("conseil_communautaire.urls")),
    path("", include("journal.urls", namespace="journal")),
    path("", include("bureau_communautaire.urls", namespace="bureau-communautaire")),
    path("", include("communes_membres.urls", namespace="communes-membres")),
    path("", include("commissions.urls", namespace="commissions")),
    path("", include("competences.urls", namespace="competences")),
    path("", include("semestriels.urls", namespace="semestriels")),
    path("", include("comptes_rendus.urls", namespace="comptes_rendus")),
    path("services/", include("services.urls", namespace="services")),
    path("", include("rapports_activite.urls", namespace="rapports_activite")),
    path("", include("contact.urls", namespace="contact")),
    # Redirections pour les URLs courtes
    path(
        "login/",
        RedirectView.as_view(pattern_name="accounts:login"),
        name="login_redirect",
    ),
    path(
        "logout/",
        RedirectView.as_view(pattern_name="accounts:logout"),
        name="logout_redirect",
    ),
    path(
        "register/",
        RedirectView.as_view(pattern_name="accounts:register"),
        name="register_redirect",
    ),
    path(
        "profile/",
        RedirectView.as_view(pattern_name="accounts:profile"),
        name="profile_redirect",
    ),
]

# Dans urls.py
if settings.DEBUG:
    # Mode développement
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
else:
    # Mode production
    urlpatterns += [
        path('static/<path:path>', serve, {'document_root': settings.STATIC_ROOT}),
        path('media/<path:path>', serve, {'document_root': settings.MEDIA_ROOT}),
    ]