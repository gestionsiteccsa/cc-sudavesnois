# Django - Guide des Bonnes Pratiques

## Table des matières
1. [Structure du projet](#structure-du-projet)
2. [Organisation des applications](#organisation-des-applications)
3. [Modèles (Models)](#modèles-models)
4. [Vues (Views)](#vues-views)
5. [Templates](#templates)
6. [URLs](#urls)
7. [Settings et Configuration](#settings-et-configuration)
8. [Sécurité](#sécurité)
9. [Tests](#tests)
10. [Performance](#performance)
11. [Convention de nommage](#convention-de-nommage)

---

## Structure du projet

### Architecture recommandée

```
myproject/
├── manage.py
├── requirements/
│   ├── base.txt
│   ├── development.txt
│   ├── production.txt
│   └── testing.txt
├── config/
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── development.py
│   │   ├── production.py
│   │   └── testing.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── __init__.py
│   ├── users/
│   ├── blog/
│   └── core/
├── static/
│   ├── css/
│   ├── js/
│   └── img/
├── media/
├── templates/
│   ├── base.html
│   └── includes/
├── locale/
├── docs/
└── scripts/
```

### Principes de base
- **Séparer le code métier** dans le dossier `apps/`
- **Centraliser la configuration** dans `config/`
- **Organiser les requirements** par environnement
- **Isoler les assets** dans `static/` et `media/`

---

## Organisation des applications

### Structure d'une application

```
apps/blog/
├── __init__.py
├── admin.py
├── apps.py
├── migrations/
├── models/
│   ├── __init__.py
│   ├── article.py
│   └── category.py
├── views/
│   ├── __init__.py
│   ├── article_views.py
│   └── category_views.py
├── serializers/
│   ├── __init__.py
│   └── article_serializers.py
├── forms/
│   ├── __init__.py
│   └── article_forms.py
├── urls.py
├── tests/
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_views.py
│   └── test_forms.py
├── managers/
│   ├── __init__.py
│   └── article_managers.py
├── utils/
│   ├── __init__.py
│   └── helpers.py
└── templates/blog/
    ├── article_list.html
    └── article_detail.html
```

### Bonnes pratiques
- **Diviser les gros fichiers** : Si `models.py` devient trop volumineux, créer un package `models/`
- **Grouper par fonctionnalité** : Une vue par fichier pour les vues complexes
- **Templates dédiés** : Chaque app a son dossier de templates

---

## Modèles (Models)

### Convention de nommage

```python
# ✅ Bon
class Article(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=False)
    
    # Relations
    author = models.ForeignKey('users.User', on_delete=models.CASCADE)
    categories = models.ManyToManyField('Category', blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Article'
        verbose_name_plural = 'Articles'
        
    def __str__(self):
        return self.title
        
    def get_absolute_url(self):
        return reverse('blog:article-detail', kwargs={'slug': self.slug})

# ❌ Éviter
class article(models.Model):  # Nom en minuscule
    Title = models.CharField(max_length=200)  # Champ en majuscule
    createdAt = models.DateTimeField()  # CamelCase
```

### Bonnes pratiques pour les modèles

#### 1. Utiliser des Managers personnalisés
```python
class PublishedArticleManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_published=True)

class Article(models.Model):
    # ... champs ...
    
    objects = models.Manager()  # Manager par défaut
    published = PublishedArticleManager()  # Manager personnalisé
```

#### 2. Propriétés et méthodes métier
```python
class Article(models.Model):
    # ... champs ...
    
    @property
    def reading_time(self):
        """Calcule le temps de lecture estimé"""
        word_count = len(self.content.split())
        return max(1, word_count // 200)
    
    def is_recent(self):
        """Vérifie si l'article est récent (moins de 7 jours)"""
        return (timezone.now() - self.created_at).days < 7
```

#### 3. Validation personnalisée
```python
class Article(models.Model):
    # ... champs ...
    
    def clean(self):
        if self.is_published and not self.content:
            raise ValidationError('Un article publié doit avoir du contenu')
```

---

## Vues (Views)

### Class-Based Views (recommandées)

```python
# ✅ Bon usage des CBV
class ArticleListView(ListView):
    model = Article
    template_name = 'blog/article_list.html'
    context_object_name = 'articles'
    paginate_by = 10
    
    def get_queryset(self):
        return Article.published.select_related('author').prefetch_related('categories')

class ArticleDetailView(DetailView):
    model = Article
    template_name = 'blog/article_detail.html'
    context_object_name = 'article'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        return Article.published.select_related('author')

class ArticleCreateView(LoginRequiredMixin, CreateView):
    model = Article
    form_class = ArticleForm
    template_name = 'blog/article_form.html'
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
```

### Function-Based Views (pour la logique complexe)

```python
# ✅ Bon usage des FBV
@login_required
def article_publish(request, pk):
    article = get_object_or_404(Article, pk=pk, author=request.user)
    
    if request.method == 'POST':
        article.is_published = True
        article.published_at = timezone.now()
        article.save()
        messages.success(request, 'Article publié avec succès')
        return redirect('blog:article-detail', slug=article.slug)
    
    return render(request, 'blog/article_publish_confirm.html', {'article': article})
```

### Bonnes pratiques pour les vues
- **Préférer les CBV** pour les opérations CRUD standards
- **Utiliser les FBV** pour la logique métier complexe
- **Optimiser les requêtes** avec `select_related()` et `prefetch_related()`
- **Toujours valider les permissions** et l'authentification

---

## Templates

### Structure des templates

```html
<!-- templates/base.html -->
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Mon Site{% endblock %}</title>
    {% load static %}
    <link rel="stylesheet" href="{% static 'css/main.css' %}">
    {% block extra_css %}{% endblock %}
</head>
<body>
    {% include 'includes/header.html' %}
    
    <main>
        {% include 'includes/messages.html' %}
        {% block content %}{% endblock %}
    </main>
    
    {% include 'includes/footer.html' %}
    
    <script src="{% static 'js/main.js' %}"></script>
    {% block extra_js %}{% endblock %}
</body>
</html>
```

### Bonnes pratiques templates
- **Utiliser l'héritage** avec `base.html`
- **Créer des includes** pour les composants réutilisables
- **Organiser les blocks** : `title`, `extra_css`, `content`, `extra_js`
- **Échapper les données** utilisateur (Django le fait par défaut)

---

## URLs

### Configuration des URLs

```python
# config/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls')),
    path('blog/', include('apps.blog.urls', namespace='blog')),
    path('users/', include('apps.users.urls', namespace='users')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# apps/blog/urls.py
from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.ArticleListView.as_view(), name='article-list'),
    path('article/<slug:slug>/', views.ArticleDetailView.as_view(), name='article-detail'),
    path('article/create/', views.ArticleCreateView.as_view(), name='article-create'),
    path('category/<slug:slug>/', views.CategoryDetailView.as_view(), name='category-detail'),
]
```

### Bonnes pratiques URLs
- **Utiliser des namespaces** pour éviter les conflits
- **Noms d'URLs cohérents** : `model-action` (ex: `article-list`, `article-detail`)
- **URLs SEO-friendly** avec des slugs
- **Regrouper par fonctionnalité**

---

## Settings et Configuration

### Structure des settings

```python
# config/settings/base.py
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'crispy_forms',
]

LOCAL_APPS = [
    'apps.core',
    'apps.users',
    'apps.blog',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# config/settings/development.py
from .base import *

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Database pour le développement
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# config/settings/production.py
from .base import *
import os

DEBUG = False
ALLOWED_HOSTS = [os.getenv('DOMAIN_NAME')]

# Database pour la production
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
    }
}
```

---

## Sécurité

### Configuration sécurisée

```python
# settings/production.py

# Sécurité HTTPS
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Cookies sécurisés
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True

# Content Security Policy
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
```

### Bonnes pratiques sécurité
- **Utiliser des variables d'environnement** pour les secrets
- **Valider toutes les entrées** utilisateur
- **Utiliser les permissions Django** appropriées
- **Configurer HTTPS** en production
- **Activer les headers de sécurité**

---

## Tests

### Structure des tests

```python
# apps/blog/tests/test_models.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.blog.models import Article

User = get_user_model()

class ArticleModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com'
        )
        
    def test_article_creation(self):
        article = Article.objects.create(
            title='Test Article',
            content='Test content',
            author=self.user
        )
        self.assertEqual(article.title, 'Test Article')
        self.assertFalse(article.is_published)
        
    def test_article_str_method(self):
        article = Article(title='Test Article')
        self.assertEqual(str(article), 'Test Article')

# apps/blog/tests/test_views.py
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.blog.models import Article

class ArticleViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.article = Article.objects.create(
            title='Test Article',
            content='Test content',
            author=self.user,
            is_published=True
        )
        
    def test_article_list_view(self):
        response = self.client.get(reverse('blog:article-list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Article')
```

---

## Performance

### Optimisation des requêtes

```python
# ✅ Bon : Optimisation des requêtes
def article_list_view(request):
    articles = Article.published.select_related('author').prefetch_related('categories')
    return render(request, 'blog/article_list.html', {'articles': articles})

# ✅ Pagination efficace
class ArticleListView(ListView):
    model = Article
    paginate_by = 20
    
    def get_queryset(self):
        return Article.published.select_related('author').only(
            'title', 'slug', 'created_at', 'author__username'
        )
```

### Cache

```python
# settings.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}

# Dans les vues
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

@method_decorator(cache_page(60 * 15), name='dispatch')  # 15 minutes
class ArticleListView(ListView):
    # ...
```

---

## Convention de nommage

### Variables et fonctions
```python
# ✅ Bon
user_name = 'john_doe'
article_count = 10
is_published = True

def get_published_articles():
    pass

def calculate_reading_time(content):
    pass

# ❌ Éviter
userName = 'john_doe'  # CamelCase
ArticleCount = 10      # PascalCase
```

### Classes
```python
# ✅ Bon
class ArticleManager(models.Manager):
    pass

class BlogPost(models.Model):
    pass

class ArticleForm(forms.ModelForm):
    pass

# ❌ Éviter
class article_manager:  # snake_case
    pass
```

### Constantes
```python
# ✅ Bon
MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5MB
DEFAULT_PAGINATION = 20
ARTICLE_STATUSES = [
    ('draft', 'Brouillon'),
    ('published', 'Publié'),
    ('archived', 'Archivé'),
]
```

### Fichiers et dossiers
```python
# ✅ Bon
article_views.py
user_serializers.py
blog_utils.py

# Dossiers
apps/
static/css/
templates/blog/
```
