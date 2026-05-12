# Audit Accessibilité — Page Collecte des Déchets

**Date :** 11/05/2026  
**URL :** http://127.0.0.1:8000/collecte-dechets/  
**Template :** `home/templates/home/collecte-dechets.html`  

---

## 1. Résumé

| Métrique | Valeur |
|---|---|
| Conformité estimée | ~50% |
| Critères applicables | 44 |
| Conformes | 22 |
| Non conformes | 22 |
| **Bloquants 🔴** | **5** |
| **Majeurs 🟠** | **6** |
| **Mineurs 🟡** | **11** |

---

## 2. Non-conformités

### Thème 1 : Images

**[C] 1.1.1 — Image poubelle verre**
- **Élément :** `alt="Poubelle de collecte du verre"`  
- **Statut :** ✅ Conforme.

### Thème 3 : Couleurs

**[NC] 3.2.1 — Contraste bannière #005a9e/blanc**
- **Gravité :** 🟠 Majeure — identique à toutes les pages.

**[C] 3.3.1 — Contraste listes consignes (text-green-500 sur fond blanc)**
- **Statut :** ✅ Conforme AA.

### Thème 6 : Liens

**[NC] 6.1.1 — Contact sans lien cliquable**
- **Niveau :** A  
- **Gravité :** 🟠 Majeure  
- **Élément :** `<div class="inline-flex items-center px-6 py-4 bg-primary text-white rounded-lg ...">`  
- **Problème :** Le numéro de téléphone est dans un `<div>`, pas dans un `<a href="tel:...">`. Impossible de cliquer ou de naviguer au clavier.  
- **Correction :** Remplacer le `<div>` par un `<a href="tel:0327606524">`.

### Thème 7 : Scripts

**[NC] 7.1.1 — Widget recherche avec `onchange`/`oninput`**
- **Niveau :** A  
- **Gravité :** 🟡 Mineure  
- **Élément :** Les gestionnaires inline `onchange`, `oninput`, `onclick`  
- **Problème :** Les événements inline ne posent pas de problème d'accessibilité en soi. Mais si JS est désactivé, le widget ne fonctionne pas. C'est acceptable.  
- **Statut :** ⚠️ OK si JS chargé.

**[C] 7.5.1 — `aria-live` manquant sur les résultats de recherche**
- **Gravité :** 🟠 Majeure  
- **Élément :** `<div id="result"></div>` et `<div id="suggestions"></div>`  
- **Problème :** Les résultats dynamiques de la recherche de rue ne sont pas annoncés par `aria-live`. Les utilisateurs de lecteurs d'écran ne sauront pas que les résultats ont changé.  
- **Correction :** Ajouter `aria-live="polite"` sur les deux conteneurs :

```html
<div id="suggestions" aria-live="polite"></div>
<div id="result" aria-live="polite"></div>
```

### Thème 8 : Éléments obligatoires

**[NC] 8.2.1 — Double `<main>`**
- **Niveau :** A  
- **Gravité :** 🔴 Critique  
- **Élément :** `<main id="main-content">` dans le template + `<main>` dans `base.html`  
- **Correction :** Supprimer `<main id="main-content">` du template.

**[NC] 8.2.2 — 4 SVGs avec `aria-hidden` dans l'attribut `class`**
- **Niveau :** A  
- **Gravité :** 🔴 Critique  
- **Élément :** `class="h-5 aria-hidden="true" focusable="false" w-5 ..."`  
- **Problème :** `aria-hidden="true"` est à l'intérieur de `class` au lieu d'être un attribut séparé. Ces SVGs ne sont PAS masqués des AT.  
- **Occurrences :** Lignes 119, 125, 131, 137  
- **Correction :**

```html
<svg class="h-5 w-5 text-green-500 mt-0.5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true" focusable="false">
```

**[NC] 8.2.3 — Motifs décoratifs bannière sans `aria-hidden`**
- **Gravité :** 🟡 Mineure  
- **Élément :** Deux `<div>` avec clip-path (lignes 18-19)  
- **Problème :** Ces éléments décoratifs n'ont pas `aria-hidden="true"`, contrairement aux autres pages.

### Thème 9 : Structuration

**[C] 9.1.1 — Hiérarchie de titres**
- **Élément :** H1 → H2 → H3 → H2 → H3 → H2 → H3, H3, H3 → H2  
- **Problème :** La hiérarchie est correctement ordonnée mais alterne entre h2 et h3 de manière sémantique. C'est acceptable.

**[C] 9.2.1 — Landmarks**
- **Statut :** ⚠️ Un seul main si on supprime la duplication.

### Thème 11 : Formulaires

**[NC] 11.1.1 — Label select non associé visuellement**
- **Niveau :** A  
- **Gravité :** 🟡 Mineure  
- **Élément :** `<label for="citySelect">Sélectionner votre commune</label>`  
- **Problème :** Le label est correct avec `for`. Mais le `<select>` utilise `onchange="handleCityChange()"` qui n'est pas fiable au clavier sans gestionnaire keydown.  
- **Correction :** Ajouter un gestionnaire `keydown` ou utiliser un écouteur JS en non-inline.

**[C] 11.4.1 — Champ search avec placeholder**
- **Élément :** `<input type="text" id="search" placeholder="Saisir le nom d'une rue...">`  
- **Problème :** Le champ a un label avant, donc conforme. Mais le placeholder a `text-gray-600` sur fond blanc → ratio ~4.6:1, juste conforme AA.  
- **Correction :** Assombrir à `placeholder-gray-700`.

---

## 3. Plan d'action

| # | Gravité | Correctif | Effort |
|---|---|---|---|
| 🔴 1 | Critique | Supprimer `<main>` en double | 2 min |
| 🔴 2 | Critique | 4× SVGs avec `aria-hidden` dans `class` → attributs séparés | 5 min |
| 🔴 3 | Critique | `aria-live="polite"` sur `#result` et `#suggestions` | 2 min |
| 🟠 4 | Majeure | Remplacer `<div>` contact par `<a href="tel:...">` | 2 min |
| 🟠 5 | Majeure | Contraste bannière | Intégré |
| 🟡 6 | Mineure | `aria-hidden` sur motifs décoratifs bannière | 1 min |
| 🟡 7 | Mineure | Placeholder contrast (`text-gray-600` → `text-gray-700`) | 2 min |

*Rapport spécifique à la page `/collecte-dechets/`.*
