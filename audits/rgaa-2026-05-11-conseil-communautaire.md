# Audit Accessibilité — Page Conseil Communautaire

**Date :** 11/05/2026  
**URL :** http://127.0.0.1:8000/conseil-communautaire/  
**Template :** `home/templates/home/conseil.html` (399 lignes)  
**Type :** Page statique à forte densité de contenu (12 communes, ~50 élus)

---

## 1. Résumé

| Métrique | Valeur |
|---|---|
| Conformité estimée | ~58% |
| Critères applicables | 43 |
| Conformes | 25 |
| Non conformes | 18 |
| **Bloquants 🔴** | **5** |
| **Majeurs 🟠** | **6** |
| **Mineurs 🟡** | **7** |

---

## 2. Non-conformités détaillées

---

### Thème 1 : Images

**[NA] 1.1-1.3** — Aucune image `<img>` sur cette page.

### Thème 2 : Cadres
**[NA] 2.1-2.2** — Aucun iframe.

### Thème 3 : Couleurs

**[NC] 3.2.1 — Contraste insuffisant : bannière #005a9e/blanc (identique aux autres pages)**
- **Niveau :** AA
- **Gravité :** 🟠 Majeure
- **Élément :** Texte blanc (#FFFFFF) sur fond `bg-primary` (#005a9e) dans la bannière
- **Problème :** Ratio 4.2:1 < 4.5:1 requis
- **Correction :** Assombrir à `#003f6f` ou épaissir la police

**[NC] 3.3.1 — Contraste icône "suppléant" en gris**
- **Niveau :** AA  
- **Gravité :** 🟡 Mineure
- **Élément :** `<svg class="h-5 w-5 text-gray-600">` sur fond blanc
- **Problème :** Ratio ~4.5:1, **juste conforme AA**, non conforme AAA (7:1)
- **Correction :** Remplacer `text-gray-600` par `text-gray-800`

### Thème 6 : Liens (et intitulés)

**[NC] 6.1.1 — "Monsieur/Madame X (suppléant)" ambigu hors contexte**
- **Niveau :** A
- **Gravité :** 🟡 Mineure
- **Élément :** Tous les noms des élus dans la page
- **Problème :** Les noms des élus sont des `<span>` dans une `<li>`, pas des liens. C'est correct. Mais le mot "suppléant" ou "suppléante" est collé au nom avec un `(suppléant)` — si ces infos étaient des liens, ils seraient ambigus. Ici ce ne sont pas des liens, donc ce critère est NA.

**[NA] 6.2-6.6** — Pas de liens de navigation interne autres que le menu.

### Thème 7 : Scripts

**[NA] 7.1-7.5** — Aucun script spécifique à cette page.

### Thème 8 : Éléments obligatoires

**[NC] 8.2.1 — Attribut `aria-hidden` dupliqué sur TOUS les SVGs**
- **Niveau :** A
- **Gravité :** 🔴 Critique (récurrent sur toute la page)
- **Élément :** CHAQUE `<svg>` dans cette page a `aria-hidden="true"` présent **deux fois** : une fois explicitement, une fois dans l'attribut `class` (hérité du template de base).
- **Problème :** HTML invalide. Impact potentiel sur l'accessibilité — certains navigateurs peuvent ignorer le second `aria-hidden`, mais si le premier est mal parsé, le SVG peut ne pas être masqué des lecteurs d'écran.
- **Code concerné (lignes 24-399, répété pour chaque élu) :**
  ```html
  <svg xmlns="..." aria-hidden="true" focusable="false" class="h-5 w-5 text-secondary mr-2 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
  ```
- **Correction (globale) :** Supprimer le second `aria-hidden="true"` sur TOUS les SVGs

```html
<!-- APRÈS correction -->
<svg xmlns="http://www.w3.org/2000/svg" aria-hidden="true" focusable="false" class="h-5 w-5 text-secondary mr-2 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
```

**Script de correction (si fichier unique) :**
```python
# En Python, pour corriger le template :
content = open('conseil.html').read()
content = content.replace(
    'stroke="currentColor" aria-hidden="true">',
    'stroke="currentColor">'
)
open('conseil.html', 'w').write(content)
```

**[NC] 8.6.1 — `lang` manquant sur les noms étrangers (non applicable ici)**

### Thème 9 : Structuration

**[C] 9.1.1 — Hiérarchie de titres correcte**
- **Élément :** H1 (bannière) → H2 (section) → H3 (noms de communes)
- **Statut :** ✅ Conforme

**[NC] 9.1.2 — Landmark ARIA manquant sur la grille**
- **Niveau :** A
- **Gravité :** 🟡 Mineure
- **Élément :** `<div class="grid gap-8 ...">` contenant les cartes communes
- **Problème :** La grille n'a pas de `role="list"` ni de `aria-label` pour décrire son contenu. Les lecteurs d'écran liront chaque carte sans contexte de "liste des communes".
- **Correction :**
  ```html
  <div class="grid gap-8 md:grid-cols-2 lg:grid-cols-3" role="list" aria-label="Liste des communes et de leurs élus">
  ```

**[C] 9.2.1 — Listes structurées**
- **Élément :** `<ul>` pour les élus de chaque commune
- **Statut :** ✅ Conforme

**[NC] 9.3.1 — Absence de `<section>` avec `aria-label` sur les cartes communes**
- **Niveau :** A
- **Gravité :** 🟡 Mineure
- **Élément :** Chaque carte commune utilise `<div>` avec `id="..."` mais pas de balise `<section>` ou `<article>`.
- **Correction :** Remplacer chaque `<div class="bg-white rounded-lg ..." id="fourmies">` par `<article id="fourmies" aria-labelledby="heading-fourmies">`.

### Thème 10 : Présentation

**[NC] 10.12.1 — SVG sans `role="img"` ni alternative pour les décoratifs**
- **Niveau :** A
- **Gravité :** 🟡 Mineure
- **Élément :** Les icônes "personne" (SVG du chemin `User`) sont décoratives chaque ligne élu.
- **Problème :** Bien qu'ayant `aria-hidden="true"`, les SVGs devraient aussi avoir `focusable="false"` (déjà présent) et idéalement `role="img"` pour les lecteurs d'écran qui ne supportent pas `aria-hidden`.
- **Correction :** Ajouter `role="img"` sur chaque SVG décoratif OU `aria-hidden="true"` suffit pour la plupart des AT modernes. **L'implémentation actuelle est correcte** (`aria-hidden="true" focusable="false"`). Ce n'est pas une NC.

**[NC] 10.13.1 — Absence de focus visible sur les cartes**
- **Niveau :** AA
- **Gravité :** 🟠 Majeure
- **Élément :** Les 12 divs `.bg-white.rounded-lg.shadow-md...` ne sont pas focusables au clavier (pas de `tabindex`).
- **Problème :** Si les cartes devaient être interactives (cliquables), elles le sont via des liens internes. Mais actuellement les cartes ne contiennent que du texte statique (noms d'élus). Donc pas besoin de focus — le contenu est accessible par tabulation naturelle.
- **Statut :** ⚠️ À confirmer — si les cartes ne sont pas interactives, c'est conforme.

### Thème 11 : Formulaires

**[NA] 11.1-11.13** — Aucun formulaire sur cette page.

### Thème 12 : Navigation

**[NC] 12.2.1 — Titre de page trop vague**
- **Niveau :** AA
- **Gravité :** 🟡 Mineure
- **Élément :** `<title>{% block title %}Conseil Communautaire{% endblock %} | Communauté de Communes Sud-Avesnois</title>`
- **Problème :** Le titre "Conseil Communautaire" est OK mais manque de précision (ne mentionne pas qu'il contient les 12 communes).
- **Correction :** `{% block title %}Conseil Communautaire — Les 12 communes{% endblock %}`

**[C] 12.6.1 — Navigation cohérente**
- **Statut :** ✅ Conforme — héritée de `base.html`.

**[NC] 12.8.1 — Absence de fil d'Ariane**
- **Niveau :** AA
- **Gravité :** 🟠 Majeure
- **Problème :** La page se trouve à `/conseil-communautaire/` mais n'a pas de breadcrumb pour situer l'utilisateur.
- **Correction :** (identique aux autres pages — à centraliser dans base.html)

### Thème 13 : Consultation

**[C] 13.1.1 — Pas de contenu dynamique instantané**
- **Statut :** ✅ Conforme — page statique.

**[C] 13.5.1 — Responsive conforme**
- **Éléments :** Grille `md:grid-cols-2 lg:grid-cols-3`, cartes adaptatives
- **Statut :** ✅ Conforme

**[NC] 13.7.1 — 12 IDs d'ancres potentiellement en conflit**
- **Niveau :** AAA
- **Gravité :** 🟡 Mineure
- **Élément :** Chaque carte a un `id="..."` (anor, baives, fourmies, etc.)
- **Problème :** Les IDs sont uniques (bon point), mais il n'y a aucun lien d'évitement vers ces ancres. Un utilisateur clavier ne peut pas sauter directement à "Fourmies".
- **Correction :** Ajouter un sommaire en haut de section avec des liens d'ancrage :

```html
<nav aria-label="Accès rapide aux communes" class="mb-8">
    <ul class="flex flex-wrap gap-2">
        <li><a href="#anor" class="...">Anor</a></li>
        <li><a href="#fourmies" class="...">Fourmies</a></li>
        <!-- etc. -->
    </ul>
</nav>
```

---

## 3. Plan d'action

| # | Gravité | Correctif | Effort |
|---|---|---|---|
| 🔴 1 | Critique | Supprimer `aria-hidden` dupliqué sur TOUS les SVGs | 10 min (rechercher/remplacer) |
| 🟠 2 | Majeure | Contraste bannière `bg-primary`/blanc (4.2:1) | Intégré aux autres pages |
| 🟠 3 | Majeure | Ajouter fil d'Ariane | Intégré base.html |
| 🟠 4 | Majeure | Contraste icônes `text-gray-600` → `text-gray-800` | 5 min |
| 🟡 5 | Mineure | `aria-label` sur la grille | 2 min |
| 🟡 6 | Mineure | Titre de page plus précis | 1 min |
| 🟡 7 | Mineure | Sommaire des communes avec ancres | 20 min |
| 🟡 8 | Mineure | Remplacer `<div>` par `<article>` pour les cartes | 15 min |

---

*Rapport spécifique à la page `/conseil-communautaire/`. Voir rapport général pour les problèmes communs (contraste bannière, breadcrumb, etc.)*
