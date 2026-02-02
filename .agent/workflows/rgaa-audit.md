---
description: Agent spécialisé dans l'audit d'accessibilité RGAA 4.1.2 pour les sites web français
---

# Agent Audit RGAA 4.1.2

Cet agent réalise des audits d'accessibilité selon le Référentiel Général d'Amélioration de l'Accessibilité (RGAA 4.1.2).

## ⚠️ DÉCLENCHEMENT AUTOMATIQUE

**Cet agent DOIT être appliqué automatiquement lors de :**
- Création d'une nouvelle page HTML/template Django
- Modification d'une page HTML/template Django existante
- Ajout de nouveaux composants (formulaires, liens, images, tableaux)

---

## Procédure de validation obligatoire

Après chaque création ou modification de page, l'agent DOIT :

### Étape 1 : Vérifications automatiques
Analyser le code HTML et vérifier les points suivants :

1. **Structure de base**
   - [ ] `{% block title %}` présent et descriptif
   - [ ] Un seul `<main>` ou hérité de base.html
   - [ ] Hiérarchie h1 > h2 > h3 sans saut de niveau
   - [ ] Chaque `<section>` a un `<h2>` (visible ou `sr-only`)

2. **Images et SVG**
   - [ ] Toutes les `<img>` ont un attribut `alt`
   - [ ] Images décoratives : `alt=""` 
   - [ ] SVG décoratifs : `aria-hidden="true"`
   - [ ] SVG informatifs : `role="img"` + `<title>`

3. **Liens**
   - [ ] Pas de "cliquez ici" ou "en savoir plus" seul
   - [ ] `target="_blank"` → ajouter `(nouvelle fenêtre)` ou `aria-label`
   - [ ] Fichiers téléchargeables → format et poids (ex: PDF, 2 Mo)
   - [ ] Attribut `download` sur liens de téléchargement direct

4. **Formulaires** (si présents)
   - [ ] `<label for="id">` sur chaque champ
   - [ ] Champs obligatoires : `required` + indication `*`
   - [ ] `autocomplete` sur champs standards

5. **Tags Django**
   - [ ] `{% load static %}` si utilisation de `{% static %}`
   - [ ] `{% block meta_description %}` présent

### Étape 2 : Rapport de conformité
Après analyse, fournir un rapport sous cette forme :

```
## Rapport RGAA - [nom_page.html]

### ✅ Points conformes
- [liste des points OK]

### ⚠️ Points à corriger
| Critère | Problème | Correction requise |
|---------|----------|-------------------|
| X.X | Description | Action à faire |

### Statut : CONFORME / NON CONFORME
```

### Étape 3 : Corrections automatiques
Si des non-conformités sont détectées :
1. Proposer les corrections
2. Appliquer les corrections après validation
3. Vérifier à nouveau la conformité

---

## Utilisation manuelle

```
/rgaa-audit [page.html]    # Auditer une page spécifique
/rgaa-audit --all          # Auditer toutes les pages
/rgaa-audit --check        # Vérifier les problèmes systémiques
```

---

## Les 13 thématiques RGAA 4.1.2 (106 critères)

### Thématique 1 : Images (9 critères)

| Critère | Niveau | Description | Test rapide |
|---------|--------|-------------|-------------|
| 1.1 | A | Image porteuse d'information avec alternative textuelle | `img[alt]` non vide |
| 1.2 | A | Image de décoration correctement ignorée | `img[alt=""]` ou `aria-hidden="true"` |
| 1.3 | A | Alternative pertinente pour les images informatives | Alt décrit le contenu |
| 1.4 | A | Image légendée correctement restituée | `<figure>` + `<figcaption>` |
| 1.5 | A | CAPTCHA avec alternative | Alternative audio ou autre |
| 1.6 | A | Image porteuse d'info avec description détaillée | `aria-describedby` si nécessaire |
| 1.7 | A | Description détaillée pertinente | Contenu de la description |
| 1.8 | AA | Image texte remplacée par du texte stylé | Pas d'image pour du texte |
| 1.9 | A | Légende d'image correctement reliée | `aria-labelledby` |

**Vérifications courantes** :
```html
<!-- Correct : image informative -->
<img src="logo.png" alt="Logo de la CCSA">

<!-- Correct : image décorative -->
<img src="decoration.png" alt="" aria-hidden="true">

<!-- Correct : SVG décoratif -->
<svg aria-hidden="true">...</svg>

<!-- Correct : SVG informatif -->
<svg role="img" aria-labelledby="title">
  <title id="title">Description</title>
</svg>
```

---

### Thématique 2 : Cadres (2 critères)

| Critère | Niveau | Description | Test rapide |
|---------|--------|-------------|-------------|
| 2.1 | A | Chaque iframe a un titre | `<iframe title="...">` |
| 2.2 | A | Titre de cadre pertinent | Title décrit le contenu |

**Vérification** :
```html
<!-- Correct -->
<iframe src="video.html" title="Vidéo de présentation de la CCSA"></iframe>
```

---

### Thématique 3 : Couleurs (3 critères)

| Critère | Niveau | Description | Test rapide |
|---------|--------|-------------|-------------|
| 3.1 | A | Information non donnée uniquement par la couleur | Texte + couleur |
| 3.2 | AA | Contraste texte/fond ≥ 4.5:1 (normal) ou 3:1 (grand) | Outil contraste |
| 3.3 | AA | Contraste composants d'interface ≥ 3:1 | Boutons, liens, icônes |

**Ratios de contraste minimum** :
- Texte normal (< 24px ou < 18.5px bold) : **4.5:1**
- Grand texte (≥ 24px ou ≥ 18.5px bold) : **3:1**
- Composants d'interface : **3:1**

---

### Thématique 4 : Multimédia (13 critères)

| Critère | Niveau | Description |
|---------|--------|-------------|
| 4.1-4.4 | A | Sous-titres pour vidéos |
| 4.5-4.8 | AA | Audiodescription |
| 4.9-4.11 | A | Alternative aux médias non temporels |
| 4.12 | A | Contrôle du son automatique |
| 4.13 | A | Alternative aux médias temporels |

---

### Thématique 5 : Tableaux (8 critères)

| Critère | Niveau | Description | Test rapide |
|---------|--------|-------------|-------------|
| 5.1 | A | Tableau de données avec en-têtes | `<th>` présents |
| 5.2 | A | Titre de tableau pertinent | `<caption>` |
| 5.3 | A | En-têtes associés aux cellules | `scope="col/row"` |
| 5.4 | A | Tableaux de données identifiés | Pas `role="presentation"` |
| 5.5 | A | Tableaux de mise en forme identifiés | `role="presentation"` |
| 5.6 | A | En-têtes et données liés | `headers` et `id` |
| 5.7 | A | Résumé de tableau complexe | `aria-describedby` |
| 5.8 | A | Tableau de mise en forme linéarisable | Ordre logique |

**Structure correcte** :
```html
<table>
  <caption>Horaires de la déchetterie</caption>
  <thead>
    <tr>
      <th scope="col">Jour</th>
      <th scope="col">Matin</th>
      <th scope="col">Après-midi</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th scope="row">Lundi</th>
      <td>Fermé</td>
      <td>14h-18h</td>
    </tr>
  </tbody>
</table>
```

---

### Thématique 6 : Liens (2 critères)

| Critère | Niveau | Description | Test rapide |
|---------|--------|-------------|-------------|
| 6.1 | A | Lien explicite (intitulé + contexte) | Pas de "cliquez ici" |
| 6.2 | A | Lien identique = même destination | Cohérence des liens |

**Exemples** :
```html
<!-- Mauvais -->
<a href="/rapport.pdf">Cliquez ici</a>

<!-- Bon -->
<a href="/rapport.pdf">Télécharger le rapport d'activité 2024 (PDF, 2.5 Mo)</a>

<!-- Acceptable avec aria-label -->
<a href="/rapport.pdf" aria-label="Télécharger le rapport d'activité 2024 (PDF)">
  En savoir plus
</a>
```

---

### Thématique 7 : Scripts (5 critères)

| Critère | Niveau | Description | Test rapide |
|---------|--------|-------------|-------------|
| 7.1 | A | Script compatible avec les TA | ARIA correctement utilisé |
| 7.2 | A | Script contrôlable au clavier | Tab, Enter, Escape |
| 7.3 | A | Alerte contrôlable | Pas d'alerte bloquante |
| 7.4 | A | Changement de contexte explicite | Pas de changement auto |
| 7.5 | AA | Message de statut accessible | `aria-live`, `role="alert"` |

**Attributs ARIA essentiels** :
```html
<!-- Menu déroulant -->
<button aria-expanded="false" aria-haspopup="true" aria-controls="menu">
  Menu
</button>
<ul id="menu" aria-hidden="true">...</ul>

<!-- Message de statut -->
<div role="alert" aria-live="polite">
  Formulaire envoyé avec succès
</div>

<!-- Modale -->
<div role="dialog" aria-modal="true" aria-labelledby="title">
  <h2 id="title">Titre de la modale</h2>
</div>
```

---

### Thématique 8 : Éléments obligatoires (10 critères)

| Critère | Niveau | Description | Test rapide |
|---------|--------|-------------|-------------|
| 8.1 | A | DOCTYPE valide | `<!DOCTYPE html>` |
| 8.2 | A | Langue par défaut | `<html lang="fr">` |
| 8.3 | A | Changements de langue signalés | `lang="en"` sur le texte |
| 8.4 | A | Direction de lecture | `dir="ltr"` si nécessaire |
| 8.5 | A | Titre de page présent | `<title>` non vide |
| 8.6 | A | Titre de page pertinent | Décrit le contenu |
| 8.7 | A | Focus visible | Outline visible |
| 8.8 | A | Pas de changement de contexte au focus | Pas d'action auto |
| 8.9 | A | Balises utilisées sémantiquement | Pas de `<div>` pour `<button>` |
| 8.10 | A | Changement de contexte sur demande | Action utilisateur requise |

---

### Thématique 9 : Structuration (4 critères)

| Critère | Niveau | Description | Test rapide |
|---------|--------|-------------|-------------|
| 9.1 | A | Hiérarchie des titres logique | h1 > h2 > h3 sans saut |
| 9.2 | A | Structure du document cohérente | `<header>`, `<main>`, `<footer>` |
| 9.3 | A | Listes correctement structurées | `<ul>/<ol>` + `<li>` |
| 9.4 | A | Citations correctement balisées | `<blockquote>`, `<q>` |

**Structure HTML5 correcte** :
```html
<body>
  <header>
    <nav aria-label="Menu principal">...</nav>
  </header>

  <main id="main-content">
    <h1>Titre principal (unique)</h1>
    <section>
      <h2>Section 1</h2>
      <h3>Sous-section</h3>
    </section>
  </main>

  <footer>...</footer>
</body>
```

**Règle importante** : Un seul `<main>` par page !

---

### Thématique 10 : Présentation (14 critères)

| Critère | Niveau | Description |
|---------|--------|-------------|
| 10.1 | A | CSS utilisé pour la présentation |
| 10.2 | A | Contenu compréhensible sans CSS |
| 10.3 | A | Information non véhiculée par la forme seule |
| 10.4 | AA | Texte redimensionnable à 200% |
| 10.5 | A | Texte caché restitué par les TA |
| 10.6 | A | Liens visibles au focus |
| 10.7 | AA | Focus visible |
| 10.8 | A | Contenus masqués accessibles |
| 10.9-10.10 | A | Information non donnée par forme/position |
| 10.11 | AA | Pas de scroll horizontal à 320px |
| 10.12 | AA | Propriétés de texte personnalisables |
| 10.13-10.14 | AA | Contenus additionnels contrôlables |

---

### Thématique 11 : Formulaires (13 critères)

| Critère | Niveau | Description | Test rapide |
|---------|--------|-------------|-------------|
| 11.1 | A | Champ avec étiquette | `<label for="id">` |
| 11.2 | A | Étiquette associée | `for` = `id` |
| 11.3 | A | Étiquette pertinente | Label descriptif |
| 11.4 | A | Regroupement avec légende | `<fieldset>` + `<legend>` |
| 11.5 | A | Items de même nature regroupés | Groupes logiques |
| 11.6 | A | Champs obligatoires identifiés | `required` + indication visuelle |
| 11.7 | A | Format attendu indiqué | Placeholder ou aide |
| 11.8 | A | Aide à la saisie | Instructions claires |
| 11.9 | A | Erreurs identifiées accessiblement | `aria-invalid` + `aria-describedby` |
| 11.10 | A | Erreurs décrites | Message d'erreur clair |
| 11.11 | AA | Suggestions de correction | Aide à corriger |
| 11.12 | AA | Autocomplete présent | `autocomplete="..."` |
| 11.13 | AA | Finalité identifiable | Autocomplete standard |

**Formulaire accessible complet** :
```html
<form>
  <p class="text-sm text-gray-600">
    Les champs marqués d'un <span aria-hidden="true">*</span>
    <span class="sr-only">astérisque</span> sont obligatoires.
  </p>

  <fieldset>
    <legend>Informations personnelles</legend>

    <div>
      <label for="email">
        Email <span aria-hidden="true">*</span>
        <span class="sr-only">(obligatoire)</span>
      </label>
      <input
        type="email"
        id="email"
        name="email"
        required
        autocomplete="email"
        aria-describedby="email-help email-error"
        aria-invalid="false"
      >
      <p id="email-help" class="text-sm">Format : exemple@domaine.fr</p>
      <p id="email-error" class="text-red-600 hidden">Veuillez saisir un email valide</p>
    </div>
  </fieldset>

  <button type="submit">Envoyer</button>
</form>
```

---

### Thématique 12 : Navigation (11 critères)

| Critère | Niveau | Description | Test rapide |
|---------|--------|-------------|-------------|
| 12.1 | AA | Au moins 2 systèmes de navigation | Menu + plan du site |
| 12.2 | AA | Navigation cohérente | Même structure partout |
| 12.3 | AA | Moteur de recherche accessible | Si présent |
| 12.4 | AA | Plan du site accessible | Lien vers plan |
| 12.5 | AA | Fil d'Ariane | Sur pages internes |
| 12.6 | A | Zones de regroupement identifiables | Landmarks HTML5 |
| 12.7 | A | Lien d'évitement | "Aller au contenu" |
| 12.8 | A | Ordre de tabulation logique | Tab suit le DOM |
| 12.9 | A | Pas de piège au clavier | Escape fonctionne |
| 12.10 | A | Raccourcis à 1 touche contrôlables | Si présents |
| 12.11 | AA | Contenus additionnels accessibles | Focus trap correct |

**Lien d'évitement** :
```html
<body>
  <a href="#main-content" class="sr-only focus:not-sr-only focus:absolute ...">
    Aller au contenu principal
  </a>
  <!-- ... -->
  <main id="main-content">
```

---

### Thématique 13 : Consultation (12 critères)

| Critère | Niveau | Description | Test rapide |
|---------|--------|-------------|-------------|
| 13.1 | A | Pas de rafraîchissement auto | Pas de `<meta refresh>` |
| 13.2 | A | Limite de temps contrôlable | Si présente |
| 13.3 | A | Contenus en mouvement contrôlables | Bouton pause |
| 13.4 | A | Pas de clignotement > 3/s | Pas de flash |
| 13.5 | AAA | Contenus en mouvement stoppables | Préférence utilisateur |
| 13.6 | A | Son automatique contrôlable | Bouton mute |
| 13.7 | A | Pas de changement de luminosité brusque | Transitions douces |
| 13.8 | A | Documents téléchargeables accessibles | PDF accessible |
| 13.9 | A | Ouverture nouvelle fenêtre signalée | "(nouvelle fenêtre)" |
| 13.10 | AA | Orientation non bloquée | Pas de `orientation: portrait` |
| 13.11 | A | Gestes complexes avec alternative | Alternative simple |
| 13.12 | A | Actions par mouvement avec alternative | Alternative clavier |

**Liens externes** :
```html
<!-- Correct -->
<a href="https://externe.com" target="_blank" rel="noopener">
  Site externe
  <span class="sr-only">(nouvelle fenêtre)</span>
  <svg aria-hidden="true"><!-- icône externe --></svg>
</a>
```

**Documents téléchargeables** :
```html
<a href="/rapport.pdf">
  Rapport d'activité 2024 (PDF, 2.5 Mo)
</a>
```

---

## Checklist rapide pour audit

### Structure de base
- [ ] `<!DOCTYPE html>` présent
- [ ] `<html lang="fr">` défini
- [ ] `<title>` unique et descriptif
- [ ] Un seul `<main>` par page
- [ ] `<header>`, `<nav>`, `<main>`, `<footer>` présents
- [ ] Hiérarchie h1 > h2 > h3 sans saut
- [ ] Lien d'évitement "Aller au contenu"

### Images
- [ ] `alt` sur toutes les `<img>`
- [ ] `alt=""` ou `aria-hidden="true"` pour images décoratives
- [ ] SVG avec `aria-hidden="true"` ou `role="img"` + titre

### Liens
- [ ] Intitulés explicites (pas de "cliquez ici")
- [ ] `target="_blank"` avec indication "(nouvelle fenêtre)"
- [ ] Documents avec format et poids (PDF, 2 Mo)

### Formulaires
- [ ] `<label for="">` sur tous les champs
- [ ] Champs obligatoires identifiés (`required` + `*`)
- [ ] Erreurs avec `aria-invalid` et `aria-describedby`
- [ ] `autocomplete` sur les champs standards

### Navigation
- [ ] Ordre de tabulation logique
- [ ] Focus visible sur tous les éléments interactifs
- [ ] Pas de piège au clavier (Escape fonctionne)

### Couleurs
- [ ] Contraste texte ≥ 4.5:1
- [ ] Information non donnée par la couleur seule

---

## Outils recommandés

1. **Extension navigateur** : WAVE, axe DevTools, Lighthouse
2. **Contraste** : WebAIM Contrast Checker
3. **Lecteur d'écran** : NVDA (Windows), VoiceOver (Mac)
4. **Validation HTML** : W3C Validator

---

## Références

- [RGAA 4.1.2 officiel](https://accessibilite.numerique.gouv.fr/methode/criteres-et-tests/)
- [WCAG 2.1](https://www.w3.org/WAI/WCAG21/quickref/)
- [MDN Accessibility](https://developer.mozilla.org/fr/docs/Web/Accessibility)
