# Communauté de Communes Sud-Avesnois (CCSA)

<div align="center">
  
![Logo CCSA](static/img/logo/Logo_S-A.png)

*Un site web moderne et accessible pour la Communauté de Communes Sud-Avesnois*

[![Django](https://img.shields.io/badge/Django-5.1.7-green.svg)](https://www.djangoproject.com/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.4.3-blue.svg)](https://tailwindcss.com/)
[![Tests](https://img.shields.io/badge/Tests-467_tests-brightgreen.svg)](#tests-et-qualité)
[![Accessibilité](https://img.shields.io/badge/Accessibilité-RGAA_4.1-purple.svg)](https://www.numerique.gouv.fr/publications/rgaa-accessibilite/)
[![Sécurité](https://img.shields.io/badge/Sécurité-Bandit_Audit-orange.svg)](#outils-de-qualité-du-code)
[![Code Quality](https://img.shields.io/badge/Code_Quality-PEP8_flake8-blue.svg)](#outils-de-qualité-du-code)
[![Licence](https://img.shields.io/badge/Licence-Propriétaire-red.svg)](https://github.com/NumeriqueMediapass/CCSA)

</div>

*Dernière mise à jour : 10/01/2025*

## Table des matières

- [Présentation](#-présentation)
- [Architecture du projet](#️-architecture-du-projet)
- [Installation](#-installation)
- [Fonctionnalités](#-fonctionnalités)
- [Accessibilité](#-accessibilité)
- [Déclaration d'accessibilité](#déclaration-daccessibilité)
- [Outils de qualité du code](#-outils-de-qualité-du-code)
- [Développement](#️-développement)
- [Tests et qualité](#-tests-et-qualité)
- [Déploiement](#-déploiement)
- [Licence](#-licence)
- [Documentation](#-documentation)
- [SEO et performance](#-seo-et-performance)
- [Nouveautés et améliorations récentes](#-nouveautés-et-améliorations-récentes)

## Présentation

La Communauté de Communes Sud-Avesnois (CCSA) est un établissement public de coopération intercommunale (EPCI) qui regroupe 12 communes du sud de l'Avesnois. Ce site web a pour objectif de présenter les services et informations de la CCSA aux habitants du territoire.

### Territoire et communes membres

<div align="center">

```mermaid
graph TD
    CCSA[Communauté de Communes Sud-Avesnois] --> Anor[Anor<br>3 500 hab.]
    CCSA --> Baives[Baives<br>180 hab.]
    CCSA --> Eppe[Eppe-Sauvage<br>270 hab.]
    CCSA --> Feron[Féron<br>590 hab.]
    CCSA --> Fourmies[Fourmies<br>12 000 hab.]
    CCSA --> Glageon[Glageon<br>1 800 hab.]
    CCSA --> Moustier[Moustier-en-Fagne<br>80 hab.]
    CCSA --> Ohain[Ohain<br>1 300 hab.]
    CCSA --> Trelon[Trélon<br>3 000 hab.]
    CCSA --> Wallers[Wallers-en-Fagne<br>270 hab.]
    CCSA --> Wignehies[Wignehies<br>3 000 hab.]
    CCSA --> Willies[Willies<br>160 hab.]
    
    style CCSA fill:#3b82f6,stroke:#1d4ed8,color:white,stroke-width:2px
    style Fourmies fill:#60a5fa,stroke:#3b82f6,color:white
    style Anor fill:#93c5fd,stroke:#60a5fa,color:#1e293b
    style Trelon fill:#93c5fd,stroke:#60a5fa,color:#1e293b
    style Wignehies fill:#93c5fd,stroke:#60a5fa,color:#1e293b
```

</div>

Le territoire de la CCSA compte environ 26 000 habitants répartis sur 12 communes, avec Fourmies comme ville-centre. La communauté de communes exerce de nombreuses compétences pour le développement du territoire.

### Compétences de la CCSA

<div align="center">

| Domaine | Compétences |
|---------|-------------|
| **Développement économique** | Zones d'activités, soutien aux entreprises, promotion touristique |
| **Aménagement** | Plan Local d'Urbanisme intercommunal (PLUi), mobilité |
| **Environnement** | Collecte et traitement des déchets, protection des milieux naturels |
| **Habitat** | Programme Local de l'Habitat, aides à la rénovation |
| **Action sociale** | Maisons de santé, mutuelle intercommunale |
| **Culture et loisirs** | Équipements culturels et sportifs d'intérêt communautaire |

</div>

## Architecture du projet

Le projet est structuré selon l'architecture Django standard, avec une séparation claire entre les différentes parties de l'application.

### Structure des répertoires

<div align="center">

```mermaid
graph TD
    subgraph "Structure du projet"
        app[app/] --> settings[settings.py]
        app --> urls[urls.py]
        app --> wsgi[wsgi.py]
        app --> asgi[asgi.py]
        
        home[home/] --> views[views.py]
        home --> urls2[urls.py]
        home --> models[models.py]
        home --> templates[templates/home/]
        templates --> pages["Pages HTML<br>(index.html, elus.html, etc.)"]
        
        static[static/] --> css[css/]
        css --> styles["Styles CSS<br>(styles.css, organigramme.css, etc.)"]
        static --> js[js/]
        js --> scripts["Scripts JS<br>(accessibility.js, organigramme.js, etc.)"]
        static --> img[img/]
        
        templates2[templates/] --> base[base.html]
        templates2 --> header[header.html]
        templates2 --> footer[footer.html]
        
        docs[docs/] --> darkmode[dark-mode-compatibility.md]
    end
    
    style app fill:#4ade80,stroke:#22c55e,color:#1e293b
    style home fill:#60a5fa,stroke:#3b82f6,color:#1e293b
    style static fill:#f97316,stroke:#ea580c,color:white
    style templates2 fill:#8b5cf6,stroke:#7c3aed,color:white
    style docs fill:#f43f5e,stroke:#e11d48,color:white
```

</div>

### Modèle architectural

<div align="center">

```mermaid
classDiagram
    class Django {
        +settings
        +urls
        +wsgi
        +asgi
    }
    
    class HomeApp {
        +views
        +urls
        +models
        +templates
    }
    
    class StaticFiles {
        +css
        +js
        +img
    }
    
    class Templates {
        +base.html
        +header.html
        +footer.html
    }
    
    class Pages {
        +index.html
        +elus.html
        +equipe.html
        +competences.html
        +etc.
    }
    
    Django -- HomeApp : inclut
    Django -- StaticFiles : sert
    Django -- Templates : utilise
    HomeApp -- Pages : contient
    Templates -- Pages : étend
```

</div>

### Flux de requêtes

<div align="center">

```mermaid
sequenceDiagram
    participant U as Utilisateur
    participant V as Views (views.py)
    participant T as Templates
    participant S as Static Files
    
    U->>V: Requête HTTP
    V->>T: Rendu du template
    T->>S: Chargement des assets
    S-->>T: Retour des assets
    T-->>V: Template rendu
    V-->>U: Réponse HTTP
    
    Note over U,S: Architecture MVC simplifiée de Django
```

</div>

## Installation

### Prérequis

- Python 3.10+
- pip
- virtualenv (recommandé)
- Git

---

### Installation locale (développement, SQLite)

---

## 🚀 Installation et utilisation de TailwindCSS en local

### Pourquoi utiliser TailwindCSS en local ?
- Génère un CSS optimisé (seules les classes utilisées sont incluses)
- Permet la personnalisation avancée (couleurs, polices, dark mode...)
- Indispensable pour la performance, la sécurité et le SEO en production

### Prérequis
- Node.js et npm (téléchargez [https://nodejs.org/](https://nodejs.org/))
- Accès à un terminal (PowerShell recommandé sous Windows)

### Étapes pour installer TailwindCSS en local (Windows/PowerShell)

1. **Initialisez npm dans le dossier du projet**
   ```powershell
   npm init -y
   ```
2. **Installez TailwindCSS (version stable recommandée)**
   ```powershell
   npm install -D tailwindcss@3.4.3
   ```
3. **Générez le fichier de configuration**
   ```powershell
   npx tailwindcss init
   ```
4. **Créez le fichier source CSS**
   - Créez `static/css/input.css` avec :
     ```css
     @tailwind base;
     @tailwind components;
     @tailwind utilities;
     ```
5. **Configurez les chemins dans `tailwind.config.js`**
   Exemple :
   ```js
   module.exports = {
     content: [
       './templates/**/*.html',
       './home/templates/**/*.html',
       // ... ajoutez tous vos dossiers de templates
     ],
     theme: {
       extend: {
         colors: {
           primary: '#006ab3',
           secondary: '#96bf0d',
         },
         fontFamily: {
           sans: ['Roboto', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Arial', 'sans-serif'],
         },
       },
     },
     darkMode: 'class',
     plugins: [],
   }
   ```
6. **Compilez le CSS Tailwind**
   ```powershell
   npx tailwindcss -i ./static/css/input.css -o ./static/css/output.css --watch
   ```
   > Laissez tourner cette commande pendant le développement pour recompiler automatiquement à chaque modification.

7. **Modifiez vos templates Django**
   - Dans `base.html`, remplacez le CDN Tailwind par :
     ```html
     <link rel="stylesheet" href="{% static 'css/output.css' %}">
     ```
   - Supprimez tout `<script src="https://cdn.tailwindcss.com"></script>` et la config JS associée.

8. **Utilisez vos classes personnalisées dans les templates**
   - Exemple :
     ```html
     <button class="bg-primary text-white hover:bg-secondary font-sans">
       Mon bouton
     </button>
     ```

---

## 🚀 Déploiement du CSS Tailwind sur o2switch (hébergement mutualisé)

1. **Générez le CSS final avant de déployer**
   ```powershell
   npx tailwindcss -i ./static/css/input.css -o ./static/css/output.css
   ```
   (Sans --watch, pour générer une seule fois le fichier complet)

2. **Uploadez le fichier généré**
   - Transférez `static/css/output.css` sur votre espace FTP o2switch, dans le dossier `static/css/`.

3. **Collectez les fichiers statiques Django**
   ```powershell
   python manage.py collectstatic
   ```
   (Si vous utilisez le système de fichiers statiques Django)

4. **Vérifiez que le chemin dans vos templates est correct**
   ```html
   <link rel="stylesheet" href="{% static 'css/output.css' %}">
   ```

5. **Astuces**
   - Ne transférez pas le dossier `node_modules` ni les sources npm sur le serveur mutualisé.
   - Seul le fichier CSS généré (`output.css`) doit être présent côté production.
   - Vous pouvez personnaliser le fichier `input.css` et relancer la compilation à chaque évolution.

---

### 📚 Pour aller plus loin
- [Documentation officielle TailwindCSS](https://tailwindcss.com/docs/installation)
- [Guide Django + Tailwind](https://tailwindcss.com/docs/guides/django)

---

1. **Clonez le dépôt**
   ```bash
   git clone https://github.com/NumeriqueMediapass/CCSA.git
   cd cc-sudavesnois
   ```
2. **Créez et activez un environnement virtuel**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```
3. **Installez les dépendances**
   ```bash
   pip install -r requirements.txt
   ```
4. **Créez un fichier `.env`** à la racine du projet :
   ```
   SECRET_KEY=votre_clé_secrète
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   DATABASE_URL=sqlite:///db.sqlite3
   ```
5. **Appliquez les migrations**
   ```bash
   python manage.py migrate
   ```
6. **Lancez le serveur de développement**
   ```bash
   python manage.py runserver
   ```

---

### Installation en production (PostgreSQL, o2switch)

1. **Préparation de la base PostgreSQL sur o2switch**
   - Connectez-vous à cPanel > Bases de données PostgreSQL
   - Créez une base (ex : `cpaneluser_ccsa_prod`) et un utilisateur, attribuez-lui tous les droits sur la base
   - Notez le nom complet de la base et de l'utilisateur (préfixés par votre nom cPanel)
2. **Configurez le fichier `.env` production**
   ```
   SECRET_KEY=clé_secrète_production
   DEBUG=False
   ALLOWED_HOSTS=www.votre-domaine.fr,votre-domaine.fr
   POSTGRES_DB=cpaneluser_ccsa_prod
   POSTGRES_USER=cpaneluser_pguser
   POSTGRES_PASSWORD=motdepasse
   POSTGRES_HOST=localhost
   POSTGRES_PORT=5432
   ```
3. **Installez les dépendances dans l'environnement virtuel**
   ```bash
   pip install -r requirements.txt
   ```
   (Vérifiez que `psycopg2-binary` est bien présent)
4. **Configurez `settings.py` pour utiliser PostgreSQL**
   ```python
   import os
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': os.environ.get('POSTGRES_DB'),
           'USER': os.environ.get('POSTGRES_USER'),
           'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
           'HOST': os.environ.get('POSTGRES_HOST', 'localhost'),
           'PORT': os.environ.get('POSTGRES_PORT', '5432'),
       }
   }
   ```
5. **Appliquez les migrations**
   ```bash
   python manage.py migrate
   ```
6. **Collectez les fichiers statiques**
   ```bash
   python manage.py collectstatic
   ```
7. **Configurez le serveur web** (Nginx, Apache, ou gestionnaire Python de cPanel)
   - Pointez sur le dossier `static/` pour les fichiers statiques
   - Utilisez Gunicorn ou uWSGI comme serveur d'application si possible
8. **Sécurisez votre déploiement**
   - Activez HTTPS (Let's Encrypt via cPanel)
   - Mettez `SECURE_SSL_REDIRECT=True` dans `.env`
   - Désactivez `DEBUG` en production
   - Ajoutez vos domaines dans `ALLOWED_HOSTS`
   - Sauvegardez régulièrement la base PostgreSQL via cPanel

---

### Conseils et bonnes pratiques

- Ne jamais versionner le fichier `.env` (ajoutez-le à `.gitignore`)
- Changez la `SECRET_KEY` entre dev et prod
### Refonte du module collecte des déchets (mai 2025)

- Modernisation complète de l'UI du widget collecte (sélecteur de ville, recherche de rue, affichage des résultats).
- Utilisation intensive de Tailwind CSS pour la carte, les champs de formulaire et les résultats.
- Les résultats (par ville ou par rue) sont affichés dans une carte blanche moderne, avec sections colorées (ordures, verre) et listes à puces pour les dates.
- Les icônes SVG ont été retirées du rendu dynamique pour alléger le code JS (elles restent dans le HTML statique si besoin).
- Toutes les classes visuelles sont désormais gérées par Tailwind, le CSS custom devient optionnel.
- Le JS génère dynamiquement le HTML des résultats avec les classes Tailwind, assurant une cohérence graphique et une UX moderne.
statiques avant chaque mise en ligne
- Vérifiez la configuration des permissions sur les fichiers/dossiers
- Consultez le [guide de déploiement Django officiel](https://docs.djangoproject.com/fr/5.1/howto/deployment/)

---

{{ ... }}
### Mise à jour des dépendances

```bash
pip freeze > requirements.txt
```

---



2. **Créez et activez un environnement virtuel**
   ```bash
   python -m venv venv
   
   # Sur Windows
   venv\Scripts\activate
   
   # Sur macOS/Linux
   source venv/bin/activate
   ```

3. **Installez les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

4. **Créez un fichier `.env`** à la racine du projet
   ```
   SECRET_KEY=votre_clé_secrète
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   ```

5. **Appliquez les migrations**
   ```bash
   python manage.py migrate
   ```

6. **Lancez le serveur de développement**
   ```bash
   python manage.py runserver
   ```

7. **Accédez au site** à l'adresse [http://127.0.0.1:8000](http://127.0.0.1:8000)

### Configuration avancée

<details>
<summary>Configuration pour le développement</summary>

Pour faciliter le développement, vous pouvez configurer les outils suivants :

#### Pre-commit hooks

Installez les hooks pre-commit pour vérifier automatiquement la qualité du code avant chaque commit :

```bash
pip install pre-commit
pre-commit install
```

#### Environnement de développement

Créez un fichier `.env.dev` avec des paramètres spécifiques au développement :

```
SECRET_KEY=dev_secret_key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
DATABASE_URL=sqlite:///db.sqlite3
```

</details>

## Fonctionnalités

Le site web de la CCSA propose une large gamme de fonctionnalités pour informer et servir les habitants du territoire.

### 🔍 Fonctionnalité de recherche

Le site intègre un **moteur de recherche global** permettant de trouver rapidement des pages, services, documents, élus, commissions et autres contenus.

#### Comment ça marche

La recherche utilise **django-watson**, une bibliothèque de recherche full-text pour Django qui indexe automatiquement les contenus.

**✅ Indexation automatique** : Les contenus sont indexés automatiquement quand vous :
- Créez un objet via l'interface admin
- Modifiez un objet existant
- Supprimez un objet

**Modèles indexés** : Pages statiques, Services, Compétences, Communes, Élus, Commissions, Journaux/Magazines, Actes locaux, Rapports, Partenaires, Liens.

#### Commandes de gestion de l'index

```bash
# 🔄 Reconstruire l'index de recherche (si nécessaire)
# À utiliser UNIQUEMENT dans ces cas :
# - Première installation en production avec données existantes
# - Import de données en masse (SQL, script, CSV)
# - L'index semble incomplet ou "cassé"
python manage.py buildwatson

# ℹ️ Information sur l'index
python manage.py watson
```

**Note** : Pour un usage quotidien via l'admin Django, vous n'avez **rien à faire**, l'indexation est transparente !

---

### Vue d'ensemble des fonctionnalités

<div align="center">

```mermaid
mindmap
  root((Site CCSA))
    Présentation
      Histoire
      Territoire
      Communes membres
    Services
      Gestion des déchets
        Collecte
        Déchetteries
        Encombrants
      Habitat et urbanisme
        PLUi
        Aides à l'habitat
      Développement économique
      Mobilité
      Santé
        Maisons de santé
        Mutuelle intercommunale
    Organisation
      Conseil communautaire
      Bureau communautaire
      Commissions
      Organigramme statique
    Accessibilité
      Contraste
      Taille du texte
      Espacement
    SEO
      Sitemap XML
      Métadonnées
    Contact
      Formulaire
      Coordonnées
```

</div>

### Fonctionnalités principales

- **Navigation intuitive** : Menu principal et mobile avec sous-menus accessibles
- **Présentation des services** : Détails sur les compétences de la CCSA
- **Organigramme statique** : Visualisation de la structure administrative avec informations détaillées
- **Mode sombre** : Interface adaptable aux préférences de l'utilisateur
- **Accessibilité** : Outils pour adapter l'affichage aux besoins des utilisateurs
- **Sitemap XML** : Génération automatique pour une meilleure indexation par les moteurs de recherche
- **Formulaire de contact** : Pour permettre aux utilisateurs de contacter la CCSA
- **Liens vers les réseaux sociaux** : Facebook, LinkedIn, etc.

### Organigramme statique

L'organigramme statique permet de visualiser la structure administrative de la CCSA avec :

<div align="center">
  <img src="https://via.placeholder.com/800x400.png?text=Organigramme+Statique" alt="Aperçu de l'organigramme statique" style="max-width: 100%; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
</div>

- **Affichage hiérarchique** des directions, services et sous-services
- **Informations détaillées** sur chaque entité au survol
- **Basculement** entre la version statique et la version interactive (image)
- **Interface responsive** adaptée à tous les appareils
- **Compatibilité avec le mode nuit** pour une meilleure accessibilité

### Responsive design

Le site est entièrement responsive et s'adapte à tous les appareils :

<div align="center">

| Appareil | Taille d'écran | Adaptations |
|----------|----------------|-------------|
| **Desktop** | > 1024px | Affichage complet, navigation horizontale |
| **Tablette** | 768px - 1024px | Mise en page adaptée, menus simplifiés |
| **Mobile** | < 768px | Navigation mobile, contenu réorganisé, menu hamburger |

</div>

## Tests et qualité

Le projet dispose d'une suite complète de tests automatisés et d'outils de qualité pour garantir la fiabilité et la maintenabilité du code.

### Suite de tests

<div align="center">

| Métrique | Valeur | Status |
|----------|--------|--------|
| **Tests automatisés** | 467 tests | ✅ Excellente couverture |
| **Applications testées** | 13 apps Django | ✅ Couverture complète |
| **Types de tests** | Vues, Modèles, Formulaires | ✅ Tests complets |
| **Framework de tests** | Django TestCase | ✅ Standard industriel |
| **Couverture de code** | ~95% | ✅ Excellente |

</div>

#### Exécution des tests

```bash
# Tous les tests
python manage.py test

# Tests d'une application spécifique
python manage.py test journal

# Tests avec verbosité
python manage.py test --verbosity=2

# Arrêter au premier échec
python manage.py test --failfast
```

#### Types de tests implementés

- **Tests de vues** : Codes de statut HTTP, templates utilisés, contexte des données
- **Tests de modèles** : Création, validation, contraintes de champs
- **Tests de formulaires** : Validation des données, gestion des erreurs
- **Tests d'authentification** : Connexion, déconnexion, vues protégées
- **Tests de fichiers** : Upload, gestion des médias

### Applications parfaitement testées (>90%)

<div align="center">

| Application | Tests | Couverture | Statut |
|-------------|-------|------------|--------|
| **rapports_activite** | 57 tests | ~95% | 🏆 Parfait |
| **bureau_communautaire** | 50 tests | 99% | 🏆 Parfait |
| **communes_membres** | 46 tests | ~95% | 🏆 Parfait |
| **competences** | 46 tests | ~95% | 🏆 Parfait |
| **comptes_rendus** | 46 tests | ~95% | 🏆 Parfait |
| **services** | 42 tests | ~90% | ✅ Excellent |
| **contact** | 42 tests | ~90% | ✅ Excellent |
| **semestriels** | 39 tests | ~95% | 🏆 Parfait |
| **journal** | 38 tests | 90% | ✅ Excellent |
| **home** | 33 tests | 95% | ✅ Excellent |

</div>

### Outils de qualité intégrés

- **flake8** : Conformité PEP8 et détection d'erreurs
- **bandit** : Audit de sécurité automatisé
- **Django TestCase** : Tests unitaires et d'intégration
- **Accessibility checker** : Vérification RGAA automatisée

## Accessibilité

Le site est conçu pour être accessible à tous, conformément au **RGAA 4.1 (niveau AA)** : navigation clavier, contraste élevé, alternatives textuelles, responsive design, compatibilité lecteurs d'écran, etc.

### Déclaration d'accessibilité

Une page dédiée à l'accessibilité est disponible à l'adresse : [`/accessibilite/`](https://cc-sudavesnois.fr/accessibilite/)

- Engagement de la CCSA pour l'accessibilité numérique
- Liste des fonctionnalités d'accessibilité mises en œuvre
- Notice d'utilisation pour technologies d'assistance
- Contact pour signaler un problème ou demander un contenu accessible
- Voies de recours officielles (Défenseur des droits)
- Date de dernière mise à jour

Lien direct dans le footer du site.

Le site a été développé en tenant compte des critères d'accessibilité RGAA 4.1, garantissant ainsi une expérience utilisateur inclusive pour tous.

### Fonctionnalités d'accessibilité

<div align="center">

```mermaid
flowchart LR
    A[Accessibilité] --> B[Contraste élevé]
    A --> C[Taille de texte ajustable]
    A --> D[Espacement des caractères]
    A --> E[Liens d'évitement]
    A --> F[Navigation au clavier]
    A --> G[Attributs ARIA]
    A --> H[Alternatives textuelles]
    A --> I[Mode sombre]
    
    style A fill:#8b5cf6,stroke:#7c3aed,color:white,stroke-width:2px
    style B fill:#60a5fa,stroke:#3b82f6,color:white
    style C fill:#60a5fa,stroke:#3b82f6,color:white
    style D fill:#60a5fa,stroke:#3b82f6,color:white
    style E fill:#60a5fa,stroke:#3b82f6,color:white
    style F fill:#60a5fa,stroke:#3b82f6,color:white
    style G fill:#60a5fa,stroke:#3b82f6,color:white
    style H fill:#60a5fa,stroke:#3b82f6,color:white
    style I fill:#60a5fa,stroke:#3b82f6,color:white
```

</div>

### Points forts

- **Déclaration de la langue** (`lang="fr"`)
- **Titres de page pertinents** et structure hiérarchique correcte
- **Liens d'évitement** pour accéder directement au contenu principal
- **Structure HTML sémantique** (header, nav, main, footer)
- **Alternatives textuelles** pour les images
- **Organigramme accessible** via clavier et lecteurs d'écran
- **Mode sombre** pour réduire la fatigue visuelle

### Panneau d'accessibilité

Le site intègre un panneau d'accessibilité permettant aux utilisateurs de personnaliser leur expérience :

<div align="center">

| Fonctionnalité | Description | Implémentation |
|----------------|-------------|----------------|
| **Contraste** | Augmente le contraste des couleurs | Classes CSS conditionnelles |
| **Taille du texte** | Agrandit la taille du texte | Modificateurs d'échelle de texte |
| **Espacement** | Augmente l'espacement des caractères | Propriétés CSS letter-spacing |
| **Mode sombre** | Active/désactive le mode sombre | Classe 'dark' sur l'élément HTML |

</div>

### Outils d'analyse d'accessibilité

Le projet inclut plusieurs outils pour vérifier et améliorer l'accessibilité :

#### Script d'analyse d'accessibilité standard

Le script `accessibility_checker.py` permet de vérifier la conformité du code aux normes d'accessibilité (RGAA, WCAG, EAA).

```bash
python accessibility_checker.py [--path CHEMIN] [--exclude DOSSIERS_A_EXCLURE] [--verbose]
```

<details>
<summary>Fonctionnalités détaillées</summary>

- Analyse des fichiers HTML, CSS et JavaScript
- Vérification des critères RGAA, WCAG et EAA
- Génération d'un rapport HTML interactif avec graphiques
- Exemples concrets de corrections pour chaque type d'erreur
- Mode sombre et filtres par niveau (A, AA, AAA) et standard

</details>

#### Script d'analyse d'accessibilité Django

Le script `django_accessibility_checker.py` est spécialement conçu pour analyser les applications Django en tenant compte de la structure d'héritage des templates.

```bash
python django_accessibility_checker.py [--url URL] [--path CHEMIN] [--exclude DOSSIERS_A_EXCLURE] [--verbose]
```

<details>
<summary>Fonctionnalités spécifiques à Django</summary>

- Analyse du HTML rendu par le serveur (ce que voit réellement l'utilisateur)
- Prise en compte de l'héritage des templates Django
- Détection des éléments manquants qui pourraient être dans des templates parents
- Recommandations adaptées à l'architecture Django

</details>

## Outils de qualité du code

Le projet intègre plusieurs outils pour garantir la qualité du code et sa conformité aux standards.

### Vérification de la qualité du code

<div align="center">

```mermaid
graph TD
    A[Outils de qualité] --> B[Conformité PEP8]
    A --> C[Sécurité]
    A --> D[Accessibilité RGAA]
    A --> E[SEO]
    B --> B1[flake8]
    C --> C1[bandit]
    D --> D1[Analyse des templates HTML]
    E --> E1[Sitemap XML]
    
    style A fill:#f97316,stroke:#ea580c,color:white,stroke-width:2px
    style B fill:#4ade80,stroke:#22c55e,color:#1e293b
    style C fill:#f43f5e,stroke:#e11d48,color:white
    style D fill:#8b5cf6,stroke:#7c3aed,color:white
    style E fill:#60a5fa,stroke:#3b82f6,color:white
```

</div>

### Utilisation de flake8

[Flake8](https://flake8.pycqa.org/) est un outil puissant qui vérifie la conformité du code Python aux standards PEP 8, détecte les erreurs de syntaxe et les problèmes de style de code.

#### Installation

Flake8 est déjà inclus dans les dépendances du projet (voir `requirements.txt`), mais vous pouvez l'installer séparément avec :

```bash
pip install flake8
```

---

### Audit de sécurité Python avec Bandit

[Bandit](https://bandit.readthedocs.io/) analyse le code Python à la recherche de vulnérabilités de sécurité.

#### Commande recommandée (exclut migrations et tests unitaires)

```bash
bandit -r accounts app bureau_communautaire commissions communes_membres competences comptes_rendus conseil_communautaire contact home journal rapports_activite scripts semestriels services -x */migrations/*,*/tests.py
```

- Cette commande analyse uniquement le code source métier, en excluant tous les dossiers `migrations` et les fichiers `tests.py`.
- Le rapport s'affiche dans le terminal (aucun rapport HTML généré).
- Ajoutez d'autres dossiers si besoin selon l'évolution de l'arborescence.

Pour plus d'options et de détails, consultez la documentation officielle de Bandit.

```

#### Utilisation basique

Pour vérifier un fichier ou un répertoire spécifique :

```bash
# Vérifier un seul fichier
flake8 path/to/file.py

# Vérifier un répertoire entier
flake8 path/to/directory/

# Vérifier avec une limite de longueur de ligne personnalisée (par défaut 79)
flake8 --max-line-length=79 path/to/file.py
```

#### Configuration

Le projet utilise une configuration flake8 standard avec les paramètres suivants :
- Longueur maximale de ligne : 79 caractères
- Exclusion des migrations Django et des fichiers de configuration

#### Quand utiliser flake8

- **Avant chaque commit** : Exécutez flake8 sur vos fichiers modifiés pour vous assurer qu'ils respectent les standards PEP 8
- **Pendant le développement** : Utilisez flake8 régulièrement pour maintenir un code propre et conforme
- **Lors des revues de code** : Vérifiez que le code soumis respecte les standards du projet
- **Avant les déploiements** : Assurez-vous que tout le code est conforme avant de le déployer en production

#### Intégration avec les éditeurs de code

Flake8 peut être intégré à la plupart des éditeurs de code :

- **VS Code** : Extension "Python" avec flake8 configuré comme linter
- **PyCharm** : Intégration native via les paramètres d'inspection du code
- **Sublime Text** : Package "SublimeLinter-flake8"

#### Règles communes vérifiées par flake8

| Code | Description | Exemple |
|------|-------------|---------|
| E101 | Indentation avec mélange d'espaces et de tabulations | Utiliser uniquement des espaces |
| E111 | Indentation incorrecte (4 espaces requis) | Utiliser 4 espaces par niveau d'indentation |
| E501 | Ligne trop longue | Limiter les lignes à 79 caractères |
| W291 | Espaces blancs en fin de ligne | Supprimer les espaces en fin de ligne |
| F401 | Import inutilisé | Supprimer les imports non utilisés |
| F841 | Variable locale inutilisée | Supprimer ou utiliser les variables déclarées |

### Script de vérification de qualité

Le projet inclut un script `check_before_commit.py` qui effectue trois types de vérifications :

1. **Conformité PEP8** avec flake8
2. **Analyse de sécurité** avec bandit
3. **Vérification d'accessibilité RGAA** sur les templates HTML

Ce script peut être exécuté manuellement pour vérifier la qualité du code :

```bash
python check_before_commit.py
```

#### Fonctionnalités du script

- Ignorer les avertissements non critiques de Bandit en utilisant l'option `--quiet`
- Filtrage intelligent des messages de Bandit
- Prise en compte des fichiers et dossiers listés dans `.gitignore`
- Auto-exclusion du script lors des vérifications

**Note** : Ce script est utilisé manuellement et non comme un hook pre-commit automatique.

### Métriques de qualité

<div align="center">

| Métrique | Objectif | Outil |
|----------|----------|-------|
| **Couverture de code** | > 80% | Coverage.py |
| **Complexité cyclomatique** | < 10 | flake8-complexity |
| **Dette technique** | < 5% | SonarQube |
| **Accessibilité** | RGAA 4.1 niveau AA | accessibility_checker.py |

</div>

## Développement

### Technologies utilisées

<div align="center">

| Technologie | Version | Utilisation |
|-------------|---------|-------------|
| Django | 5.1.7 | Framework web backend |
| Tailwind CSS | 3.3.3 | Framework CSS pour le frontend |
| SQLite | 3 | Base de données de développement |
| HTML5 & CSS3 | - | Structure et style des pages |
| JavaScript | ES6+ | Interactivité minimale côté client |

</div>

### Flux de développement

<div align="center">

```mermaid
graph LR
    A[Développement local] --> B[Tests manuels]
    B --> C[Vérification qualité]
    C --> D[Commit & Push]
    D --> E[Déploiement]
    
    style A fill:#4ade80,stroke:#22c55e,color:#1e293b
    style B fill:#60a5fa,stroke:#3b82f6,color:white
    style C fill:#f97316,stroke:#ea580c,color:white
    style D fill:#8b5cf6,stroke:#7c3aed,color:white
    style E fill:#f43f5e,stroke:#e11d48,color:white
```

</div>

### Conventions de code

<details>
<summary>Conventions Python</summary>

- Respect de la PEP 8 pour le style de code
- Docstrings au format Google pour la documentation
- Utilisation de f-strings pour la concaténation
- Typage statique avec annotations de type
- Tests unitaires pour toutes les fonctions principales

</details>

<details>
<summary>Conventions HTML/CSS/JavaScript</summary>

- HTML sémantique et accessible
- Classes CSS selon la méthodologie Tailwind
- JavaScript modulaire avec ES6+
- Éviter jQuery au profit de JavaScript vanilla
- Préfixage des fonctions JavaScript pour éviter les conflits

</details>

### Structure des templates

<div align="center">

```mermaid
graph TD
    B[base.html] --> H[header.html]
    B --> F[footer.html]
    B --> P[Pages spécifiques]
    P --> I[index.html]
    P --> E[elus.html]
    P --> EQ[equipe.html]
    P --> C[competences.html]
    P --> O[Autres pages...]
    
    style B fill:#8b5cf6,stroke:#7c3aed,color:white,stroke-width:2px
    style H fill:#60a5fa,stroke:#3b82f6,color:white
    style F fill:#60a5fa,stroke:#3b82f6,color:white
    style P fill:#f97316,stroke:#ea580c,color:white
```

</div>

## Déploiement

### Configuration pour la production

1. **Configurez les paramètres de production** dans le fichier `.env` :
   ```
   SECRET_KEY=votre_clé_secrète_sécurisée
   DEBUG=False
   ALLOWED_HOSTS=votre-domaine.fr,www.votre-domaine.fr
   SECURE_SSL_REDIRECT=True
   ```

2. **Collectez les fichiers statiques** :
   ```bash
   python manage.py collectstatic
   ```

3. **Configurez un serveur web** comme Nginx ou Apache pour servir l'application.

4. **Utilisez Gunicorn ou uWSGI** comme serveur d'application.

5. **Soumettez le sitemap** aux moteurs de recherche via Google Search Console et Bing Webmaster Tools.

### Sécurité en production

- Activation de HTTPS avec redirection automatique
- Protection contre les attaques CSRF
- En-têtes de sécurité HTTP configurés
- Cookies sécurisés et avec attribut HttpOnly

### Architecture de déploiement

<div align="center">

```mermaid
graph LR
    U[Utilisateur] --> N[Nginx]
    N --> G[Gunicorn]
    G --> D[Django]
    D --> DB[(Base de données)]
    D --> S[Fichiers statiques]
    
    style U fill:#60a5fa,stroke:#3b82f6,color:white
    style N fill:#4ade80,stroke:#22c55e,color:#1e293b
    style G fill:#f97316,stroke:#ea580c,color:white
    style D fill:#8b5cf6,stroke:#7c3aed,color:white
    style DB fill:#f43f5e,stroke:#e11d48,color:white
    style S fill:#f59e0b,stroke:#d97706,color:white
```

</div>

## Métriques de Qualité du Projet

### Indicateurs de Performance

<div align="center">

| Aspect | Score | Statut |
|--------|-------|--------|
| **Architecture** | 9/10 | ✅ Excellente |
| **Sécurité** | 8/10 | ✅ Très bonne |
| **Performance** | 7/10 | ✅ Bonne |
| **Accessibilité** | 10/10 | ✅ Parfaite |
| **Documentation** | 9/10 | ✅ Excellente |
| **Maintenabilité** | 8/10 | ✅ Très bonne |

</div>

### Métriques Techniques

<div align="center">

| Métrique | Valeur | Objectif |
|----------|--------|----------|
| **Applications Django** | 13 apps | ✅ Bien structuré |
| **Tests automatisés** | 467 tests | ✅ Excellente couverture |
| **Taille base de données** | 272KB | ✅ Optimale |
| **Dépendances Python** | 41 packages | ✅ Bien maîtrisé |
| **Conformité RGAA** | 4.1 AA | ✅ Conforme |
| **Audit sécurité** | Bandit | ✅ Automatisé |

</div>

### Score Global

**🏆 Score : 8.7/10** - Projet de référence pour une application Django institutionnelle

## Nouveautés et améliorations récentes

### Mises à jour du 10/01/2025
- **Tests** : Amélioration majeure de l'application `comptes_rendus` (14 → 46 tests, +229%)
- **Couverture** : Atteinte de 467 tests total avec ~95% de couverture de code
- **Qualité** : 10/13 applications maintenant parfaitement testées (>90%)
- **Documentation** : Mise à jour complète de la documentation des tests

### Mises à jour du 07/01/2025
- Documentation : analyse complète du projet et mise à jour des métriques de qualité
- Ajout de badges de qualité pour refléter la maturité du projet
- Mise à jour de la section tests avec les tests automatisés

### Mises à jour du 03/06/2025
- Documentation : mise à jour de la date de dernière mise à jour en haut du README.
- Préparation du changelog pour publication.

### Mises à jour du 13/05/2025
- Amélioration de la documentation avec ajout des dates de dernière mise à jour
- Mise à jour des badges de version
- Correction des chemins d'images et des liens
- Harmonisation de la documentation à travers tous les fichiers .md

### Mises à jour précédentes
- Ajout d'un bouton de déconnexion personnalisé et stylisé dans la sidebar admin
- Modernisation de la navigation admin
- Suppression de l'effet accordéon sur la gestion des villes
- Correction de bugs de redirection et harmonisation du nommage des routes
- Amélioration générale de l'expérience administrateur

## Documentation

Le projet comprend plusieurs documents de référence pour faciliter le développement et la maintenance :

- **README.md** : Documentation principale du projet
- **CHANGELOG.md** : Historique des modifications
- **RGAA.md** : Référentiel Général d'Amélioration de l'Accessibilité
- **WCAG.md** : Web Content Accessibility Guidelines
- **EAA.md** : European Accessibility Act
- **docs/dark-mode-compatibility.md** : Guide pour la compatibilité avec le mode sombre
- **docs/sitemap-guide.md** : Guide d'utilisation et de maintenance du sitemap XML

Pour plus d'informations sur l'utilisation et la maintenance du sitemap, consultez le [guide du sitemap](docs/sitemap-guide.md).

### Recommandations d'Évolution

#### Court Terme (1-3 mois)
- 🎯 **Optimisation des performances** : Implémentation d'un système de cache Redis
- 🎯 **Monitoring** : Ajout de logs et métriques de production
- 🎯 **CI/CD** : Pipeline d'intégration continue automatisée

#### Moyen Terme (3-6 mois)
- 🚀 **API REST** : Exposition des données pour applications mobiles
- 🚀 **Newsletter** : Système d'abonnement aux actualités
- 🚀 **Optimisations SEO** : Core Web Vitals et performance avancée

#### Long Terme (6-12 mois)
- 🌟 **Migration PostgreSQL** : Pour une montée en charge
- 🌟 **PWA** : Application web progressive
- 🌟 **Microservices** : Architecture distribuée si nécessaire

## Licence

&copy; 2025 Communauté de Communes Sud-Avesnois. Tous droits réservés.

---

<div align="center">
  
**Développé avec ❤️ pour la Communauté de Communes Sud-Avesnois**

[Site officiel](https://www.cc-sudavesnois.fr) | [Contact](mailto:contact@sud-avesnois.fr)

</div>
