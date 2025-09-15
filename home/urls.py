from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("presentation/", views.presentation, name="presentation"),
    path("marches-publics/", views.marches_publics, name="marches_publics"),
    path("mobilite/", views.mobilite, name="mobilite"),
    path("habitat/", views.habitat, name="habitat"),
    path("collecte-dechets/", views.collecte_dechets, name="collecte_dechets"),
    path("encombrants/", views.encombrants, name="encombrants"),
    path("dechetteries/", views.dechetteries, name="dechetteries"),
    path(
        "maisons-sante-pluridisciplinaires/", views.maisons_sante, name="maisons_sante"
    ),
    path("mutuelle-intercommunautaire/", views.mutuelle, name="mutuelle"),
    path("plui/", views.plui, name="plui"),
    path("projet-plui/", views.projet_plui, name="projet_plui"),
    # Équipe administrative & technique
    path("equipe/", views.equipe, name="equipe"),
    # Mentions légales
    path("mentions-legales/", views.mentions_legales, name="mentions_legales"),
    # Politique de confidentialité
    path(
        "politique-confidentialite/",
        views.politique_confidentialite,
        name="politique_confidentialite",
    ),
    # Politique de cookies
    path("politique-cookies/", views.cookies, name="cookies"),
    # Plan du site
    path("plan-du-site/", views.plan_du_site, name="plan_du_site"),
    # Accessibilité
    path("accessibilite/", views.accessibilite, name="accessibilite"),
    # Médi@'pass
    path("mediapass/", views.mediapass, name="mediapass"),
    # Parc Naturel Régional de l'Avesnois
    path("pnra/", views.pnra, name="pnra"),
    # Tourisme en Avesnois
    path("tourisme/", views.tourisme, name="tourisme"),
    # Documents PLUi
    path("documents-plui/", views.documents_plui, name="documents_plui"),
    path("test-email/", views.test_email, name="test_email"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
