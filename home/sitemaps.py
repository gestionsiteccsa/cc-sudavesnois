from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from conseil_communautaire.models import ConseilVille
from journal.models import Journal


class StaticViewSitemap(Sitemap):
    """
    Sitemap pour les vues statiques du site.
    """

    priority = 0.5
    changefreq = "weekly"

    def items(self):
        # Liste de tous les noms d'URL du site
        return [
            "home",
            "elus",
            "conseil",
            "comptes_rendus",
            "presentation",
            "competences",
            "journal",
            "commissions",
            "marches_publics",
            "mobilite",
            "habitat",
            "collecte_dechets",
            "encombrants",
            "dechetteries",
            "maisons_sante",
            "mutuelle",
            "plui",
            "projet_plui",
            "equipe",
            "semestriel",
            "rapports_activite",
            "mentions_legales",
            "politique_confidentialite",
        ]

    def location(self, item):
        return reverse(item)


class CommunesSitemap(Sitemap):
    """
    Sitemap pour les pages de communes.
    """

    priority = 0.7
    changefreq = "monthly"

    def items(self):
        return ConseilVille.objects.all()

    def location(self, obj):
        return reverse("communes-membres:commune", kwargs={"slug": obj.slug})


class JournalSitemap(Sitemap):
    """
    Sitemap pour les publications du journal.
    """

    priority = 0.6
    changefreq = "monthly"

    def items(self):
        return Journal.objects.all()

    def lastmod(self, obj):
        return obj.release_date

    def location(self, obj):
        return reverse("journal:journal_detail", kwargs={"id": obj.id})
