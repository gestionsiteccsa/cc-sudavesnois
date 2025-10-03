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
DEBUG = env.bool('DEBUG', default=False)

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
]

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
    }
}

# Paramètres de sécurité recommandés pour la production
SECURE_SSL_REDIRECT = env("SECURE_SSL_REDIRECT", default=False)  # Force HTTPS
SECURE_HSTS_SECONDS = env("SECURE_HSTS_SECONDS", default=31536000)  # HSTS header
SECURE_HSTS_INCLUDE_SUBDOMAINS = env(
    "SECURE_HSTS_INCLUDE_SUBDOMAINS", default=True
)  # HSTS sur sous-domaines
SECURE_HSTS_PRELOAD = env("SECURE_HSTS_PRELOAD", default=True)  # Préchargement HSTS
SESSION_COOKIE_SECURE = env("SESSION_COOKIE_SECURE", default=True)  # Cookies sécurisés
CSRF_COOKIE_SECURE = env("CSRF_COOKIE_SECURE", default=True)  # Cookies CSRF sécurisés


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
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Force Django à servir les fichiers statiques même en production
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

MEDIA_ROOT = BASE_DIR / "media"
MEDIA_URL = "/media/"
DATA_UPLOAD_MAX_MEMORY_SIZE = 60 * 1024 * 1024  # 60 Mo

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "accounts.CustomUser"


LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "accounts:profile"
LOGOUT_REDIRECT_URL = "accounts:login"


# Active les pages d'erreur personnalisées
HANDLER404 = "home.views.custom_handler404"
HANDLER500 = "home.views.custom_handler500"


EMAIL_BACKEND = env("EMAIL_BACKEND")
EMAIL_HOST = env("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = env.int("EMAIL_PORT", default=587)
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=True)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
