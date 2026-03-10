from django.core.management.base import BaseCommand
from home.models import StaticPage


class Command(BaseCommand):
    help = 'Importe les pages statiques pour l\'indexation de recherche'
    
    PAGES = [
        {
            "title": "Accueil",
            "slug": "accueil",
            "url": "/",
            "description": "Page d'accueil de la Communauté de Communes Sud-Avesnois",
            "content": "CCSA Communauté de Communes Sud-Avesnois services communes Féron Wignehies Sassegnies"
        },
        {
            "title": "Présentation",
            "slug": "presentation",
            "url": "/presentation/",
            "description": "Présentation de la CCSA, son territoire et ses communes membres",
            "content": "Présentation territoire communes Sud-Avesnois histoire organisation"
        },
        {
            "title": "Conseil communautaire",
            "slug": "conseil",
            "url": "/conseil/",
            "description": "Conseil communautaire et élus de la CCSA",
            "content": "Conseil communautaire élus représentation démocratie locale"
        },
        {
            "title": "Marchés publics",
            "slug": "marches-publics",
            "url": "/marches-publics/",
            "description": "Informations sur les marchés publics et appels d'offres",
            "content": "Marchés publics appels d'offres consultation fournisseurs achats"
        },
        {
            "title": "Mobilité",
            "slug": "mobilite",
            "url": "/mobilite/",
            "description": "Services de mobilité et transport à la demande",
            "content": "Mobilité transport à la demande TAD bus cars navettes"
        },
        {
            "title": "Habitat",
            "slug": "habitat",
            "url": "/habitat/",
            "description": "Politique habitat et logement sur le territoire",
            "content": "Habitat logement PLH Programme Local de l'Habitat construction"
        },
        {
            "title": "Collecte des déchets",
            "slug": "collecte-dechets",
            "url": "/collecte-dechets/",
            "description": "Informations sur la collecte des déchets et calendriers",
            "content": "Collecte déchets ordures ménagères recyclage tri sélectif"
        },
        {
            "title": "Encombrants",
            "slug": "encombrants",
            "url": "/encombrants/",
            "description": "Service de collecte des encombrants",
            "content": "Encombrants collecte meubles objets volumineux"
        },
        {
            "title": "Déchetteries",
            "slug": "dechetteries",
            "url": "/dechetteries/",
            "description": "Déchetteries du territoire et horaires d'ouverture",
            "content": "Déchetteries déchèterie horaires déchets recyclage"
        },
        {
            "title": "Maisons de santé pluridisciplinaires",
            "slug": "maisons-sante",
            "url": "/maisons-sante/",
            "description": "Maisons de santé et professionnels de santé du territoire",
            "content": "Maisons santé médecins infirmiers professionnels santé"
        },
        {
            "title": "Mutuelle intercommunautaire",
            "slug": "mutuelle",
            "url": "/mutuelle/",
            "description": "Mutuelle intercommunautaire et couverture santé",
            "content": "Mutuelle santé complémentaire couverture soins"
        },
        {
            "title": "Contrat local de santé",
            "slug": "contrat-local-sante",
            "url": "/contrat-local-sante/",
            "description": "Contrat local de santé du territoire",
            "content": "Contrat santé CLS prévention soins accès aux soins"
        },
        {
            "title": "PLUi",
            "slug": "plui",
            "url": "/plui/",
            "description": "Plan Local d'Urbanisme Intercommunal",
            "content": "PLUi urbanisme planification construction règlement"
        },
        {
            "title": "Projet PLUi",
            "slug": "projet-plui",
            "url": "/projet-plui/",
            "description": "Projet de Plan Local d'Urbanisme Intercommunal",
            "content": "Projet PLUi urbanisme évolution territoire"
        },
        {
            "title": "Documents PLUi",
            "slug": "documents-plui",
            "url": "/documents-plui/",
            "description": "Documents du PLUi et demandes de modification",
            "content": "Documents PLUi modification carte zonage règlement"
        },
        {
            "title": "Équipe",
            "slug": "equipe",
            "url": "/equipe/",
            "description": "L'équipe de la Communauté de Communes",
            "content": "Équipe agents salariés direction services"
        },
        {
            "title": "Mentions légales",
            "slug": "mentions-legales",
            "url": "/mentions-legales/",
            "description": "Mentions légales du site",
            "content": "Mentions légales éditeur hébergeur propriété intellectuelle"
        },
        {
            "title": "Politique de confidentialité",
            "slug": "politique-confidentialite",
            "url": "/politique-confidentialite/",
            "description": "Politique de confidentialité et protection des données",
            "content": "Confidentialité RGPD données personnelles protection"
        },
        {
            "title": "Cookies",
            "slug": "cookies",
            "url": "/cookies/",
            "description": "Politique de gestion des cookies",
            "content": "Cookies traceurs consentement navigation"
        },
        {
            "title": "Plan du site",
            "slug": "plan-du-site",
            "url": "/plan-du-site/",
            "description": "Plan du site et navigation",
            "content": "Plan du site navigation arborescence pages"
        },
        {
            "title": "Accessibilité",
            "slug": "accessibilite",
            "url": "/accessibilite/",
            "description": "Déclaration d'accessibilité du site",
            "content": "Accessibilité handicap conformité RGAA"
        },
        {
            "title": "Mediapass",
            "slug": "mediapass",
            "url": "/mediapass/",
            "description": "Service Mediapass et presse locale",
            "content": "Mediapass presse information locale médias"
        },
        {
            "title": "Guide pratique éco-citoyen",
            "slug": "guide-eco-citoyen",
            "url": "/guide-eco-citoyen/",
            "description": "Guide pratique pour un comportement éco-citoyen",
            "content": "Guide éco-citoyen environnement développement durable"
        },
        {
            "title": "Développement économique",
            "slug": "dev-eco",
            "url": "/dev-eco/",
            "description": "Développement économique du territoire",
            "content": "Développement économique entreprises commerces emploi"
        },
        {
            "title": "Kit logos",
            "slug": "kit-logos",
            "url": "/kit-logos/",
            "description": "Kit de logos officiels de la CCSA",
            "content": "Logos charte graphique identité visuelle communication"
        },
    ]
    
    def handle(self, *args, **options):
        count = 0
        for page_data in self.PAGES:
            _, created = StaticPage.objects.get_or_create(
                slug=page_data["slug"],
                defaults=page_data
            )
            if created:
                count += 1
                self.stdout.write(f"  Créé: {page_data['title']}")
            else:
                # Mettre à jour les données existantes
                StaticPage.objects.filter(slug=page_data["slug"]).update(**page_data)
                self.stdout.write(f"  Mis à jour: {page_data['title']}")
        
        self.stdout.write(self.style.SUCCESS(f"\n{count} nouvelles pages créées, {len(self.PAGES) - count} pages mises à jour"))
