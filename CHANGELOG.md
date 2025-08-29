# Changelog

## [Non publié]

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
