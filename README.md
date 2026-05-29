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

# 6. Compiler le CSS Tailwind
npx tailwindcss -i static/css/styles.css -o static/css/output.css --watch

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
3. Collecter les fichiers statiques : `python manage.py collectstatic`
4. Configurer Nginx/Apache en proxy inverse
5. Activer HTTPS (Let's Encrypt)

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
