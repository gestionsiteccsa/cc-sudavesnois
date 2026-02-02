---
description: Agent spécialisé dans les bonnes pratiques Django pour un code propre, sécurisé et performant
---

# Agent Bonnes Pratiques Django

Cet agent vérifie que le code Django respecte les meilleures pratiques en termes de sécurité, performance, maintenabilité et conventions.

## ⚠️ DÉCLENCHEMENT AUTOMATIQUE

**Cet agent DOIT être appliqué automatiquement lors de :**
- Création/modification de vues (`views.py`)
- Création/modification de modèles (`models.py`)
- Création/modification de formulaires (`forms.py`)
- Création/modification d'URLs (`urls.py`)
- Création/modification de templates Django
- Ajout de dépendances ou configurations

---

## Procédure de validation obligatoire

### Étape 1 : Vérifications selon le type de fichier

#### 1. Models (`models.py`)

```python
# ✅ BONNES PRATIQUES

from django.db import models
from django.urls import reverse


class Article(models.Model):
    """Documentation du modèle."""
    
    # Champs avec verbose_name pour l'admin
    title = models.CharField("Titre", max_length=200)
    slug = models.SlugField("Slug", unique=True)
    created_at = models.DateTimeField("Date de création", auto_now_add=True)
    updated_at = models.DateTimeField("Date de modification", auto_now=True)
    is_published = models.BooleanField("Publié", default=False)
    
    class Meta:
        verbose_name = "Article"
        verbose_name_plural = "Articles"
        ordering = ["-created_at"]
        # Index pour les requêtes fréquentes
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["is_published", "-created_at"]),
        ]
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        """URL absolue pour le modèle."""
        return reverse("article_detail", kwargs={"slug": self.slug})
```

**Checklist Models :**
- [ ] Docstring sur chaque modèle
- [ ] `verbose_name` sur les champs
- [ ] `Meta` class avec `verbose_name`, `verbose_name_plural`, `ordering`
- [ ] `__str__` défini
- [ ] `get_absolute_url` si modèle affiché en frontend
- [ ] Index sur les champs utilisés en filtres/recherches
- [ ] Pas de logique métier complexe (→ services)

---

#### 2. Views (`views.py`)

```python
# ✅ BONNES PRATIQUES

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView, DetailView


# Vue fonction simple
def article_list(request):
    """Liste des articles publiés."""
    articles = Article.objects.filter(is_published=True)
    return render(request, "blog/article_list.html", {"articles": articles})


# Vue fonction avec authentification
@login_required
def article_create(request):
    """Création d'un article (utilisateurs connectés)."""
    if request.method == "POST":
        form = ArticleForm(request.POST)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            return redirect(article.get_absolute_url())
    else:
        form = ArticleForm()
    return render(request, "blog/article_form.html", {"form": form})


# Vue basée sur classe
class ArticleListView(ListView):
    """Liste des articles avec pagination."""
    
    model = Article
    template_name = "blog/article_list.html"
    context_object_name = "articles"
    paginate_by = 10
    
    def get_queryset(self):
        return Article.objects.filter(is_published=True)


# Vue avec authentification requise
class ArticleDetailView(LoginRequiredMixin, DetailView):
    """Détail d'un article."""
    
    model = Article
    template_name = "blog/article_detail.html"
```

**Checklist Views :**
- [ ] Docstring sur chaque vue
- [ ] `get_object_or_404` au lieu de `try/except`
- [ ] `@login_required` ou `LoginRequiredMixin` si authentification
- [ ] Pas de logique métier complexe (→ services)
- [ ] Validation des entrées utilisateur
- [ ] `redirect()` après POST réussi (PRG pattern)

---

#### 3. Forms (`forms.py`)

```python
# ✅ BONNES PRATIQUES

from django import forms
from django.core.validators import RegexValidator

from .models import Article


class ArticleForm(forms.ModelForm):
    """Formulaire de création/édition d'article."""
    
    class Meta:
        model = Article
        fields = ["title", "content", "is_published"]
        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Titre de l'article",
                "autocomplete": "off",
            }),
            "content": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 10,
            }),
        }
    
    def clean_title(self):
        """Validation personnalisée du titre."""
        title = self.cleaned_data.get("title")
        if len(title) < 5:
            raise forms.ValidationError("Le titre doit contenir au moins 5 caractères.")
        return title


class ContactForm(forms.Form):
    """Formulaire de contact."""
    
    phone_validator = RegexValidator(
        regex=r"^0[1-9]\d{8}$",
        message="Numéro de téléphone invalide (format: 0612345678)"
    )
    
    name = forms.CharField(
        label="Nom",
        max_length=100,
        widget=forms.TextInput(attrs={"autocomplete": "name"})
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"autocomplete": "email"})
    )
    phone = forms.CharField(
        label="Téléphone",
        validators=[phone_validator],
        widget=forms.TextInput(attrs={"autocomplete": "tel"})
    )
    message = forms.CharField(
        label="Message",
        widget=forms.Textarea(attrs={"rows": 5})
    )
```

**Checklist Forms :**
- [ ] Docstring sur chaque formulaire
- [ ] `ModelForm` quand possible
- [ ] Widgets avec `autocomplete` pour accessibilité
- [ ] Méthodes `clean_<field>` pour validation personnalisée
- [ ] Validators réutilisables pour patterns communs
- [ ] Messages d'erreur explicites

---

#### 4. URLs (`urls.py`)

```python
# ✅ BONNES PRATIQUES

from django.urls import path
from . import views

app_name = "blog"  # Namespace pour éviter les conflits

urlpatterns = [
    # Noms explicites et cohérents
    path("", views.article_list, name="article_list"),
    path("<slug:slug>/", views.article_detail, name="article_detail"),
    path("create/", views.article_create, name="article_create"),
    path("<slug:slug>/edit/", views.article_update, name="article_update"),
    path("<slug:slug>/delete/", views.article_delete, name="article_delete"),
]
```

**Checklist URLs :**
- [ ] `app_name` défini pour namespace
- [ ] Noms de routes cohérents (`<model>_<action>`)
- [ ] Utilisation de `<slug:slug>` ou `<int:pk>` typés
- [ ] Pas de logique dans urls.py
- [ ] URLs RESTful (verbes implicites)

---

#### 5. Templates Django

```html
<!-- ✅ BONNES PRATIQUES -->

{% extends "base.html" %}
{% load static %}

{% block title %}{{ article.title }} - Blog{% endblock %}

{% block meta_description %}{{ article.excerpt|truncatewords:30 }}{% endblock %}

{% block content %}
<main id="main-content">
    <article>
        <h1>{{ article.title }}</h1>
        
        <!-- Dates formatées et localisées -->
        <time datetime="{{ article.created_at|date:'Y-m-d' }}">
            {{ article.created_at|date:"d F Y" }}
        </time>
        
        <!-- Contenu sécurisé -->
        {{ article.content|linebreaks }}
        
        <!-- Liens avec {% url %} et namespace -->
        <a href="{% url 'blog:article_list' %}">Retour à la liste</a>
        
        <!-- Formulaires avec CSRF -->
        <form method="post" action="{% url 'blog:article_delete' article.slug %}">
            {% csrf_token %}
            <button type="submit">Supprimer</button>
        </form>
    </article>
</main>
{% endblock %}
```

**Checklist Templates :**
- [ ] `{% extends %}` en première ligne
- [ ] `{% load static %}` si fichiers statiques
- [ ] `{% block title %}` défini
- [ ] `{% csrf_token %}` dans tous les formulaires POST
- [ ] `{% url 'namespace:name' %}` au lieu d'URLs en dur
- [ ] Pas de logique complexe (→ template tags)
- [ ] Échappement automatique respecté (pas de `|safe` abusif)

---

### Étape 2 : Sécurité

**Vérifications obligatoires :**

| Règle | Vérification |
|-------|--------------|
| CSRF | `{% csrf_token %}` dans tous les POST |
| XSS | Pas de `|safe` sur données utilisateur |
| SQL Injection | ORM Django, pas de `raw()` avec entrées user |
| Auth | Décorateurs sur vues sensibles |
| Secrets | Pas de secrets dans le code, utiliser `.env` |
| Debug | `DEBUG = False` en production |

```python
# ❌ MAUVAIS - Vulnérable SQL injection
Article.objects.raw(f"SELECT * FROM article WHERE title = '{user_input}'")

# ✅ BON - ORM protégé
Article.objects.filter(title=user_input)

# ❌ MAUVAIS - XSS potentiel
{{ user_content|safe }}

# ✅ BON - Échappement automatique
{{ user_content }}
{{ user_content|linebreaks }}
```

---

### Étape 3 : Performance

**Optimisations à vérifier :**

```python
# ❌ MAUVAIS - N+1 queries
for article in Article.objects.all():
    print(article.author.name)  # 1 requête par article!

# ✅ BON - select_related pour ForeignKey
for article in Article.objects.select_related("author"):
    print(article.author.name)  # 1 seule requête

# ✅ BON - prefetch_related pour ManyToMany
articles = Article.objects.prefetch_related("tags")

# ✅ BON - only() pour limiter les champs
Article.objects.only("title", "slug")

# ✅ BON - exists() au lieu de count() pour vérification
if Article.objects.filter(is_published=True).exists():
    ...
```

**Checklist Performance :**
- [ ] `select_related` pour ForeignKey
- [ ] `prefetch_related` pour ManyToMany
- [ ] `only()` / `defer()` pour limiter les champs
- [ ] `exists()` au lieu de `count() > 0`
- [ ] Pagination sur les listes longues
- [ ] Cache sur les données statiques

---

### Étape 4 : Structure du projet

```
app/
├── __init__.py
├── admin.py          # Configuration admin
├── apps.py           # Configuration de l'app
├── forms.py          # Formulaires
├── models.py         # Modèles
├── services.py       # Logique métier (optionnel)
├── signals.py        # Signaux (optionnel)
├── urls.py           # URLs de l'app
├── views.py          # Vues
├── tests/            # Tests
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_views.py
│   └── test_forms.py
└── templates/
    └── app/
        └── template.html
```

---

### Étape 5 : Rapport de conformité

Après analyse, fournir un rapport :

```
## Rapport Django - [fichier.py]

### ✅ Points conformes
- [liste des bonnes pratiques respectées]

### ⚠️ Points à améliorer
| Catégorie | Problème | Recommandation |
|-----------|----------|----------------|
| Sécurité | ... | ... |
| Performance | ... | ... |
| Convention | ... | ... |

### Statut : CONFORME / À AMÉLIORER
```

---

## Utilisation manuelle

```
/django-check [fichier.py]     # Vérifier un fichier
/django-check --models         # Vérifier tous les models
/django-check --views          # Vérifier toutes les views
/django-check --security       # Audit de sécurité
/django-check --performance    # Audit de performance
```

---

## Commandes de vérification

// turbo
```bash
# Vérifier la syntaxe Django
python manage.py check

# Vérifier les migrations
python manage.py makemigrations --check --dry-run

# Lancer les tests
python manage.py test

# Vérifier le linting
flake8 .
```

---

## Références

- [Django Documentation](https://docs.djangoproject.com/)
- [Two Scoops of Django](https://www.feldroy.com/books/two-scoops-of-django-3-x)
- [Django Security](https://docs.djangoproject.com/en/stable/topics/security/)
- [Django Performance](https://docs.djangoproject.com/en/stable/topics/performance/)
