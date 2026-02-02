---
description: Agent spécialisé TailwindCSS avec vérification obligatoire de la compatibilité mobile
---

# Agent TailwindCSS & Mobile-First

Cet agent est spécialisé dans l'intégration TailwindCSS et doit **toujours** vérifier la compatibilité mobile de chaque modification.

## Règles obligatoires

### 1. Approche Mobile-First
- Toujours commencer par les styles mobiles (sans préfixe)
- Ajouter les breakpoints pour les écrans plus grands : `sm:`, `md:`, `lg:`, `xl:`, `2xl:`
- Exemple correct : `text-sm md:text-base lg:text-lg`

### 2. Breakpoints TailwindCSS
| Préfixe | Taille min | Appareil type |
|---------|------------|---------------|
| (aucun) | 0px | Mobile |
| `sm:` | 640px | Mobile paysage |
| `md:` | 768px | Tablette |
| `lg:` | 1024px | Desktop |
| `xl:` | 1280px | Grand écran |
| `2xl:` | 1536px | Très grand écran |

### 3. Vérifications obligatoires avant chaque modification

Avant de valider une modification CSS/TailwindCSS, vérifier :

- [ ] **Texte lisible** : `text-sm` minimum sur mobile, pas de texte trop petit
- [ ] **Espacement adapté** : `p-4` ou `px-4` sur mobile, augmenter sur desktop
- [ ] **Grilles responsives** : `grid-cols-1` sur mobile → `md:grid-cols-2` → `lg:grid-cols-3`
- [ ] **Flexbox responsive** : `flex-col` sur mobile → `md:flex-row` si nécessaire
- [ ] **Images adaptées** : `w-full` ou `max-w-full` avec `h-auto`
- [ ] **Boutons tactiles** : minimum 44x44px pour les zones cliquables (RGAA)
- [ ] **Navigation** : menu hamburger sur mobile si header complexe

### 4. Classes à privilégier

```html
<!-- Container responsive -->
<div class="container mx-auto px-4 md:px-6">

<!-- Grille responsive -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6">

<!-- Flexbox responsive -->
<div class="flex flex-col md:flex-row items-center gap-4">

<!-- Texte responsive -->
<h1 class="text-2xl md:text-3xl lg:text-4xl font-bold">

<!-- Espacement responsive -->
<section class="py-8 md:py-12 lg:py-16">

<!-- Affichage conditionnel -->
<div class="hidden md:block">  <!-- Visible desktop uniquement -->
<div class="block md:hidden">  <!-- Visible mobile uniquement -->
```

### 5. Processus de validation

// turbo
1. Après chaque modification de template HTML, lancer le serveur si pas déjà actif :
   ```
   python manage.py runserver
   ```

2. Tester la page dans le navigateur avec les DevTools :
   - Ouvrir les DevTools (F12)
   - Activer le mode responsive (Ctrl+Shift+M)
   - Tester les tailles : 375px (iPhone), 768px (iPad), 1024px (Desktop)

3. Points de contrôle visuels :
   - Pas de scroll horizontal sur mobile
   - Texte lisible sans zoom
   - Boutons assez grands pour le tactile
   - Images ne débordent pas
   - Menus accessibles

### 6. Erreurs courantes à éviter

❌ **Ne PAS faire** :
```html
<!-- Largeur fixe qui déborde sur mobile -->
<div class="w-[800px]">

<!-- Flex row sans fallback mobile -->
<div class="flex flex-row">

<!-- Texte trop grand sur mobile -->
<h1 class="text-5xl">

<!-- Padding excessif sur mobile -->
<div class="p-16">
```

✅ **Faire plutôt** :
```html
<!-- Largeur responsive -->
<div class="w-full max-w-4xl">

<!-- Flex avec fallback mobile -->
<div class="flex flex-col md:flex-row">

<!-- Texte adaptatif -->
<h1 class="text-2xl md:text-4xl lg:text-5xl">

<!-- Padding adaptatif -->
<div class="p-4 md:p-8 lg:p-16">
```

### 7. Utilitaires de debug

Pour débugger le responsive pendant le développement :
```html
<!-- Affiche le breakpoint actuel (à retirer en prod) -->
<div class="fixed bottom-0 right-0 bg-black text-white p-2 text-xs z-50">
  <span class="sm:hidden">XS</span>
  <span class="hidden sm:inline md:hidden">SM</span>
  <span class="hidden md:inline lg:hidden">MD</span>
  <span class="hidden lg:inline xl:hidden">LG</span>
  <span class="hidden xl:inline 2xl:hidden">XL</span>
  <span class="hidden 2xl:inline">2XL</span>
</div>
```
