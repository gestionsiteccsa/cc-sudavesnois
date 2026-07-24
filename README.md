# Communauté de Communes Sud-Avesnois (CCSA)

<div align="center">

![Logo CCSA](static/img/logo/Logo_S-A.png)

*Site web institutionnel de la Communauté de Communes Sud-Avesnois*

[![Django](https://img.shields.io/badge/Django-5.1.7-092E20?logo=django)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python)](https://python.org)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.4-06B6D4?logo=tailwindcss)](https://tailwindcss.com/)
[![Code style](https://img.shields.io/badge/Code%20style-PEP%208-4B8BBE)](https://peps.python.org/pep-0008/)
[![Linter](https://img.shields.io/badge/Linter-Flake8-4B8BBE)](https://flake8.pycqa.org/)
[![Licence](https://img.shields.io/badge/Licence-Propriétaire-red)]()

</div>

## Table des matières

- [Présentation](#présentation)
- [Fonctionnalités](#fonctionnalités)
- [Installation](#installation)
- [Utilisation](#utilisation)
- [Structure du projet](#structure-du-projet)
- [Tests](#tests)
- [Accessibilité](#accessibilité)
- [Déploiement](#déploiement)
- [Mise à jour en production](#mise-à-jour-en-production)
- [Documentation](#documentation)
- [Contribuer](#contribuer)

---

## Présentation

La **Communauté de Communes Sud-Avesnois (CCSA)** regroupe **12 communes** du sud de l'Avesnois, représentant environ **26 000 habitants**.

Le site permet aux habitants et usagers d'accéder aux informations et services de la collectivité : présentation des élus, comptes rendus, informations pratiques, collecte des déchets, démarches administratives, etc.

### Applications Django

| Application | Rôle |
|-------------|------|
| `home` | Page d'accueil, pages statiques, recherche |
| `accounts` | Authentification, inscriptions, profil utilisateur |
| `conseil_communautaire` | Conseil communautaire (membres, villes) |
| `bureau_communautaire` | Bureau communautaire (élus, documents officiels) |
| `commissions` | Commissions et compétences associées |
| `communes_membres` | Actes locaux par commune |
| `competences` | Compétences de la CCSA |
| `journal` | Journal d'information |
| `comptes_rendus` | Comptes rendus et procès-verbaux |
| `services` | Guide des services |
| `partenaires` | Annuaire des partenaires |
| `contact` | Gestion des emails de contact |
| `semestriels` | Calendrier semestriel des manifestations |
| `rapports_activite` | Rapports d'activité annuels |
| `linktree` | Page de liens (Linktree) |
| `backup` | Sauvegarde de la base de données |
| `search` | Indexation et recherche full-text |
| `analytics` | Statistiques de visites (serveur, sans base de données) |

---

## Fonctionnalités

### Publiques

- **Présentation du territoire** : communes membres, chiffres clés
- **Guide des services** : annuaire des services de la CCSA
- **Élus et commissions** : présentation du bureau communautaire et des commissions
- **Actes administratifs** : comptes rendus, procès-verbaux, actes locaux
- **Collecte des déchets** : calendrier interactive par commune/rue avec génération PDF
- **Journal d'information** : publications périodiques
- **Page Linktree** : centralisation des liens utiles
- **Recherche full-text** : moteur de recherche interne
- **Formulaire de contact** : envoi de message à la CCSA
- **Plan Local d'Urbanisme (PLUi)** : informations et formulaire de modification

### Administration

- **Dashboard admin** : vue d'ensemble avec statistiques
- **CRUD complet** : gestion de toutes les entités (élus, commissions, services, etc.)
- **Gestion des utilisateurs** : activation/désactivation, création
- **Sauvegarde de la base** : création et téléchargement de backups
- **Statut de page** : activation/désactivation des pages avec message de maintenance
- **Drag & drop** : réordonnancement des services
- **Statistiques de visites** : pages vues, visiteurs uniques, navigateurs, OS, géolocalisation (sans base de données, stockage JSON)
- **Logs applicatifs** : consultation des logs en temps réel dans l'interface admin
- **Vérification des pages** : commande pour tester toutes les pages du site (200, redirections, erreurs)

---

## Installation

### Prérequis

- Python 3.10+
- Node.js 16+ (pour Tailwind CSS)
- Git

### Développement local (SQLite)

```bash
# 1. Cloner le dépôt
git clone https://github.com/gestionsiteccsa/cc-sudavesnois.git
cd cc-sudavesnois

# 2. Créer et activer l'environnement virtuel
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# 3. Installer les dépendances Python
pip install -r requirements.txt

# 4. Copier et configurer les variables d'environnement
cp .env.exemple .env
# Éditer .env avec vos paramètres

# 5. Appliquer les migrations
python manage.py migrate

# 6. Installer les dépendances Node.js (Tailwind CSS) et compiler en mode watch
npm install
npm run watch:css

# 7. Lancer le serveur de développement
python manage.py runserver

# 8. Accéder au site
# http://127.0.0.1:8000
```

### Variables d'environnement (.env)

```env
SECRET_KEY=votre_clé_secrète
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
```

### Production

Adaptez votre fichier `.env` avec les paramètres de votre environnement :

```env
DEBUG=False
SECURE_SSL_REDIRECT=True
ALLOWED_HOSTS=votre-domaine.fr
```

> **Note** : La base de données est configurée via `DATABASE_URL` dans `settings.py`. Par défaut, le projet utilise SQLite. Pour PostgreSQL, installez `psycopg2-binary` et modifiez `settings.py` pour lire les variables d'environnement appropriées.

---

## Utilisation

### Commandes utiles

```bash
# Collecter les fichiers statiques
python manage.py collectstatic

# Créer les migrations
python manage.py makemigrations

# Appliquer les migrations
python manage.py migrate

# Créer un superutilisateur
python manage.py createsuperuser

# Reconstruire l'index de recherche
python manage.py buildwatson

# Créer une sauvegarde
python manage.py create_backup

# Vérifier que toutes les pages répondent (200, redirections, erreurs)
python manage.py check_pages

# Voir toutes les pages, y compris celles en OK
python manage.py check_pages --all

# Vérifier sur le domaine de production
python manage.py check_pages --base-url https://cc-sudavesnois.fr

# Télécharger la base de géolocalisation IP (GeoIP)
# --mirror pour utiliser le miroir GitHub (pas de clé requise)
python manage.py update_geoip_db --mirror

# Ou avec une clé MaxMind (gratuite sur maxmind.com)
python manage.py update_geoip_db --license-key VOTRE_CLE
```

### Build CSS (Tailwind)

```bash
# Mode développement — regénère static/css/output.css à chaque modification
npm run watch:css

# Build standard — regénère static/css/output.css (non minifié)
npm run build:css

# Build production — regénère static/css/output.min.css (minifié, ~76 Ko)
# À exécuter avant `collectstatic` lors d'un déploiement
npm run build:css:prod
```

### Pré-commit hooks

```bash
pip install pre-commit
pre-commit install
```

### Qualité du code

Le projet utilise **flake8** (linter), **black** (formateur) et **isort** (tri des imports) :

```bash
# Vérifier la conformité PEP8
flake8

# Formater le code
black .

# Trier les imports
isort .
```

---

## Structure du projet

```
cc-sudavesnois/
├── app/                    # Configuration du projet Django
│   ├── settings.py
│   ├── urls.py             # URLs racine
│   ├── wsgi.py / asgi.py   # Points d'entrée serveur
│   ├── context_processors.py
│   └── utils.py
│
├── accounts/               # Application d'authentification
├── backup/                 # Sauvegarde de base de données
├── bureau_communautaire/   # Élus et documents officiels
├── commissions/            # Commissions
├── communes_membres/       # Actes locaux
├── competences/            # Compétences
├── comptes_rendus/         # Comptes rendus et PV
├── conseil_communautaire/  # Conseil communautaire
├── contact/                # Emails de contact
├── home/                   # Pages principales
├── journal/                # Journal d'information
├── linktree/               # Page de liens
├── partenaires/            # Partenaires
├── rapports_activite/      # Rapports d'activité
├── search/                 # Indexation de recherche
├── semestriels/            # Calendrier semestriel
├── services/               # Guide des services
├── analytics/              # Statistiques de visites (JSON, middleware, GeoIP)
│
├── static/                 # Fichiers statiques (CSS, JS, images)
├── templates/              # Templates globaux (base.html, header, footer)
├── media/                  # Fichiers uploadés
├── docs/                   # Documentation
│
├── manage.py               # CLI Django
├── requirements.txt        # Dépendances Python
├── pyproject.toml          # Configuration des outils
├── package.json            # Dépendances Node.js (Tailwind)
└── tailwind.config.js      # Configuration Tailwind CSS
```

---

## Tests

```bash
# Exécuter tous les tests
python manage.py test

# Tests d'une application spécifique
python manage.py test journal

# Avec verbosité
python manage.py test --verbosity=2
```

Le projet utilise le framework de test intégré de Django (`django.test.TestCase`).

---

## Accessibilité

Le site vise la conformité **RGAA 4.1 (niveau AA)**.

Fonctionnalités :
- **Contraste élevé** : mode d'affichage à fort contraste
- **Taille de texte ajustable** : agrandissement du texte
- **Navigation au clavier** : tous les éléments accessibles au clavier
- **Attributs ARIA** : rôles et propriétés ARIA appropriés
- **Liens d'évitement** : accès direct au contenu principal
- **Mode sombre** : interface adaptable

Consultez le fichier [`RGAA.md`](RGAA.md) pour les détails de conformité.

---

## Déploiement

### Architecture cible

```
Utilisateur → Nginx → Gunicorn → Django → PostgreSQL
                              ↘ WhiteNoise (fichiers statiques)
```

### Étapes

1. Configurer PostgreSQL et les variables d'environnement
2. Installer les dépendances et appliquer les migrations
3. Générer le CSS Tailwind minifié pour la production : `npm install && npm run build:css:prod`
4. Collecter les fichiers statiques : `python manage.py collectstatic --noinput`
5. Configurer Nginx/Apache en proxy inverse
6. Activer HTTPS (Let's Encrypt)

> **Cache statique** : WhiteNoise est configuré pour servir les fichiers avec un cache de **1 an + header `immutable`** (cf. `app/settings.py > WHITENOISE_MAX_AGE` et `WHITENOISE_IMMUTABLE_FILE_TEST`). Les fichiers collectés sont automatiquement renommés avec un hash de contenu (`output.min.38a16c852cb5.css`) — tout changement de contenu génère une nouvelle URL, ce qui force le navigateur à re-télécharger sans intervention manuelle.

### Mise à jour en production

Procédure à exécuter **sur le serveur** (dans l'ordre) après chaque déploiement de code :

```bash
# 0. Se placer dans le répertoire du projet et activer l'environnement virtuel
cd /var/www/cc-sudavesnois   # adapter le chemin
source .venv/bin/activate    # Linux — ou .venv\Scripts\activate sur Windows

# 1. Sauvegarder la base de données AVANT toute migration
python manage.py create_backup
# Ou via PostgreSQL directement :
# pg_dump -U <user> -h <host> <dbname> > backups/pre_update_$(date +%Y%m%d_%H%M%S).sql

# 2. Récupérer les dernières modifications
git pull origin main

# 3. Mettre à jour les dépendances Python
pip install -r requirements.txt --upgrade

# 4. Appliquer les migrations de la base de données
#    (makemigrations n'est nécessaire que si de nouveaux modèles ont été ajoutés
#     par les devs ; en prod on applique juste les migrations existantes)
python manage.py migrate

# 5. Collecter les fichiers statiques (CSS, JS, images, fonts)
python manage.py collectstatic --noinput

# 6. Reconstruire l'index de recherche full-text (si l'app search a été modifiée)
python manage.py buildwatson

# 7. Redémarrer les services applicatifs
sudo systemctl restart gunicorn      # ou supervisor, pm2, etc.
sudo systemctl restart nginx         # si la conf Nginx a changé

# 8. Vérifier le bon fonctionnement
sudo systemctl status gunicorn
tail -n 50 /var/log/gunicorn/error.log
curl -I https://www.cc-sudavesnois.fr  # doit retourner 200 OK
```

> **Bonnes pratiques**
> - Toujours faire la sauvegarde **avant** `migrate` (étape 1).
> - Exécuter la procédure pendant une fenêtre de maintenance à faible trafic.
> - Vérifier les logs après redémarrage pour s'assurer qu'il n'y a pas d'erreur.
> - En cas de rollback : `git checkout <commit_precedent>` puis rejouer les étapes 3 à 7.

#### Build du CSS Tailwind (à faire **en local**, pas sur le serveur)

Le fichier `static/css/output.min.css` est versionné dans le dépôt. Le serveur n'a donc **pas besoin de Node.js/npm** : un simple `git pull` le récupère.

À exécuter **uniquement sur votre poste de développement** quand vous modifiez des templates HTML ou des classes Tailwind :

```bash
# En développement (regénération auto à chaque modification)
npm run watch:css

# Avant de pousser en production
npm run build:css:prod
git add static/css/output.css static/css/output.min.css
git commit -m "build(css): regenerer output.min.css"
git push origin main
```

##### Alternative si vous ne pouvez pas builder en local

Si vous n'avez accès ni à Node.js, ni à un poste de dev, le workflow GitHub Actions `.github/workflows/build-css.yml` s'en charge automatiquement :

- **Déclencheur** : push sur `main` modifiant un template HTML, `static/css/input.css`, `tailwind.config.js` ou `package.json`.
- **Action** : installe Node.js 20, lance `npm ci`, exécute `npm run build:css` et `npm run build:css:prod`, puis commit `static/css/output.min.css` directement sur la branche (avec le message `build(css): regen output.min.css (auto)`).
- **Anti-boucle** : les modifications de `static/css/output.css` et `static/css/output.min.css` n'ont aucun effet sur les classes HTML et n'ont pas besoin d'être buildées à nouveau. Le workflow utilise `paths-ignore` pour ne pas se redéclencher sur ses propres commits.

Le workflow peut aussi être lancé manuellement depuis l'onglet **Actions** du dépôt GitHub via le bouton "Run workflow".

> En dernier recours uniquement (non recommandé en prod), il est possible d'utiliser **Tailwind Play CDN** en remplaçant la balise `link` dans `base.html` par :
> ```html
> <script src="https://cdn.tailwindcss.com"></script>
> ```
> ⚠️ ~300 Ko, non purgeable, pas de JIT, à n'utiliser qu'en dernier recours.

---

## Documentation

| Document | Description |
|----------|-------------|
| `CHANGELOG.md` | Historique des modifications |
| `RGAA.md` | Référentiel RGAA |
| `WCAG.md` | Règles WCAG |
| `EAA.md` | European Accessibility Act |
| `docs/tailwind.md` | Configuration et usage de Tailwind CSS |
| `docs/architecture.md` | Architecture du projet |
| `docs/deployment.md` | Guide de déploiement |
| `docs/security.md` | Considérations de sécurité |
| `docs/testing.md` | Guide des tests |

---

## Contribuer

1. Créer une branche depuis `main`
2. Développer la fonctionnalité ou la correction
3. Exécuter les tests : `python manage.py test`
4. Vérifier le linting : `flake8`
5. Ouvrir une Pull Request

---

<div align="center">

**Développé pour la Communauté de Communes Sud-Avesnois**

[Site officiel](https://www.cc-sudavesnois.fr) | [Contact](mailto:contact@cc-sudavesnois.fr)

&copy; 2025 Communauté de Communes Sud-Avesnois. Tous droits réservés.

</div>
