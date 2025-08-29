# Guide Frontend - Configuration Tailwind CSS

## Vue d'ensemble

Le projet CCSA utilise **Tailwind CSS 3.4.3** comme framework de styles principal, permettant un développement rapide avec un design system cohérent et des performances optimisées.

### Configuration Actuelle
- **Version** : Tailwind CSS 3.4.3
- **Build system** : PostCSS + Autoprefixer
- **Mode sombre** : Activé (classe)
- **Taille finale** : ~127KB (optimisé)
- **Personnalisation** : Couleurs CCSA, polices

## Architecture CSS

```mermaid
graph TB
    A[input.css] --> B[Tailwind Directives]
    B --> C[@tailwind base]
    B --> D[@tailwind components]
    B --> E[@tailwind utilities]
    
    F[tailwind.config.js] --> G[Theme Configuration]
    G --> H[Colors CCSA]
    G --> I[Fonts Custom]
    G --> J[Extensions]
    
    K[PostCSS] --> L[Autoprefixer]
    L --> M[output.css]
    M --> N[Production 127KB]
```

## Configuration Principale

### tailwind.config.js (35 lignes)

```javascript
/** @type {import('tailwindcss').Config} */
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
        primary: '#006ab3',      // Bleu CCSA officiel
        secondary: '#96bf0d',    // Vert CCSA officiel
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

### Fichiers Sources

#### static/css/input.css (3 lignes)
```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

#### static/css/output.css (2500+ lignes)
- Fichier généré automatiquement
- Contient tous les utilitaires Tailwind
- Optimisé pour la production
- Classes non utilisées supprimées

## Système de Couleurs

### Couleurs Principales CCSA

```css
/* Couleurs officielles intégrées */
:root {
  --color-primary: #006ab3;    /* Bleu institutionnel */
  --color-secondary: #96bf0d;  /* Vert dynamique */
}
```

### Usage dans les Classes
```html
<!-- Backgrounds -->
<div class="bg-primary">Fond bleu CCSA</div>
<div class="bg-secondary">Fond vert CCSA</div>

<!-- Textes -->
<h1 class="text-primary">Titre bleu</h1>
<p class="text-secondary">Texte vert</p>

<!-- Bordures -->
<button class="border-primary">Bordure bleue</button>
<input class="focus:ring-secondary">Focus vert</input>
```

### Dégradés Personnalisés
```html
<!-- Dégradé institutionnel -->
<div class="bg-gradient-to-r from-primary to-secondary">
  Dégradé bleu vers vert
</div>

<!-- Avec transparence -->
<div class="bg-primary/10">Bleu 10% d'opacité</div>
```

## Typographie

### Police Principale
- **Famille** : Roboto (Google Fonts)
- **Fallbacks** : -apple-system, BlinkMacSystemFont, Segoe UI, Arial, sans-serif
- **Usage** : `font-sans` (par défaut)

### Hiérarchie Typographique
```html
<!-- Titres -->
<h1 class="text-4xl font-bold text-primary">Titre Principal</h1>
<h2 class="text-3xl font-semibold text-gray-800">Sous-titre</h2>
<h3 class="text-2xl font-medium text-gray-700">Section</h3>

<!-- Corps de texte -->
<p class="text-base text-gray-600 leading-relaxed">Paragraphe</p>
<p class="text-sm text-gray-500">Texte secondaire</p>
```

## Composants Récurrents

### Boutons Système

#### Bouton Principal
```html
<button class="
  bg-primary hover:bg-primary/90 
  text-white font-medium 
  px-6 py-3 rounded-lg 
  transition-colors duration-200
  focus:ring-2 focus:ring-primary focus:ring-offset-2
">
  Action Principale
</button>
```

#### Bouton Secondaire
```html
<button class="
  bg-secondary hover:bg-secondary/90 
  text-white font-medium 
  px-6 py-3 rounded-lg 
  transition-colors duration-200
">
  Action Secondaire
</button>
```

#### Bouton Outline
```html
<button class="
  border-2 border-primary text-primary 
  hover:bg-primary hover:text-white 
  px-6 py-3 rounded-lg 
  transition-all duration-200
">
  Bouton Outline
</button>
```

### Cards et Conteneurs

#### Card Standard
```html
<div class="
  bg-white rounded-xl shadow-lg 
  p-6 border border-gray-200
  hover:shadow-xl transition-shadow duration-200
">
  <h3 class="text-xl font-semibold text-primary mb-4">Titre Card</h3>
  <p class="text-gray-600">Contenu de la carte...</p>
</div>
```

#### Card avec Image
```html
<div class="bg-white rounded-xl shadow-lg overflow-hidden">
  <img src="image.jpg" class="w-full h-48 object-cover">
  <div class="p-6">
    <h3 class="text-xl font-semibold text-primary mb-2">Titre</h3>
    <p class="text-gray-600">Description...</p>
  </div>
</div>
```

### Formulaires

#### Input Standard
```html
<input type="text" class="
  w-full px-4 py-3 
  border border-gray-300 rounded-lg 
  focus:ring-2 focus:ring-primary focus:border-transparent
  placeholder-gray-400
" placeholder="Votre texte...">
```

#### Textarea
```html
<textarea class="
  w-full px-4 py-3 
  border border-gray-300 rounded-lg 
  focus:ring-2 focus:ring-primary focus:border-transparent
  resize-vertical min-h-[120px]
" placeholder="Votre message..."></textarea>
```

#### Select
```html
<select class="
  w-full px-4 py-3 
  border border-gray-300 rounded-lg 
  focus:ring-2 focus:ring-primary focus:border-transparent
  bg-white
">
  <option>Choisir une option</option>
</select>
```

## Responsive Design

### Breakpoints Tailwind
```css
/* sm: 640px et plus */
/* md: 768px et plus */
/* lg: 1024px et plus */
/* xl: 1280px et plus */
/* 2xl: 1536px et plus */
```

### Usage Responsive
```html
<!-- Layout responsive -->
<div class="
  grid grid-cols-1 gap-6
  md:grid-cols-2 
  lg:grid-cols-3 
  xl:grid-cols-4
">
  <!-- Cards -->
</div>

<!-- Texte responsive -->
<h1 class="
  text-2xl md:text-4xl lg:text-5xl 
  font-bold text-primary
">
  Titre Responsive
</h1>

<!-- Espacement responsive -->
<section class="
  px-4 py-8 
  md:px-8 md:py-12 
  lg:px-16 lg:py-16
">
  <!-- Contenu -->
</section>
```

## Mode Sombre

### Activation
```javascript
// Configuration darkMode: 'class'
// Basculer via classe sur <html>
document.documentElement.classList.toggle('dark');
```

### Classes Mode Sombre
```html
<!-- Fond et texte adaptatifs -->
<div class="
  bg-white dark:bg-gray-800 
  text-gray-900 dark:text-white
">
  Contenu adaptatif
</div>

<!-- Bordures -->
<div class="
  border-gray-200 dark:border-gray-700
">
  Bordure adaptative
</div>
```

## Build et Optimisation

### Package.json Scripts
```json
{
  "scripts": {
    "build-css": "tailwindcss -i ./static/css/input.css -o ./static/css/output.css",
    "watch-css": "tailwindcss -i ./static/css/input.css -o ./static/css/output.css --watch",
    "build-css-prod": "tailwindcss -i ./static/css/input.css -o ./static/css/output.css --minify"
  }
}
```

### Commandes de Build

#### Développement (avec watch)
```bash
# Surveillance continue des changements
npx tailwindcss -i ./static/css/input.css -o ./static/css/output.css --watch
```

#### Production (optimisé)
```bash
# Build minifié pour production
npx tailwindcss -i ./static/css/input.css -o ./static/css/output.css --minify
```

### Optimisations Actives
- **PurgeCSS intégré** : Suppression classes non utilisées
- **Minification** : Compression CSS production
- **Autoprefixer** : Préfixes navigateurs automatiques
- **Tree-shaking** : Seules les classes utilisées

## Performance

### Métriques Actuelles
- **Taille développement** : ~3.5MB (toutes les utilitaires)
- **Taille production** : ~127KB (après purge)
- **Classes utilisées** : ~1,200 sur 15,000+ disponibles
- **Temps de build** : <2 secondes

### Optimisations Techniques
```javascript
// Configuration purge aggressive
module.exports = {
  content: ['./templates/**/*.html'], // Scan précis
  safelist: ['transition', 'transform'], // Classes à préserver
  blocklist: ['container'], // Classes à exclure
}
```

## Intégration Django

### Template Base
```html
<!-- base.html -->
<!DOCTYPE html>
<html lang="fr" class="h-full">
<head>
    {% load static %}
    <link rel="stylesheet" href="{% static 'css/output.css' %}">
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
</head>
<body class="h-full bg-gray-50 font-sans">
    <!-- Contenu -->
</body>
</html>
```

### Classes Django Forms
```python
# forms.py avec widget_tweaks
from django import forms

class ContactForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent',
            'placeholder': 'votre@email.com'
        })
    )
```

## Maintenance et Évolution

### Mise à Jour Tailwind
```bash
# Vérifier version actuelle
npm list tailwindcss

# Mettre à jour
npm update tailwindcss

# Vérifier compatibilité
npx tailwindcss --help
```

### Ajout de Nouvelles Couleurs
```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: '#006ab3',
        secondary: '#96bf0d',
        accent: '#ff6b35',        // Nouvelle couleur
        neutral: '#64748b',       // Gris personnalisé
      }
    }
  }
}
```

### Plugins Recommandés
```javascript
// Plugins utiles à considérer
module.exports = {
  plugins: [
    require('@tailwindcss/forms'),      // Styles formulaires
    require('@tailwindcss/typography'), // Styles contenu
    require('@tailwindcss/aspect-ratio'), // Ratios d'aspect
  ],
}
```

## Debugging et Tools

### Extensions VS Code
- **Tailwind CSS IntelliSense** : Autocomplétion
- **Headwind** : Tri automatique des classes
- **Tailwind Docs** : Documentation intégrée

### Classes Debug
```html
<!-- Visualiser les breakpoints -->
<div class="
  bg-red-500 sm:bg-blue-500 md:bg-green-500 
  lg:bg-yellow-500 xl:bg-purple-500
">
  Debug Responsive
</div>

<!-- Grid debug -->
<div class="bg-grid-pattern opacity-20 fixed inset-0 pointer-events-none"></div>
```

### Commandes Utiles
```bash
# Analyser la taille du CSS
npx tailwindcss -i input.css -o output.css --verbose

# Générer toutes les classes (debug)
npx tailwindcss -i input.css -o output.css --content ""

# Vérifier la configuration
npx tailwindcss config
```

## Bonnes Pratiques

### Organisation des Classes
```html
<!-- Grouper par catégorie -->
<button class="
  <!-- Position et taille -->
  relative inline-flex items-center justify-center
  w-auto px-6 py-3
  
  <!-- Apparence -->
  bg-primary hover:bg-primary/90
  text-white font-medium
  border border-transparent rounded-lg
  
  <!-- Transitions -->
  transition-colors duration-200
  
  <!-- Focus et accessibilité -->
  focus:ring-2 focus:ring-primary focus:ring-offset-2
  focus:outline-none
">
  Bouton Organisé
</button>
```

### Composants Réutilisables
```css
/* Créer des composants avec @apply */
@layer components {
  .btn-primary {
    @apply bg-primary hover:bg-primary/90 text-white font-medium px-6 py-3 rounded-lg transition-colors duration-200 focus:ring-2 focus:ring-primary focus:ring-offset-2;
  }
  
  .card-standard {
    @apply bg-white rounded-xl shadow-lg p-6 border border-gray-200 hover:shadow-xl transition-shadow duration-200;
  }
}
```

## Support et Ressources

### Documentation Officielle
- [Tailwind CSS Docs](https://tailwindcss.com/docs)
- [Tailwind UI Components](https://tailwindui.com/)
- [Headless UI](https://headlessui.com/)

### Outils de Design
- [Tailwind Color Palette](https://tailwindcss.com/docs/customizing-colors)
- [Tailwind Play](https://play.tailwindcss.com/) - Playground en ligne
- [Figma Tailwind Kit](https://www.figma.com/community/file/768673952696297503)

### Cheat Sheets
- [Tailwind CSS Cheat Sheet](https://nerdcave.com/tailwind-cheat-sheet)
- [Classes par catégorie](https://tailwindcomponents.com/cheatsheet/)

---

*Documentation générée automatiquement - Dernière mise à jour : 07/01/2025*
