# Guide SEO Complet pour Django

## Table des matières
- [Configuration de base](#configuration-de-base)
- [URLs et structure du site](#urls-et-structure-du-site)
- [Meta tags et données structurées](#meta-tags-et-données-structurées)
- [Performance et vitesse](#performance-et-vitesse)
- [Contenu et optimisation](#contenu-et-optimisation)
- [Sitemap et robots.txt](#sitemap-et-robotstxt)
- [HTTPS et sécurité](#https-et-sécurité)
- [Mobile et responsive](#mobile-et-responsive)
- [Monitoring et analytics](#monitoring-et-analytics)

## Configuration de base

### Settings.py essentiels
```python
# SEO-friendly settings
ALLOWED_HOSTS = ['votredomaine.com', 'www.votredomaine.com']
USE_TZ = True
TIME_ZONE = 'Europe/Paris'

# Pour les URLs canoniques
SITE_ID = 1
DOMAIN = 'votredomaine.com'

# Compression et cache
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'
```

### Middleware recommandés
```python
MIDDLEWARE = [
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
]
```

## URLs et structure du site

### URLs SEO-friendly
```python
# urls.py
from django.urls import path, include
from . import views

urlpatterns = [
    # URLs explicites et descriptives
    path('articles/', views.ArticleListView.as_view(), name='article_list'),
    path('articles/<slug:slug>/', views.ArticleDetailView.as_view(), name='article_detail'),
    path('categories/<slug:category_slug>/', views.CategoryView.as_view(), name='category_detail'),
    
    # Éviter les URLs avec des IDs numériques
    # ❌ path('article/<int:id>/', ...)
    # ✅ path('articles/<slug:slug>/', ...)
]
```

### Modèles avec slugs
```python
# models.py
from django.db import models
from django.utils.text import slugify
from django.urls import reverse

class Article(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    content = models.TextField()
    meta_description = models.CharField(max_length=160, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('article_detail', kwargs={'slug': self.slug})
```

### Redirections 301
```python
# views.py
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponsePermanentRedirect

def old_article_redirect(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    return HttpResponsePermanentRedirect(article.get_absolute_url())
```

## Meta tags et données structurées

### Template de base SEO
```html
<!-- base.html -->
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    
    <!-- Title tag -->
    <title>{% block title %}{% endblock %} | Nom du Site</title>
    
    <!-- Meta description -->
    <meta name="description" content="{% block meta_description %}Description par défaut du site{% endblock %}">
    
    <!-- Meta keywords (optionnel, peu d'impact) -->
    <meta name="keywords" content="{% block meta_keywords %}mots, clés, principaux{% endblock %}">
    
    <!-- Canonical URL -->
    <link rel="canonical" href="{% block canonical_url %}{{ request.build_absolute_uri }}{% endblock %}">
    
    <!-- Open Graph -->
    <meta property="og:title" content="{% block og_title %}{% block title %}{% endblock %}{% endblock %}">
    <meta property="og:description" content="{% block og_description %}{% block meta_description %}{% endblock %}{% endblock %}">
    <meta property="og:url" content="{{ request.build_absolute_uri }}">
    <meta property="og:type" content="{% block og_type %}website{% endblock %}">
    <meta property="og:image" content="{% block og_image %}{% load static %}{% static 'images/default-og-image.jpg' %}{% endblock %}">
    
    <!-- Twitter Cards -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{% block twitter_title %}{% block title %}{% endblock %}{% endblock %}">
    <meta name="twitter:description" content="{% block twitter_description %}{% block meta_description %}{% endblock %}{% endblock %}">
    <meta name="twitter:image" content="{% block twitter_image %}{% block og_image %}{% endblock %}{% endblock %}">
    
    <!-- Hreflang pour le multilangue -->
    {% if LANGUAGE_CODE == 'fr' %}
    <link rel="alternate" hreflang="fr" href="{{ request.build_absolute_uri }}">
    <link rel="alternate" hreflang="en" href="{% url 'current_page_en' %}">
    {% endif %}
</head>
```

### Données structurées (Schema.org)
```html
<!-- Dans vos templates -->
{% block structured_data %}
<script type="application/ld+json">
{
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": "{{ article.title }}",
    "description": "{{ article.meta_description }}",
    "author": {
        "@type": "Person",
        "name": "{{ article.author.get_full_name }}"
    },
    "datePublished": "{{ article.created_at|date:'c' }}",
    "dateModified": "{{ article.updated_at|date:'c' }}",
    "image": "{{ article.image.url }}",
    "url": "{{ request.build_absolute_uri }}"
}
</script>
{% endblock %}
```

### Mixin SEO pour les vues
```python
# mixins.py
class SEOMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'meta_title': self.get_meta_title(),
            'meta_description': self.get_meta_description(),
            'canonical_url': self.get_canonical_url(),
        })
        return context
    
    def get_meta_title(self):
        return getattr(self, 'meta_title', '')
    
    def get_meta_description(self):
        return getattr(self, 'meta_description', '')
    
    def get_canonical_url(self):
        return self.request.build_absolute_uri()
```

## Performance et vitesse

### Cache Django
```python
# settings.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'TIMEOUT': 300,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Cache par vue
CACHE_MIDDLEWARE_ALIAS = 'default'
CACHE_MIDDLEWARE_SECONDS = 600
CACHE_MIDDLEWARE_KEY_PREFIX = 'mysite'
```

### Optimisation des requêtes
```python
# views.py
from django.views.generic import ListView
from django.db.models import Prefetch

class ArticleListView(ListView):
    model = Article
    queryset = Article.objects.select_related('author').prefetch_related('tags')
    paginate_by = 20
    
    def get_queryset(self):
        return super().get_queryset().filter(published=True)
```

### Compression d'images
```python
# models.py
from PIL import Image
from django.core.files.base import ContentFile
import io

class Article(models.Model):
    image = models.ImageField(upload_to='articles/')
    
    def save(self, *args, **kwargs):
        if self.image:
            img = Image.open(self.image)
            if img.height > 1080 or img.width > 1920:
                img.thumbnail((1920, 1080))
                output = io.BytesIO()
                img.save(output, format='JPEG', quality=85)
                output.seek(0)
                self.image = ContentFile(output.read(), self.image.name)
        super().save(*args, **kwargs)
```

### Lazy loading des images
```html
<!-- Dans vos templates -->
<img src="{{ article.image.url }}" 
     alt="{{ article.title }}" 
     loading="lazy"
     width="800" 
     height="600">
```

## Contenu et optimisation

### Balises HTML sémantiques
```html
<article>
    <header>
        <h1>{{ article.title }}</h1>
        <time datetime="{{ article.created_at|date:'c' }}">
            {{ article.created_at|date:'d F Y' }}
        </time>
    </header>
    
    <main>
        {{ article.content|safe }}
    </main>
    
    <footer>
        <address>
            Par <a href="{{ article.author.get_absolute_url }}">{{ article.author.get_full_name }}</a>
        </address>
    </footer>
</article>
```

### Fil d'Ariane
```html
<!-- breadcrumb.html -->
<nav aria-label="Fil d'Ariane">
    <ol itemscope itemtype="https://schema.org/BreadcrumbList">
        <li itemprop="itemListElement" itemscope itemtype="https://schema.org/ListItem">
            <a itemprop="item" href="{% url 'home' %}">
                <span itemprop="name">Accueil</span>
            </a>
            <meta itemprop="position" content="1" />
        </li>
        {% for breadcrumb in breadcrumbs %}
        <li itemprop="itemListElement" itemscope itemtype="https://schema.org/ListItem">
            <a itemprop="item" href="{{ breadcrumb.url }}">
                <span itemprop="name">{{ breadcrumb.name }}</span>
            </a>
            <meta itemprop="position" content="{{ forloop.counter|add:1 }}" />
        </li>
        {% endfor %}
    </ol>
</nav>
```

### Pagination SEO-friendly
```python
# views.py
from django.core.paginator import Paginator

class ArticleListView(ListView):
    paginate_by = 20
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Meta title avec numéro de page
        if context['page_obj'].number > 1:
            context['meta_title'] = f"Articles - Page {context['page_obj'].number}"
        
        return context
```

```html
<!-- Liens de pagination -->
{% if page_obj.has_previous %}
<link rel="prev" href="?page={{ page_obj.previous_page_number }}">
{% endif %}

{% if page_obj.has_next %}
<link rel="next" href="?page={{ page_obj.next_page_number }}">
{% endif %}
```

## Sitemap et robots.txt

### Sitemap XML
```python
# sitemaps.py
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Article, Category

class ArticleSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8
    
    def items(self):
        return Article.objects.filter(published=True)
    
    def lastmod(self, obj):
        return obj.updated_at

class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = 'monthly'
    
    def items(self):
        return ['home', 'about', 'contact']
    
    def location(self, item):
        return reverse(item)

# urls.py
from django.contrib.sitemaps.views import sitemap
from .sitemaps import ArticleSitemap, StaticViewSitemap

sitemaps = {
    'articles': ArticleSitemap,
    'static': StaticViewSitemap,
}

urlpatterns = [
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
]
```

### Robots.txt
```python
# views.py
from django.http import HttpResponse
from django.views.decorators.http import require_GET

@require_GET
def robots_txt(request):
    lines = [
        "User-Agent: *",
        "Disallow: /admin/",
        "Disallow: /private/",
        "Allow: /",
        "",
        f"Sitemap: {request.build_absolute_uri('/sitemap.xml')}",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")

# urls.py
urlpatterns = [
    path('robots.txt', views.robots_txt),
]
```

## HTTPS et sécurité

### Configuration HTTPS
```python
# settings.py pour production
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000  # 1 an
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

## Mobile et responsive

### Meta viewport
```html
<meta name="viewport" content="width=device-width, initial-scale=1.0">
```

### CSS responsive
```css
/* Base mobile-first */
.container {
    max-width: 100%;
    padding: 0 1rem;
}

@media (min-width: 768px) {
    .container {
        max-width: 750px;
        margin: 0 auto;
    }
}

@media (min-width: 1200px) {
    .container {
        max-width: 1140px;
    }
}
```

## Monitoring et analytics

### Google Analytics 4
```html
<!-- Dans base.html -->
{% if not debug %}
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
</script>
{% endif %}
```

### Google Search Console
```html
<!-- Vérification Search Console -->
<meta name="google-site-verification" content="VOTRE_CODE_VERIFICATION">
```

### Logs et monitoring
```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'seo.log',
        },
    },
    'loggers': {
        'seo': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

## Checklist SEO finale

### Technique
- [ ] URLs SEO-friendly avec slugs
- [ ] Redirections 301 pour les anciennes URLs
- [ ] HTTPS configuré et forcé
- [ ] Sitemap XML généré et soumis
- [ ] Robots.txt configuré
- [ ] Temps de chargement < 3 secondes
- [ ] Site responsive et mobile-friendly
- [ ] Images optimisées avec alt text

### Contenu
- [ ] Titre unique pour chaque page (< 60 caractères)
- [ ] Meta description pour chaque page (< 160 caractères)
- [ ] Structure H1-H6 respectée
- [ ] Contenu unique et de qualité
- [ ] Liens internes cohérents
- [ ] Fil d'Ariane implémenté

### Données structurées
- [ ] Schema.org implémenté (Article, Organization, etc.)
- [ ] Open Graph pour les réseaux sociaux
- [ ] Twitter Cards configurées
- [ ] Hreflang pour le multilangue (si applicable)

### Analytics
- [ ] Google Analytics configuré
- [ ] Google Search Console configuré
- [ ] Suivi des erreurs 404
- [ ] Monitoring des performances

