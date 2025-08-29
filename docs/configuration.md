# Configuration du Projet CCSA

## 📋 Vue d'ensemble

Ce document détaille l'ensemble des configurations du projet CCSA, depuis les paramètres Django jusqu'aux configurations des outils de développement et de déploiement.

## ⚙️ Configuration Django

### Fichier Settings Principal

Le fichier `app/settings.py` centralise toute la configuration du projet :

```python
from pathlib import Path
import environ
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# Variables d'environnement sécurisées
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# Clé secrète (OBLIGATOIRE en production via .env)
SECRET_KEY = env('SECRET_KEY')

# Mode debug (FALSE en production)
DEBUG = True  # ← Modifier pour env.bool('DEBUG', default=False)

# Hôtes autorisés
ALLOWED_HOSTS = env('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')
```

### Configuration des Applications

```python
INSTALLED_APPS = [
    # Applications Django Core
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    
    # Applications tierces
    'widget_tweaks',  # Amélioration des formulaires
    
    # Applications métier CCSA
    'home',                    # Pages principales
    'accounts',               # Authentification
    'conseil_communautaire',  # Gestion des élus
    'journal',               # Publications
    'bureau_communautaire',  # Bureau
    'communes_membres',      # 12 communes
    'contact',              # Formulaire contact
    'commissions',          # Commissions
    'competences',          # Compétences
    'semestriels',          # Publications semestrielles
    'comptes_rendus',       # Comptes-rendus
    'services',             # Services publics
    'rapports_activite'     # Rapports annuels
]
```

### Configuration des Middlewares

```python
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",      # Sécurité
    "django.contrib.sessions.middleware.SessionMiddleware",  # Sessions
    "django.middleware.common.CommonMiddleware",          # Fonctionnalités communes
    "django.middleware.csrf.CsrfViewMiddleware",          # Protection CSRF
    "django.contrib.auth.middleware.AuthenticationMiddleware",  # Auth
    "django.contrib.messages.middleware.MessageMiddleware",     # Messages
    "django.middleware.clickjacking.XFrameOptionsMiddleware",   # Clickjacking
]
```

## 🗄️ Configuration Base de Données

### Développement (SQLite)

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

### Production (PostgreSQL)

```python
# Configuration recommandée pour la production
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('POSTGRES_DB'),
        'USER': env('POSTGRES_USER'),
        'PASSWORD': env('POSTGRES_PASSWORD'),
        'HOST': env('POSTGRES_HOST', default='localhost'),
        'PORT': env('POSTGRES_PORT', default='5432'),
        'OPTIONS': {
            'charset': 'utf8',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        }
    }
}
```

## 🔧 Configuration des Templates

```python
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],  # Templates globaux
        "APP_DIRS": True,  # Templates par application
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "app.context_processors.get_cities",  # Processeur personnalisé
            ],
            'builtins': [
                'bureau_communautaire.templatetags.BC_filters',  # Filtres personnalisés
            ],
        },
    },
]
```

## 🔐 Configuration de Sécurité

### Paramètres de Sécurité Production

```python
# Force HTTPS en production
SECURE_SSL_REDIRECT = env('SECURE_SSL_REDIRECT', default=False)

# En-têtes HSTS (HTTP Strict Transport Security)
SECURE_HSTS_SECONDS = env('SECURE_HSTS_SECONDS', default=31536000)  # 1 an
SECURE_HSTS_INCLUDE_SUBDOMAINS = env('SECURE_HSTS_INCLUDE_SUBDOMAINS', default=True)
SECURE_HSTS_PRELOAD = env('SECURE_HSTS_PRELOAD', default=True)

# Cookies sécurisés
SESSION_COOKIE_SECURE = env('SESSION_COOKIE_SECURE', default=True)
CSRF_COOKIE_SECURE = env('CSRF_COOKIE_SECURE', default=True)
```

### Validation des Mots de Passe

```python
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]
```

## 📧 Configuration Email

### Développement (Console)

```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

### Production (SMTP)

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = env.int('EMAIL_PORT', default=587)
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=True)
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')
```

## 📁 Configuration des Fichiers Statiques

```python
# URL des fichiers statiques
STATIC_URL = "static/"

# Répertoires des fichiers statiques
STATICFILES_DIRS = [BASE_DIR / "static"]

# Répertoire de collecte (production)
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# Fichiers médias uploadés
MEDIA_ROOT = BASE_DIR / "media"
MEDIA_URL = "/media/"

# Limite de taille d'upload
DATA_UPLOAD_MAX_MEMORY_SIZE = 35 * 1024 * 1024  # 35 Mo
```

## 🌐 Configuration Internationale

```python
# Langue par défaut
LANGUAGE_CODE = "fr-fr"

# Fuseau horaire
TIME_ZONE = "UTC"

# Internationalisation
USE_I18N = True

# Localisation
USE_TZ = True
```

## 👤 Configuration Authentification

```python
# Modèle utilisateur personnalisé
AUTH_USER_MODEL = 'accounts.CustomUser'

# URLs d'authentification
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'accounts:profile'
LOGOUT_REDIRECT_URL = 'accounts:login'
```

## 🛠️ Configuration des Outils de Développement

### Flake8 Configuration

Fichier `.flake8` :

```ini
[flake8]
max-line-length = 79
exclude = 
    migrations,
    __pycache__,
    manage.py,
    settings.py,
    env,
    venv,
    .env
ignore = 
    E203,  # whitespace before ':'
    W503,  # line break before binary operator
per-file-ignores =
    __init__.py:F401
```

### Configuration Tailwind CSS

Fichier `tailwind.config.js` :

```javascript
module.exports = {
  content: [
    './templates/**/*.html',
    './home/templates/**/*.html',
    './accounts/templates/**/*.html',
    './conseil_communautaire/templates/**/*.html',
    './journal/templates/**/*.html',
    './bureau_communautaire/templates/**/*.html',
    './communes_membres/templates/**/*.html',
    './contact/templates/**/*.html',
    './commissions/templates/**/*.html',
    './competences/templates/**/*.html',
    './semestriels/templates/**/*.html',
    './comptes_rendus/templates/**/*.html',
    './services/templates/**/*.html',
    './rapports_activite/templates/**/*.html',
  ],
  theme: {
    extend: {
      colors: {
        primary: '#006ab3',      // Bleu CCSA
        secondary: '#96bf0d',    // Vert CCSA
      },
      fontFamily: {
        sans: ['Roboto', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Arial', 'sans-serif'],
      },
    },
  },
  darkMode: 'class',  // Mode sombre basé sur les classes
  plugins: [],
}
```

## 📦 Configuration des Dépendances

### Python - requirements.txt

```txt
# Framework principal
Django==5.1.7
django-environ==0.12.0

# Outils de formulaires
django-widget-tweaks==1.5.0

# Gestion des cookies
django-cookie-consent==0.6.0

# Outils de qualité
flake8==7.1.2
bandit==1.8.3
pre-commit==4.2.0

# Traitement d'images
Pillow==11.2.1

# Parsing et requêtes
beautifulsoup4==4.13.3
requests==2.32.3

# Utilitaires
tqdm==4.67.1
PyYAML==6.0.2
```

### Node.js - package.json

```json
{
  "name": "cc-sudavesnois",
  "version": "1.0.0",
  "devDependencies": {
    "@stagewise/toolbar": "^0.3.0",
    "autoprefixer": "^10.4.21",
    "postcss": "^8.5.4",
    "tailwindcss": "^3.4.3",
    "tailwindcss-cli": "^0.1.2"
  },
  "dependencies": {
    "browserslist": "^4.25.0",
    "caniuse-lite": "^1.0.30001720"
  }
}
```

## 🔄 Variables d'Environnement

### Fichier .env (Développement)

```env
# Django Core
SECRET_KEY=votre_cle_secrete_de_developpement
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Base de données (optionnel en dev)
DATABASE_URL=sqlite:///db.sqlite3

# Email (dev)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Sécurité (dev)
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
```

### Fichier .env (Production)

```env
# Django Core
SECRET_KEY=cle_secrete_production_tres_longue_et_complexe
DEBUG=False
ALLOWED_HOSTS=www.cc-sudavesnois.fr,cc-sudavesnois.fr

# Base de données PostgreSQL
POSTGRES_DB=ccsa_prod
POSTGRES_USER=ccsa_user
POSTGRES_PASSWORD=mot_de_passe_securise
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Email SMTP
EMAIL_HOST=smtp.votre-fournisseur.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=noreply@cc-sudavesnois.fr
EMAIL_HOST_PASSWORD=mot_de_passe_email

# Sécurité (production)
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

## 🚀 Configuration de Déploiement

### Configuration Gunicorn

Fichier `gunicorn.conf.py` :

```python
# Configuration Gunicorn pour production
bind = "127.0.0.1:8000"
workers = 3
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 30
keepalive = 2
preload_app = True
```

### Configuration Nginx

```nginx
server {
    listen 80;
    server_name cc-sudavesnois.fr www.cc-sudavesnois.fr;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name cc-sudavesnois.fr www.cc-sudavesnois.fr;

    ssl_certificate /path/to/ssl/cert.pem;
    ssl_certificate_key /path/to/ssl/private.key;

    # Fichiers statiques
    location /static/ {
        alias /path/to/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Fichiers médias
    location /media/ {
        alias /path/to/media/;
        expires 1M;
    }

    # Proxy vers Django
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 🔧 Configuration des URLs

### URLs Principales (`app/urls.py`)

```python
from django.contrib import admin
from django.urls import path, include
from django.contrib.sitemaps.views import sitemap
from home.sitemaps import StaticViewSitemap, CommunesSitemap, JournalSitemap

sitemaps = {
    'static': StaticViewSitemap,
    'communes': CommunesSitemap,
    'journals': JournalSitemap,
}

urlpatterns = [
    # Administration
    path('ccsa-admin/', admin.site.urls),
    
    # Applications principales
    path('', include('home.urls')),
    path('', include('accounts.urls', namespace='accounts')),
    
    # SEO
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}),
    path('robots.txt', TemplateView.as_view(template_name='robots.txt')),
    
    # Applications métier
    path('', include('conseil_communautaire.urls')),
    path('', include('journal.urls', namespace='journal')),
    path('services/', include('services.urls', namespace='services')),
    # ... autres apps
]
```

## 📊 Métriques de Configuration

| Aspect | Configuration | Statut |
|--------|---------------|--------|
| **Sécurité** | HTTPS, HSTS, Cookies sécurisés | ✅ Conforme |
| **Base de données** | SQLite (dev) / PostgreSQL (prod) | ✅ Optimisé |
| **Cache** | Sessions Django | ⚠️ À améliorer |
| **Email** | Console (dev) / SMTP (prod) | ✅ Configuré |
| **Monitoring** | Logs Django | ⚠️ À améliorer |
| **Performance** | Fichiers statiques optimisés | ✅ Correct |

## ⚠️ Points d'Attention

### Sécurité
- ✅ `SECRET_KEY` externalisée dans `.env`
- ✅ `DEBUG=False` en production
- ✅ `ALLOWED_HOSTS` configurés
- ✅ Middleware de sécurité activés

### Performance
- ⚠️ Cache Redis non configuré
- ⚠️ Compression gzip à optimiser
- ✅ Fichiers statiques collectés

### Monitoring
- ⚠️ Logging structuré à ajouter
- ⚠️ Métriques de performance à implémenter
- ⚠️ Alertes automatiques à configurer

---

## 📝 Checklist de Configuration

### Développement
- [ ] Fichier `.env` créé et configuré
- [ ] Base de données SQLite initialisée
- [ ] Migrations appliquées
- [ ] Superutilisateur créé
- [ ] Tailwind CSS compilé
- [ ] Tests unitaires fonctionnels

### Production
- [ ] Variables d'environnement sécurisées
- [ ] Base PostgreSQL configurée
- [ ] HTTPS activé avec certificat SSL
- [ ] Fichiers statiques collectés
- [ ] Serveur web (Nginx/Apache) configuré
- [ ] Monitoring et logs activés
- [ ] Sauvegardes automatiques programmées

---

*Documentation configuration - Dernière mise à jour : 07/01/2025*