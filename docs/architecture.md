# Architecture du Projet CCSA

## 📋 Vue d'ensemble

Le projet CCSA suit une **architecture Django moderne et modulaire**, structurée en 12 applications métier distinctes. Cette architecture privilégie la séparation des responsabilités, la réutilisabilité et la maintenabilité.

## 🏗️ Architecture Générale

```mermaid
graph TB
    subgraph "Client Layer"
        Browser[Navigateur Web]
        Mobile[Appareils Mobiles]
    end
    
    subgraph "Presentation Layer"
        Templates[Templates Django]
        Static[Fichiers Statiques]
        CSS[Tailwind CSS]
        JS[JavaScript]
    end
    
    subgraph "Application Layer"
        URLDispatcher[URL Dispatcher]
        Views[Views Django]
        Forms[Formulaires]
        Middleware[Middleware Stack]
    end
    
    subgraph "Business Logic Layer"
        Models[Modèles Django]
        Services[Services Métier]
        Utils[Utilitaires]
    end
    
    subgraph "Data Layer"
        SQLite[Base SQLite]
        Media[Fichiers Média]
        Cache[Cache Session]
    end
    
    Browser --> Templates
    Mobile --> Templates
    Templates --> Views
    Static --> CSS
    Static --> JS
    URLDispatcher --> Views
    Views --> Models
    Views --> Forms
    Models --> SQLite
    Models --> Media
    
    style Browser fill:#3498db,stroke:#2980b9,color:white
    style Templates fill:#2ecc71,stroke:#27ae60,color:white
    style Views fill:#e74c3c,stroke:#c0392b,color:white
    style Models fill:#f39c12,stroke:#e67e22,color:white
    style SQLite fill:#9b59b6,stroke:#8e44ad,color:white
```

## 🔧 Structure des Applications

### Applications Principales

```mermaid
graph LR
    subgraph "Core Apps"
        APP[app/] --> HOME[home/]
        APP --> ACCOUNTS[accounts/]
    end
    
    subgraph "Content Apps"
        JOURNAL[journal/]
        CONSEIL[conseil_communautaire/]
        BUREAU[bureau_communautaire/]
        COMMUNES[communes_membres/]
    end
    
    subgraph "Service Apps"
        CONTACT[contact/]
        SERVICES[services/]
        COMMISSIONS[commissions/]
        COMPETENCES[competences/]
    end
    
    subgraph "Publication Apps"
        SEMESTRIELS[semestriels/]
        COMPTES[comptes_rendus/]
        RAPPORTS[rapports_activite/]
    end
    
    HOME --> JOURNAL
    HOME --> CONSEIL
    HOME --> BUREAU
    HOME --> COMMUNES
    
    style APP fill:#e74c3c,stroke:#c0392b,color:white
    style HOME fill:#2ecc71,stroke:#27ae60,color:white
    style ACCOUNTS fill:#3498db,stroke:#2980b9,color:white
```

### Responsabilités par Application

| Application | Responsabilité | Modèles Principaux |
|-------------|----------------|-------------------|
| **app** | Configuration Django, URL routing | Settings, URLConf |
| **home** | Pages principales, navigation | Page statiques |
| **accounts** | Authentification, utilisateurs | CustomUser |
| **conseil_communautaire** | Gestion des élus | Ville, ConseilMembre |
| **journal** | Publications périodiques | Journal, JournalPage |
| **bureau_communautaire** | Bureau et documents | Document, Membre |
| **communes_membres** | 12 communes du territoire | Commune, ActeLocal |
| **contact** | Formulaire de contact | Message, ContactForm |
| **commissions** | Commissions CCSA | Commission, Réunion |
| **competences** | Compétences intercommunales | Domaine, Compétence |
| **semestriels** | Publications semestrielles | SemestrielPage, Event |
| **comptes_rendus** | Comptes-rendus conseils | CompteRendu, Séance |
| **services** | Services aux habitants | Service, Prestation |
| **rapports_activite** | Rapports annuels | RapportActivite |

## 🔀 Flux de Données

```mermaid
sequenceDiagram
    participant U as Utilisateur
    participant N as Nginx
    participant D as Django
    participant V as Views
    participant M as Models
    participant DB as Database
    participant T as Templates
    
    U->>N: Requête HTTP
    N->>D: Proxy vers Django
    D->>V: URL Routing
    V->>M: Logique Métier
    M->>DB: Requête SQL
    DB-->>M: Données
    M-->>V: Objets Python
    V->>T: Context Data
    T-->>V: HTML Rendu
    V-->>D: HttpResponse
    D-->>N: Réponse
    N-->>U: Page Web
```

## 📁 Structure des Répertoires

### Hiérarchie Complète

```
cc-sudavesnois/
├── app/                          # Configuration Django
│   ├── __init__.py
│   ├── settings.py              # Paramètres globaux
│   ├── urls.py                  # URL racine
│   ├── wsgi.py                  # WSGI application
│   ├── asgi.py                  # ASGI application
│   └── context_processors.py    # Processeurs de contexte
├── home/                         # Application principale
│   ├── views.py                 # Vues principales
│   ├── urls.py                  # Routes
│   ├── models.py                # Modèles (vide)
│   ├── sitemaps.py              # Sitemap XML
│   └── templates/home/          # Templates spécifiques
├── accounts/                     # Authentification
│   ├── models.py                # CustomUser
│   ├── views.py                 # Connexion/Déconnexion
│   ├── forms.py                 # Formulaires auth
│   └── templates/accounts/      # Templates auth
├── [autres_apps]/               # Autres applications Django
├── templates/                    # Templates globaux
│   ├── base.html               # Template de base
│   ├── header.html             # En-tête commun
│   ├── footer.html             # Pied de page
│   └── admin_*.html            # Templates admin
├── static/                       # Fichiers statiques
│   ├── css/                    # Styles CSS
│   ├── js/                     # Scripts JavaScript
│   ├── img/                    # Images
│   └── icones/                 # Icônes
├── media/                        # Fichiers uploadés
├── docs/                         # Documentation
├── requirements.txt              # Dépendances Python
├── package.json                  # Dépendances Node.js
├── tailwind.config.js           # Configuration Tailwind
└── manage.py                     # Script de gestion Django
```

## 🔧 Configuration Système

### Settings Principal

Le fichier `app/settings.py` centralise toute la configuration :

```python
# Configuration des applications
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    'widget_tweaks',
    # Applications métier
    'home',
    'accounts',
    'conseil_communautaire',
    'journal',
    # ... autres apps
]

# Middleware Stack
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
```

### Routing des URLs

```mermaid
graph TD
    Root[app/urls.py] --> Admin[ccsa-admin/]
    Root --> Home[/ - home.urls]
    Root --> Accounts[/ - accounts.urls]
    Root --> Sitemap[sitemap.xml]
    Root --> Robots[robots.txt]
    Root --> Council[/ - conseil_communautaire.urls]
    Root --> Journal[/ - journal.urls]
    Root --> Bureau[/ - bureau_communautaire.urls]
    Root --> Communes[/ - communes_membres.urls]
    Root --> Services[services/ - services.urls]
    Root --> Contact[/ - contact.urls]
    
    style Root fill:#e74c3c,stroke:#c0392b,color:white
    style Admin fill:#f39c12,stroke:#e67e22,color:white
```

## 🗄️ Architecture de Base de Données

### Modèle Conceptuel

```mermaid
erDiagram
    CustomUser ||--o{ Journal : "crée"
    CustomUser ||--o{ ConseilMembre : "gère"
    
    Ville ||--o{ ConseilMembre : "représente"
    Ville ||--o{ ActeLocal : "publie"
    
    Journal ||--o{ JournalPage : "contient"
    
    Commission ||--o{ Reunion : "organise"
    
    Service ||--o{ Prestation : "offre"
    
    CustomUser {
        int id PK
        string username
        string email
        string first_name
        string last_name
        boolean is_staff
        boolean is_active
        datetime date_joined
    }
    
    Ville {
        int id PK
        string nom
        string slug
        int population
        text description
    }
    
    ConseilMembre {
        int id PK
        string first_name
        string last_name
        string fonction
        int ville_id FK
        file photo
    }
    
    Journal {
        int id PK
        string title
        string slug
        file document
        file cover_image
        date date_publication
        int created_by_id FK
    }
```

## 🏛️ Architecture des Templates

### Hiérarchie d'Héritage

```mermaid
graph TD
    BASE[base.html] --> HOME[home/index.html]
    BASE --> ELUS[home/elus.html]
    BASE --> JOURNAL[journal/journal.html]
    BASE --> ADMIN[admin_base.html]
    
    ADMIN --> ADMIN_CITIES[conseil_communautaire/admin_cities_list.html]
    ADMIN --> ADMIN_JOURNAL[journal/admin_journal_list.html]
    
    BASE --> HEADER[header.html]
    BASE --> FOOTER[footer.html]
    BASE --> COOKIE[cookie_banner.html]
    
    style BASE fill:#2ecc71,stroke:#27ae60,color:white
    style ADMIN fill:#e74c3c,stroke:#c0392b,color:white
```

### Composants Réutilisables

| Template | Utilisation | Inclusions |
|----------|-------------|-----------|
| `base.html` | Template racine | Meta tags, CSS, JS |
| `header.html` | Navigation principale | Menu, logo, recherche |
| `footer.html` | Pied de page | Liens, contact, mentions |
| `cookie_banner.html` | Conformité RGPD | Bannière cookies |
| `admin_base.html` | Interface admin | Sidebar, navigation admin |

## 🔐 Architecture de Sécurité

### Couches de Sécurité

```mermaid
graph TD
    subgraph "Frontend Security"
        CSRF[Protection CSRF]
        XSS[Protection XSS]
        CSP[Content Security Policy]
    end
    
    subgraph "Application Security"
        AUTH[Authentification Django]
        PERM[Permissions & Groupes]
        FORM[Validation Formulaires]
    end
    
    subgraph "Infrastructure Security"
        HTTPS[HTTPS/TLS]
        HEADERS[Security Headers]
        FIREWALL[Firewall]
    end
    
    subgraph "Data Security"
        HASH[Hash Passwords]
        ENCRYPT[Encryption at Rest]
        BACKUP[Backups Sécurisés]
    end
    
    CSRF --> AUTH
    XSS --> PERM
    AUTH --> HTTPS
    PERM --> HASH
    
    style CSRF fill:#e74c3c,stroke:#c0392b,color:white
    style AUTH fill:#3498db,stroke:#2980b9,color:white
    style HTTPS fill:#2ecc71,stroke:#27ae60,color:white
    style HASH fill:#f39c12,stroke:#e67e22,color:white
```

## 🚀 Architecture de Performance

### Optimisations Mises en Place

1. **Static Files Management**
   - Collecte automatique des fichiers statiques
   - Compression CSS/JS en production
   - Versioning des assets

2. **Database Optimization**
   - Index sur les champs fréquemment consultés
   - Requêtes optimisées avec select_related
   - Lazy loading des relations

3. **Caching Strategy** (À implémenter)
   - Cache Redis pour les sessions
   - Cache des vues coûteuses
   - Cache des requêtes fréquentes

4. **Frontend Performance**
   - Tailwind CSS compilé localement
   - Images optimisées
   - JavaScript minifié

## 📊 Métriques d'Architecture

| Métrique | Valeur | Évaluation |
|----------|--------|------------|
| **Couplage** | Faible | ✅ Excellent |
| **Cohésion** | Élevée | ✅ Excellent |
| **Complexité** | Modérée | ✅ Maîtrisée |
| **Réutilisabilité** | Élevée | ✅ Excellent |
| **Maintenabilité** | Élevée | ✅ Excellent |
| **Testabilité** | Élevée | ✅ 54 tests |

---

## 🔧 Points d'Amélioration Identifiés

### Court Terme
- Implémentation du cache Redis
- Optimisation des requêtes N+1
- Ajout de logging structuré

### Moyen Terme  
- Migration vers PostgreSQL
- API REST avec Django REST Framework
- Containerisation Docker

### Long Terme
- Architecture microservices
- Event-driven architecture
- Scalabilité horizontale

---

*Documentation architecture - Dernière mise à jour : 07/01/2025* 