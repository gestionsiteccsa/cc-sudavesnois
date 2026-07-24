import os
import sys
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent
# Initialisation robuste des variables d'environnement
# (permet de gérer les secrets et les paramètres sensibles hors du code)
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))
# Clé secrète lue depuis le .env (jamais versionner en clair)
SECRET_KEY = env("SECRET_KEY")

# ATTENTION : DEBUG doit être à False en production !
# Utilisez env.bool('DEBUG', default=False) pour gérer le .env
DEBUG = env.bool("DEBUG", default=False)

# Liste blanche des hôtes autorisés (sécurité obligatoire en prod)
ALLOWED_HOSTS = env("ALLOWED_HOSTS", default="localhost,127.0.0.1").split(",")

# Indicateur de contexte de test (utilisé pour neutraliser des mécanismes rate limiting)
TESTING = "test" in sys.argv

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    "widget_tweaks",
    "watson",
    "home",
    "accounts",
    "conseil_communautaire",
    "journal",
    "bureau_communautaire",
    "communes_membres",
    "contact",
    "commissions",
    "competences",
    "semestriels",
    "comptes_rendus",
    "services",
    "rapports_activite",
    "linktree",
    "backup",
    "partenaires",
    "search",
    "analytics",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "watson.middleware.SearchContextMiddleware",
    "csp.middleware.CSPMiddleware",
    "analytics.middleware.PageTrackingMiddleware",
]

APPEND_SLASH = True
PREPEND_WWW = False

ROOT_URLCONF = "app.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "app.context_processors.get_cities",
            ],
            "builtins": [
                "bureau_communautaire.templatetags.BC_filters",
            ],
        },
    },
]

WSGI_APPLICATION = "app.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
        "CONN_MAX_AGE": env.int("CONN_MAX_AGE", default=300),
    }
}

# Paramètres de sécurité recommandés pour la production
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = env("SECURE_SSL_REDIRECT", default=not DEBUG)  # Force HTTPS
SECURE_HSTS_SECONDS = env("SECURE_HSTS_SECONDS", default=31536000)  # HSTS header
SECURE_HSTS_INCLUDE_SUBDOMAINS = env(
    "SECURE_HSTS_INCLUDE_SUBDOMAINS", default=True
)  # HSTS sur sous-domaines
SECURE_HSTS_PRELOAD = env("SECURE_HSTS_PRELOAD", default=True)  # Préchargement HSTS
SESSION_COOKIE_SECURE = env("SESSION_COOKIE_SECURE", default=True)  # Cookies sécurisés
CSRF_COOKIE_SECURE = env("CSRF_COOKIE_SECURE", default=True)  # Cookies CSRF sécurisés

# Headers de sécurité supplémentaires
SESSION_COOKIE_HTTPONLY = (
    True  # Empêche l'accès aux cookies via JavaScript (protection XSS)
)
SESSION_COOKIE_SAMESITE = "Lax"  # Protection contre CSRF
SECURE_CONTENT_TYPE_NOSNIFF = True  # Empêche le MIME type sniffing
SECURE_BROWSER_XSS_FILTER = True  # Active le filtre XSS du navigateur
X_FRAME_OPTIONS = "DENY"  # Empêche le clickjacking


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": ("django.contrib.auth.password_validation." "MinimumLengthValidator"),
    },
    {
        "NAME": ("django.contrib.auth.password_validation." "CommonPasswordValidator"),
    },
    {
        "NAME": ("django.contrib.auth.password_validation." "NumericPasswordValidator"),
    },
]


LANGUAGE_CODE = "fr-fr"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# Configuration WhiteNoise pour servir les fichiers statiques en production
# (Django 6.0+ : STORAGES remplace STATICFILES_STORAGE)
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# Cache long terme (1 an) pour les fichiers statiques collectés.
# Sans danger car `collectstatic` renomme chaque fichier avec un hash
# dérivé de son contenu : un changement de contenu => une nouvelle URL
# => le navigateur retélécharge automatiquement la nouvelle version.
WHITENOISE_MAX_AGE = 31536000  # 1 an en secondes


# Active l'en-tête "immutable" sur tous les fichiers servis : le navigateur
# ne lance même pas de requête de revalidation (If-Modified-Since) pendant
# toute la durée du cache.
def _whitenoise_all_files_immutable(path, url):  # noqa: ARG001
    return True


WHITENOISE_IMMUTABLE_FILE_TEST = _whitenoise_all_files_immutable

# Ne conserve dans staticfiles/ que les fichiers hachés (économise de l'espace
# en supprimant les originaux non-référencés ; le manifest fait le mapping).
WHITENOISE_KEEP_ONLY_HASHED_FILES = True

# Force Django à servir les fichiers statiques même en production
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

MEDIA_ROOT = BASE_DIR / "media"
MEDIA_URL = "/media/"
DATA_UPLOAD_MAX_MEMORY_SIZE = 60 * 1024 * 1024  # 60 Mo

# Sessions persistantes en base de données.
# Choix ``backends.db`` plutôt que ``backends.cache`` car l'hébergement
# mutualisé (o2switch) ne fournit ni Redis ni memcached. Le cache LRU
# par processus (``LocMemCache``) ne partage pas les sessions entre
# workers, ce qui provoque des déconnexions aléatoires.
SESSION_ENGINE = "django.contrib.sessions.backends.db"

# Durée de session : 30 jours par défaut, étendue par ``set_expiry`` dans
# la vue de connexion lorsque la case « Se souvenir de moi » est cochée.
SESSION_COOKIE_AGE = 30 * 24 * 60 * 60  # 30 jours

# Session glissante : l'expiration est repoussée à chaque requête tant
# que l'utilisateur reste actif. Sans ce flag, un utilisateur actif
# serait déconnecté au bout de 30 jours sans nouvelle connexion.
SESSION_SAVE_EVERY_REQUEST = True

# Configuration des backups
BACKUP_ROOT = env("BACKUP_ROOT", default=os.path.join(BASE_DIR, "backups"))
BACKUP_RETENTION_COUNT = env.int("BACKUP_RETENTION_COUNT", default=4)

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "accounts.CustomUser"


LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "accounts:profile"
LOGOUT_REDIRECT_URL = "accounts:login"


# Content Security Policy
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = (
    "'self'",
    "https://www.googletagmanager.com",
    "https://cdn.tailwindcss.com",
    "https://cdnjs.cloudflare.com",
    "https://cdn.jsdelivr.net",
)
CSP_STYLE_SRC = ("'self'", "https://fonts.googleapis.com", "'unsafe-inline'")
CSP_IMG_SRC = ("'self'", "data:", "https://cc-sudavesnois.fr")
CSP_FONT_SRC = ("'self'", "https://fonts.gstatic.com")
CSP_CONNECT_SRC = ("'self'", "https://www.google-analytics.com")
CSP_WORKER_SRC = ("'self'", "https://cdnjs.cloudflare.com")
CSP_FRAME_SRC = ("'none'",)
CSP_FORM_ACTION = ("'self'",)
CSP_OBJECT_SRC = ("'none'",)

# Active les pages d'erreur personnalisées
HANDLER404 = "home.views.custom_handler404"
HANDLER500 = "home.views.custom_handler500"


EMAIL_BACKEND = env("EMAIL_BACKEND")
EMAIL_HOST = env("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = env.int("EMAIL_PORT", default=587)
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=False)
EMAIL_USE_SSL = env.bool("EMAIL_USE_SSL", default=False)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = "nepasrepondre@cc-sudavesnois.fr"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{asctime} [{levelname}] {name} {message}",
            "style": "{",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "simple": {
            "format": "{asctime} [{levelname}] {message}",
            "style": "{",
            "datefmt": "%H:%M:%S",
        },
    },
    "handlers": {
        "app": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": BASE_DIR / "logs" / "app.log",
            "maxBytes": 5 * 1024 * 1024,
            "backupCount": 5,
            "formatter": "verbose",
        },
        "error": {
            "level": "WARNING",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": BASE_DIR / "logs" / "error.log",
            "maxBytes": 5 * 1024 * 1024,
            "backupCount": 5,
            "formatter": "verbose",
        },
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "root": {
        "handlers": ["app", "error"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["app", "error"],
            "level": "INFO",
            "propagate": False,
        },
        "django.request": {
            "handlers": ["error"],
            "level": "WARNING",
            "propagate": False,
        },
        "django.security": {
            "handlers": ["error"],
            "level": "WARNING",
            "propagate": False,
        },
        "accounts.audit": {
            "handlers": ["app"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

if DEBUG:
    LOGGING["root"]["handlers"].append("console")
    LOGGING["root"]["level"] = "DEBUG"
    LOGGING["loggers"]["django"]["handlers"].append("console")
    LOGGING["loggers"]["django"]["level"] = "DEBUG"
