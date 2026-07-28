# Changelog

## [Non publié]

### Ajouté (28/07/2026)
- **Page Changelog** : `/adminccsa/changelog/` avec rendu professionnel du CHANGELOG.md (markdown-it-py, badges par type, dark mode).
- **Mode debug** : `/adminccsa/statistiques/?debug=1` avec panneau de diagnostic complet (dossier, fichiers, middleware, pipeline GeoIP/device/hash).
- **Sélecteur de date** : possibilité de choisir une date précise via un calendrier dans les statistiques.
- **Carte visiteurs (IP)** : liste des IP uniques avec drapeau du pays, nom du pays et nombre de pages vues.
- **Liens cliquables** : les URLs des pages les plus visitées sont maintenant des liens.
- **Conformité RGPD** : stockage IP en clair (avec information des visiteurs), rétention automatique 1 an, commande `python manage.py supprimer_ip <IP>` pour le droit à l'oubli.
- **Documentation** : section Analytics dans le README.md.

### Corrigé (28/07/2026)
- **Analytics** : les statistiques de visites ne s'enregistraient pas à cause d'un buffer mémoire jamais écrit sur le disque.
  - Remplacement du buffer (`_buffer`, `FLUSH_EVERY=10`) par une écriture directe en mode append (format JSON Lines `.jsonl`).
  - Création automatique du dossier `analytics_data/` au démarrage de Django (`AppConfig.ready()`).
  - Suppression des anciens fichiers `.summary.json` (le résumé est calculé à la volée à la lecture).
  - Compatibilité ascendante : lecture des anciens fichiers `.json` (format tableau) et du nouveau format `.jsonl`.
  - Correction de l'ordre des routes : `telecharger/tout/` passait avant `<str:day_str>` (résolvait "Date invalide").
  - Logging des erreurs middleware au lieu du `except Exception: pass` silencieux.
  - Import `geoip2` sécurisé avec `try/except ImportError` pour éviter un plantage silencieux.

### Ajouté (03/06/2025)
- Documentation : mise à jour de la date de dernière mise à jour dans le README.md.
- Ajout d'une section "Nouveautés et améliorations récentes" pour le 03/06/2025 dans le README.md.
- Préparation du changelog pour publication.

### Ajouté (03/06/2025)
- Documentation : ajout dans `README.md` d’une section détaillant l’audit de sécurité Python avec Bandit, incluant la commande recommandée pour exclure les dossiers `migrations` et les fichiers `tests.py`.
- Explications ajoutées sur les bonnes pratiques d’exclusion pour Bandit et lien vers la documentation officielle.

- Création d’une page Accessibilité moderne et conforme RGAA 4.1 (`home/templates/home/accessibilite.html`) :
  - Introduction, conformité, fonctionnalités d’accessibilité, aide à l’utilisation, contact, voies de recours, date de mise à jour
  - Design responsive, compatible dark mode, emojis pour la lisibilité
- Ajout de la vue `accessibilite` dans `home/views.py`
- Ajout de la route `/accessibilite/` dans `home/urls.py`
- Ajout du lien « Accessibilité » dans le footer (`templates/footer.html`)
- Mise à jour du README.md pour documenter la page et la démarche RGAA

### Ajouté (30/05/2025)
- Intégration complète de TailwindCSS en mode build local (npm, version 3.4.3) pour la gestion des styles.
- Création et configuration du fichier `tailwind.config.js` avec chemins exhaustifs pour tous les templates Django, couleurs personnalisées (`primary`, `secondary`) et police sans-serif personnalisée.
- Suppression du CDN Tailwind (`cdn.tailwindcss.com`) dans `base.html` au profit d'un fichier CSS généré localement (`static/css/output.css`).
- Ajout du fichier source `static/css/input.css` contenant les directives `@tailwind base;`, `@tailwind components;`, `@tailwind utilities;`.
- Mise à jour du template principal pour charger le CSS généré via `{% static 'css/output.css' %}`.
- Ajout d'une documentation détaillée dans le README pour l'installation et l'utilisation de TailwindCSS en local, incluant la procédure pour Windows/PowerShell et le déploiement sur o2switch.

### Modifié (30/05/2025)

### Modifié (30/05/2025)
- Optimisation SEO et conformité RGAA renforcée sur `bureau_communautaire/templates/bureau_communautaire/elus.html` :
    - Ajout d'un bloc `{% block title %}` dynamique et d'une meta description personnalisée pour un meilleur référencement.
    - Structure HTML5 sémantique (main, section, h1, h2, h3, article) clarifiée.
    - Amélioration de l'accessibilité clavier (focus visible sur les boutons, contrastes adaptés, messages d'alerte accessibles pour documents non disponibles).
    - Vérification et fallback pour les images d'élus (texte alternatif ou message en cas d'absence de photo).
    - Ajout de rôles ARIA (`role="alert"`, `aria-live="polite"`) sur les messages d'erreur.
    - Recommandations : ajouter des balises Open Graph, compléter les attributs `alt` sur toutes les images, ajouter `role="main"` et `aria-label` sur les sections principales, vérifier la cohérence des titres et la présence d'un lien d'évitement dans le template de base.

### Modifié (30/05/2025)
- Section Application mobile (MyMobi) : image centrée, présentation modernisée, alignement et espacement optimisés des boutons App Store et Google Play.
- Mise à jour des coordonnées, numéros de téléphone et horaires d'ouverture dans `maisons-sante.html` pour plusieurs établissements.
- Modification des contacts RGPD/DPO et adresses mail dans `politique-confidentialite.html`.
- Correction et harmonisation des liens dans le menu principal (`header.html`) : tous les liens utilisent désormais les bons namespaces et noms de routes Django.
- Mise à jour du plan du site (`plan-du-site.html`) pour refléter la structure réelle des routes et corriger les liens (accueil, conseil communautaire, rapports d'activité).
- Menu mobile : génération dynamique de la liste des communes membres avec boucle sur l'objet `cities` et utilisation du namespace `communes-membres`.
- Ajout des liens manquants (présentation, compétences, équipe, semestriels, etc.) et correction des liens factices.
- Tous les liens du menu Publications utilisent maintenant les bons namespaces (`journal`, `semestriels`, `comptes_rendus`, `rapports_activite`).


### Corrigé
- Gestion d’indisponibilité des fichiers lors de la modification d’un journal : si le document PDF ou la couverture n’existe plus sur le serveur lors de l’édition, un message d’avertissement s’affiche (« Fichier indisponible ») au lieu de provoquer une erreur. Correction appliquée dans la vue `edit_journal`.
- Gestion d’erreur conviviale : lorsqu’aucune commune ne correspond au slug demandé dans la vue `commune`, une page informative s’affiche au lieu d’une 404. Ajout du template `communes_membres/commune_no_ville.html` avec message explicite pour l’utilisateur.
- Correction RGAA et UX : affichage d’un message d’erreur accessible (« Document non disponible ») si un document du Bureau Communautaire est manquant ou supprimé physiquement. Le message est conforme RGAA (role="alert", aria-live, contraste) et remplace le lien de téléchargement dans `bureau_communautaire/views.py` et `bureau_communautaire/templates/bureau_communautaire/elus.html`.
- Correction d’un lint : suppression d’un import inutile (`settings`) dans `bureau_communautaire/views.py`.


### Technique / Maintenance
- Attention : warning Django sur l’utilisation du templatetag `filters` dans plusieurs apps (`bureau_communautaire` et `communes_membres`).
- Attention : modèle `ActeLocal.commune` utilise `ForeignKey(unique=True)` (préférer `OneToOneField`).
- Attention : champ `RapportActivite.year` utilise `max_length` sur un `IntegerField` (inutile, à retirer).

### Ajouté
- Création d'une page moderne et accessible pour la politique de confidentialité (`home/templates/home/politique-confidentialite.html`) : design harmonisé, sections numérotées, conformité RGPD, dark mode, accessibilité renforcée.
- Création d'une page complète pour la politique de gestion des cookies (`home/templates/home/cookies.html`) : design harmonisé, sections numérotées, explications pédagogiques, conformité CNIL, dark mode, accessibilité.
- Ajout de la route `/politique-cookies/` (optimisée SEO) dans `home/urls.py` pour la page de gestion des cookies.
- Ajout du lien « Politique de cookies » dans le footer (`templates/footer.html`).

### Modifié
- Vue personnalisée de déconnexion (`logout_view`) dans `accounts/views.py` avec message de succès et redirection vers la page de connexion.
- Route `/logout/` utilisant désormais la vue personnalisée (plus de LogoutView générique) dans `accounts/urls.py`.
- Bouton "Ajouter un membre" sous chaque ville dans la page admin des villes du Conseil Communautaire.

### Modifié
- Amélioration UX de la page admin des villes (`conseil_communautaire/templates/conseil_communautaire/admin_cities_list.html`) : suppression de l'effet accordéon, affichage direct des membres sous chaque ville, design modernisé et plus intuitif.
- Correction et harmonisation des noms de routes dans `conseil_communautaire/urls.py` et dans toutes les redirections de vues (`admin_list_cities` au lieu de `admin_ville_list` ou `conseil:...`).
- Correction de toutes les redirections dans les vues `conseil_communautaire/views.py` pour pointer vers les bons noms de routes après ajout, modification ou suppression de ville/membre.
- Amélioration de la cohérence UX sur l'ensemble des pages admin : boutons, navigation, affichage des listes.
- Modernisation des boutons et de la navigation dans la gestion des actes locaux (`communes_membres/templates/communes_membres/admin_acte_list.html`).

### Corrigé
- Correction d'un bug NoReverseMatch lors des redirections après ajout/modif/suppression d'actes locaux (utilisation du bon nom de route `admin_acte_list`).
- Correction des liens de navigation dans la sidebar admin (`templates/admin_sidebar.html`) pour pointer vers les bons noms de routes.
- Correction de multiples incohérences de nommage dans les routes et les vues du module Conseil Communautaire.

### Supprimé
- Suppression de l'effet accordéon JS/CSS sur la page admin des villes du Conseil Communautaire (tout est affiché directement).


### Ajouté
- Documentation sur la compatibilité avec le mode nuit dans `docs/dark-mode-compatibility.md`
- Nouvelle page pour les comptes-rendus des conseils communautaires
- Fichier CSS pour la page des comptes-rendus avec compatibilité mode nuit
- Nouvelle page de présentation de la communauté de communes
- Fichier CSS pour la page de présentation avec animations et compatibilité mode nuit
- Nouvelle page des compétences de la communauté de communes
- Fichier CSS pour la page des compétences avec animations et compatibilité mode nuit
- Organigramme interactif pour la page "Équipe administrative & technique"
- Fichiers CSS et JavaScript pour l'organigramme interactif avec compatibilité mode nuit
- Possibilité de basculer entre la version interactive et la version statique de l'organigramme
- Refonte complète des pages d’administration du module journal (ajout, édition, suppression, liste) : design harmonisé, accessibilité RGAA, feedback utilisateur (messages de succès/erreur, icônes, aria-live).
- Intégration du système de messages Django dans tous les formulaires d’administration du journal.
- Ajout de l’entrée « Journal Mon Sud Avesnois » dans le menu mobile.
- Mise à jour du README.md pour documenter ces évolutions.
- Rappel : le script `check_before_commit.py` vérifie la qualité, la sécurité et l’accessibilité du code (voir README-check-before-commit.md).

### Modifié
- Amélioration de la compatibilité avec le mode nuit pour la page des élus (`home/templates/home/elus.html`)
- Amélioration de la compatibilité avec le mode nuit pour la page des communes (`home/templates/home/commune.html`)
- Ajout de styles spécifiques pour le mode nuit dans `static/css/elus.css`
- Mise à jour des routes dans `urls.py` pour inclure la page des comptes-rendus
- Ajout de la vue `comptes_rendus` dans `views.py`
- Ajout de la vue `presentation` dans `views.py`
- Ajout de la vue `competences` dans `views.py`
- Correction des problèmes de lint dans `urls.py` (espaces en fin de ligne et lignes trop longues)
- Mise à jour du README.md pour inclure les nouvelles fonctionnalités et améliorations
- Refactorisation et stylisation complète des templates d'administration du module Conseil Communautaire avec Tailwind CSS et widget_tweaks (formulaires villes et membres)
- Ajout d'une page d'administration pour la liste des membres (élus) avec actions Modifier/Supprimer
- Correction des problèmes de lint (lignes trop longues) dans `views.py` et `urls.py`
- Mise à jour des routes : le module Conseil Communautaire est désormais accessible sous `/conseil/` (voir `app/urls.py` et `conseil_communautaire/urls.py`)
- Chemin d'accueil du Conseil Communautaire simplifié (`path('', views.conseil, ...)`)
- Amélioration de la cohérence UX et accessibilité sur toutes les pages admin Conseil Communautaire

### Corrigé
- Problèmes de contraste en mode nuit sur les pages des élus et des communes
- Visibilité des textes et des éléments d'interface en mode nuit
- Erreur de lint dans `urls.py` (ligne trop longue)

## Août 2025

### Technique / Maintenance
- remplacer psycopg2 par psycopg2-binary pour éviter la compilation (pg_config) sur o2switch

## Septembre 2025

### Modifié
- file size
- page 404
- menu & pages
- mediapass..., add dev-eco
- css
- ajout formulaire plui

### Corrigé
- ulrs.py
- Responsivité du footer sur mobile
- Corriger les liens PDF des rapports d'activité

### Supprimé
- Explications

## Octobre 2025

### Ajouté
- slash url

### Modifié
- requirements.txt
- requirements.txt delete psycopg2
- requirements.txt delete psycopg2
- request
- openssl
- requirements
- urls slash
- plan du site
- **security** : Suppression des console.log du code production

### Corrigé
- slash url
- delete slash
- bug ordre url
- ortographe
- **security** : Remplacement des print() par logging sécurisé
- **security** : Bureau com
- **security** : Ajout rate limiting sur login et headers de sécurité manquants

### Supprimé
- requirements.txt delete psycopg2
- python windows

## Novembre 2025

### Modifié
- img faebook link
- numéro
- organi
- mail & menu

## Décembre 2025

### Ajouté
- remplacer le bouton unique par 3 boutons pour les comptes-rendus
- link pv
- **presentation** : ajout de liens vers les pages des communes
- agenda lien, plui liens
- analytic
- **elus** : permettre la liaison a plusieurs commissions
- **comptes_rendus** : amélioration affichage conseils - lieu optionnel, filtre dates passées, design timeline professionnel, accessibilité améliorée, responsive optimisé

### Modifié
- journal
- link
- og
- adresse habitat, calendrier
- ADIL

### Corrigé
- orthographe email
- orthog
- analytic del tagmanager
- img og
- texte + date collect
- **elus** : corriger l'affichage des commissions multiples

## Janvier 2026

### Ajouté
- **habitat** : add download icon and leaflet PDF to habitat page
- **a11y** : intégration de la déclaration d'accessibilité officielle RGAA
- **conseil** : intégration calendrier prochains conseils sur page conseil communautaire
- **admin** : refonte complète du dashboard et de la navigation admin
- **home** : ajouter page Kit de logos pour prêt de matériel

### Modifié
- name kit

### Corrigé
- habitat
- nb caract
- **a11y** : Corrections RGAA 4.1.2 - Score 93%
- **accessibility** : corrections RGAA sur les pages PLUI et ajout du rapport d'audit
- link
- suppression des erreurs console en production
- **accessibility** : affichage des icônes en mode contraste élevé
- **a11y** : corrections RGAA page kit-logos
- ajout load static manquant page kit-logos

### Performances
- optimisation Lighthouse - chargement non-bloquant des ressources

### Supprimé
- Prise rendez-vous GUH

### Technique / Maintenance
- **accessibilite** : amélioration du contraste RGAA et nettoyage

## Février 2026

### Ajouté
- **home** : amélioration accessibilité et conformité RGAA des pages kit-logos et guide-eco-citoyen
- **home** : amélioration accessibilité et conformité RGAA des pages kit-logos et guide-eco-citoyen - Amélioration des textes alternatifs des images pour une meilleure description - Remplacement des aria-label redondants par aria-describedby avec descriptions uniques - Ajout d'informations sur le format et la taille des fichiers téléchargeables - Optimisation de la hiérarchie des titres (h2 plus descriptifs) - Ajout des dimensions d'image pour éviter les décalages de mise en page (CLS) - Conformité RGAA niveau AA et WCAG 2.1 niveau AA
- linktree app with full CRUD, RGAA compliance, and comprehensive tests
- **backup** : Ajoute système de sauvegarde du site complet
- Ajout de l'application Partenaires avec CRUD complet
- **partenaires** : ajout du système de catégories avec sections Normal/Subvention
- ajout du téléchargement PDF des calendriers de collecte du verre
- modification affichage des conseils communautaires
- redesign interface admin conseils + tri décroissant
- redesign admin conseils avec tableau et pagination
- redesign PDF calendrier verre avec mode visualisation
- .env.example with configuration template
- YouTube and Instagram social media icons to header and footer

### Modifié
- kit logo
- **header** : transforme le menu 'Nos partenaires' en lien direct
- **home** : suppression des pages PNRA et Tourisme obsolètes

### Corrigé
- correction lien dans le header
- update URL reference in admin from /rejoignez-nous to /nos-liens/
- function elu
- Correction encodage UTF-8 requirements.txt - Ajout Markdown==3.10.2
- Suppression des dépendances Windows (pywin32) du requirements.txt
- **partenaires** : correction tri alphabétique avec accents et alt images accessibles
- correction des erreurs JavaScript et affichage du sous-menu
- utilisation du fichier JS non minifié pour éviter les erreurs
- affichage des jours en français dans le PDF
- mise à jour de l'adresse dans le PDF
- suppression des puces dans la liste des dates de collecte

### Sécurité
- correction des vulnérabilités de sécurité

### Supprimé
- migrations

### Technique / Maintenance
- ajustement espacement et tailles police PDF calendrier verre
- update title of upcoming council meetings section

## Mars 2026

### Ajouté
- Intégration du système de recherche global avec django-watson
- Ajout des modèles manquants et amélioration visuelle de la recherche
- Refonte design page recherche + barre recherche header mobile
- Ajout des URLs dans les résultats de recherche pour tous les modèles
- Bouton recherche header + optimisation RGAA et mobile
- **search** : Amélioration complète du système de recherche avec Watson
- **search** : Création app dédiée 'search' avec modèle SearchConfig

### Corrigé
- Correction positionnement bouton recherche et loupe
- Suppression des balises HTML dans les résultats de recherche
- **competences** : correction affichage titre compétence is_big
- **accessibility** : amélioration de l'accessibilité WCAG 2.2 AA
- **accessibility** : corrige les erreurs WCAG identifiées
- **accessibility** : augmente la taille des cibles tactiles
- **accessibility** : correction RGAA - SVG et contrastes
- **accessibility** : correction des contrastes sur fond secondary et footer
- **accessibility** : retour au texte blanc sur les boutons verts
- (texte)
- **admin** : corrige la syntaxe des attributs SVG dans la sidebar admin

### Performances
- **sql** : réduit drastiquement les requêtes N+1 et ajoute cache

## Avril 2026

### Ajouté
- ajout gestion statut page bureau-communautaire
- ctg
- **ctg** : ajoute lightbox pour image cliquable
- **commissions** : lien membres-commissions avec accordéon accessible
- **commissions** : affiche Vice-présidents et ordre Prénom Nom
- add explanatory text under transferred competences section
- img
- **conseil-communautaire** : affichage des photos et noms des conseillers avec lightbox accessible
- ajout photo membres conseil + optimisation page publique
- ajout du support des images webp pour les élus
- modernise admin liste services avec drag & drop, stats, toggle vue et optimisation SQL
- support multi-PDF par conseil avec renommage personnalisé

### Modifié
- design elu
- **bureau-communautaire** : redesign cartes élus avec photos en bulle et corrections accessibilité RGAA
- remove breadcrumb navigation from commune page

### Corrigé
- corrige l'erreur ValueError lors de l'ajout d'un PDF sur un conseil sans fichier existant
- rue saint louis
- **accessibility** : amélioration du contraste et accessibilité RGAA/WCAG AA
- suppression texte répétitif sur page maintenance
- ortho
- bug
- ortho
- url
- link onedrive
- erreur texte
- prochain conseil
- cr
- **header** : Ajoute le lien Compétences dans le menu mobile
- **commissions** : corrige le nombre de VP de 8 à 9
- **conseil_communautaire** : corrige select_related vers prefetch_related pour linked_commission
- **commissions** : inverse ordre affichage vice-président - Nom Prénom
- **commissions** : suppression des effets hover et correction des couleurs
- ortho
- **accessibilité** : corrige contraste mode sombre et attributs dupliqués
- **accessibilité** : corrige HTML, contraste et performance page Journal
- **accessibility** : optimize commune page queries, WCAG AAA compliance, breadcrumb
- **photos** : corrige affichage images élus et ajoute gestion position/zoom

### Performances
- **accessibility** : optimise SQL, contraste AAA et accessibilité selon audit RGAA/WCAG

### Supprimé
- contrainte d'unicité sur les membres du conseil

## Mai 2026

### Ajouté
- ajoute popup Jeu de l'oie avec persistance quotidienne et section sondage
- remplace tableaux horaires déchetteries par une image + icône famille section sondage
- ajoute la page Modification Simplifiée n°1 du PLUi
- **ctg** : ajoute section plan d'actions avec PDF téléchargeable
- ajout competences commissions avec toggle Voir plus dans les cartes VP

### Modifié
- **documents-plui** : remplace le formulaire par un bouton renvoyant vers /plui/#formulaire-modification
- **admin** : redesign UI/UX de toutes les pages d'administration

### Corrigé
- **commissions** : tri alphabétique des commissions/élus/membres et augmentation taille police
- retire plui@ des destinataires email et supprime mention 'Membre titulaire'
- **email-plui** : utilise nepasrepondre@ comme expéditeur et email déclarant en Reply-To
- **mobilite** : corrige accessibilite RGAA et format mobile de la page mobilite
- **accessibilite** : ajoute description textuelle détaillée des horaires dans l'alt de l'image déchetteries
- img ctg
- - img ctg
- ortho
- retire le point après Mme pour les maires femmes
- **titles** : corrige les titres HTML des pages (manquants, erronés, suffixe dupliqué)
- **titles** : corrige les 11 titres restants (doublons CCSA et block.super)
- **critical** : corrige les 5 problemes critiques identifies dans le rapport
- **security** : corrige les 9 problemes haute priorite restants
- **media** : retablit le serveur de fichiers medias en production
- corrige M2 (GA init apres consentement) et M4 (ordre import cache_page)
- **R3** : ajoute indication (nouvelle fenetre) sur les target=_blank
- corrections responsive (audit complet)

### Performances
- corrige C1, H1-H6, H9, H10, H11, H12
- corrige N+1 partenaires et double requetes exists+get

### Documentation
- met à jour README, package.json et tailwind.config.js

### Supprimé
- msp tel fourmies

## Juin 2026

### Ajouté
- ajoute un encadre 'Contacts des elus' sur la page conseil-communautaire avec lien SharePoint
- ajoute visionneuse flipbook interactive pour les journaux PDF
- ajoute trois options de consultation avec tooltips accessibles sur la liste des journaux
- **search** : refactorise la recherche en app dédiée avec rate limiting et accessibilité
- ajoute une section PLUi MS1 sur la page d'accueil avec dates de consultation publique
- remplace GA4 gtag.js par Google Tag Manager GTM-5ZR9PFQX avec consentement RGPD
- remplace toutapprendre.com par Mozaik
- ajoute la page CLÉA+ accessible et responsive
- **clea,mediapass** : accessibilite RGAA/WCAG AA et appel a candidature CLEA
- **header** : ajoute les sous-menus CLEA et Mediapass (desktop + mobile)
- **home** : PR6 - StaticPage: index, contrainte, is_published, timestamps
- **home.data** : PR9 - validation et tri des dates collecte
- **clea** : appel à candidatures en cartes côte à côte avec consultation et téléchargement
- **admin** : Lot 1 quick wins - a11y, contrast, sidebar filter, dashboard stats

### Modifié
- **clea** : aligne l'UI/UX sur habitat.html et corrige l'accessibilité
- **security** : PR2 - helper rate_limit() centralise
- **forms** : PR5 - communes dynamiques, tel stricte, autocomplete
- **bureau_communautaire** : sécurité, perf, qualité de la suite de tests
- **accounts** : UX admin, indexes BDD, génération password, pagination
- **services** : validation SVG, tri automatique, audit, tests complets

### Corrigé
- restaure le CSS du toggle 'Voir plus' des competences VP supprime accidentellement dans 7d8dd5e
- ajoute prefers-reduced-motion et prefers-contrast pour les tooltips
- **search** : corrige l'URL des resultats de recherche pour les communes
- **accessibilite** : corrige 3 non-conformités RGAA sur la page d'accueil
- **accessibilite** : assombrit bg-secondary (#3a4a08) pour contraste WCAG AA 4.5:1
- **accessibilite** : retire style font-display invalide sur le h1 (NC 10.11)
- type img
- **header** : retablit le menu mobile en dropdown sous le header
- **security,perf** : PR1+PR3+PR4 - securite applicative, refactor, cache
- **a11y** : PR7 - RGAA/WCAG 2.2 AA (rel=noopener, plui form, focus)
- **ci** : supprimer paths-ignore (interdit avec paths sur un meme event)
- **ci** : Node 22 + git-auto-commit-action (corrige exit 9)
- **ci** : mise a jour actions/checkout@v5 et setup-node@v5
- **css** : deplacement input.css de staticfiles/ vers static/css/

### Performances
- **css** : minifier output.css via Tailwind CLI --minify (97 KB -> 76 KB)
- **cache** : cache statique 1 an + hash manifest (WhiteNoise)
- **lcp** : preload + fetchpriority high image popup Jeu de l'oie

### Documentation
- **readme** : documenter les scripts npm Tailwind et le build minifie
- **readme** : ajouter procedure de mise a jour en production
- **readme** : adapter la procedure de deploiement aux serveurs sans npm

### Technique / Maintenance
- accessibilite habitat, refactor clea et ajustements divers
- wip snapshot avant audit home/
- **home,app** : PR8 - tests pour app.utils, PLUiForm, fix obsoletes
- **deps** : PR10 - requirements-prod.txt minimal + audit CVE
- **home** : PR11 - suppression code mort
- **home** : PR12 - correction tests obsoletes suite aux changements
- **css** : workflow GitHub Actions pour regenerer output.min.css
- sessions DB, suppression code mort home/, fix SVG admin_base

## Juillet 2026

### Ajouté
- **plui** : add settings admin to manage section visibility
- **communes-membres** : add public listing page with cards (TDD + SOLID)
- **admin** : page verification des pages HTTP (200/404/500)
- **admin** : ajoute page de consultation des logs dans /adminccsa/logs
- **analytics** : ajoute système de statistiques de visites côté serveur
- **analytics** : ajoute cookie visitor_id pour reconnaissance multi-jour
- **analytics** : ajoute géolocalisation IP (GeoIP) avec drapeaux

### Modifié
- **admin** : remplace page verification-pages par commande check_pages

### Corrigé
- **clea** : regen manifest staticfiles apres renommage PDFs
- **mobilite** : update TAD coordonnees, horaires, et renommage images flyers
- **mobilite** : regen manifest staticfiles apres renommage images flyers
- **mobilite** : correction casse noms images Flyer-Tad pour compatibilite Linux
- **admin** : host Client Django depuis la requete pour eviter DisallowedHost
- **admin** : urllib + cache 5min pour scan pages, abandonne Client Django
- **admin** : ajoute constantes CHECK_PAGES_CACHE_KEY/TTL manquantes
- **admin** : Client Django avec secure=True + host requete, abandonne urllib
- **admin** : retour a requests avec SSL + ThreadPoolExecutor + cache 5min

### Performances
- **admin** : remplace requests.get par Client Django pour scan pages x10 plus rapide

### Documentation
- **readme** : ajoute analytics, logs, check_pages, GeoIP dans la doc
