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
    path("contrat-local-sante/", views.contrat_local_sante, name="contrat_local_sante"),
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
    # Guide Éco-Citoyen
    path("guide-eco-citoyen/", views.guide_eco_citoyen, name="guide_eco_citoyen"),
    # Documents PLUi
    path("documents-plui/", views.documents_plui, name="documents_plui"),
    # Développement économique
    path("developpement-economique/", views.dev_eco, name="dev_eco"),
    # Kit de logos CCSA
    path("kit-logos/", views.kit_logos, name="kit_logos"),
    # Téléchargement calendrier verre PDF
    path(
        "collecte/telecharger-pdf/",
        views.telecharger_calendrier_verre,
        name="telecharger_calendrier_verre"
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
