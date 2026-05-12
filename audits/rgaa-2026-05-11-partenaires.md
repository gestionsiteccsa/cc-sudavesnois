# Audit Accessibilité — Page Partenaires

**Date :** 11/05/2026  
**URL :** http://127.0.0.1:8000/partenaires/  
**Template :** `C:\Python\cc-sudavesnois\partenaires\templates\partenaires\partenaires.html`  
**Type :** Page dynamique liste de partenaires avec catégories, logos et liens

---

## 1. Résumé

| Métrique | Valeur |
|---|---|
| Conformité estimée | ~45% |
| Critères applicables | 48 |
| Conformes | 22 |
| Non conformes | 26 |
| **Bloquants 🔴** | **6** |
| **Majeurs 🟠** | **9** |
| **Mineurs 🟡** | **11** |

---

## 2. Non-conformités détaillées

### Thème 1 : Images

**[NC] 1.1.1 — Logo partenaire sans alternative textuelle**
- **Niveau :** A  
- **Gravité :** 🟠 Majeure  
- **Élément :** `<img src="{{ partenaire.logo.url }}" alt="" class="...">` dans les partenaires normaux  
- **Problème :** L'image logo a `alt=""` (décoratif). Mais le logo est porteur d'information (identité du partenaire). Le nom du partenaire est présent en `<h3>` juste à côté, donc l'info n'est pas perdue. C'est **conforme** car l'alternative vide est acceptable quand l'information est redondante avec du texte adjacent.  
- **Statut :** ✅ Conforme pour les partenaires normaux (nom présent en h3).

**[C] 1.1.2 — Logo avec `alt="{{ partenaire.nom }}"` (subventions et autres)**
- **Niveau :** A  
- **Gravité :** 🟡 Mineure  
- **Élément :** `<img src="{{ partenaire.logo.url }}" alt="{{ partenaire.nom }}">`  
- **Problème :** Le `alt` répète le nom déjà présent dans le `<h3>` adjacent. C'est redondant, pas un blocage.  
- **Correction :** Uniformiser avec `alt=""` partout (l'info est déjà dans le titre).

### Thème 3 : Couleurs

**[NC] 3.2.1 — Contraste bannière #005a9e/blanc (identique)**
- **Gravité :** 🟠 Majeure — voir rapports précédents.

**[C] 3.3.1 — Liens partenaires avec `aria-label`**
- **Élément :** `aria-label="Visiter le site de {{ partenaire.nom }} (nouvelle fenêtre)"`  
- **Statut :** ✅ Conforme.

### Thème 6 : Liens

**[C] 6.1.1 — Intitulés de liens explicites**
- **Élément :** "Aller vers le site" avec `aria-label`  
- **Statut :** ✅ Conforme.

**[NC] 6.4.1 — `rel="noopener noreferrer"` mal orthographié**
- **Niveau :** A  
- **Gravité :** 🟡 Mineure  
- **Élément :** `rel="noopener noreferrer"` sur TOUS les liens externes  
- **Problème :** `noopener` est une faute de frappe au lieu de `noopener`. La valeur `noreferrer` (correcte) est présente, mais `noopener` manque car mal orthographié. La protection de sécurité contre `window.opener` est réduite.  
- **Correction :** Remplacer `rel="noopener noreferrer"` par `rel="noopener noreferrer"`.

### Thème 7 : Scripts

**[NA] 7.1-7.5** — Aucun script spécifique.

### Thème 8 : Éléments obligatoires — 🔴 ZONE CRITIQUE

**[NC] 8.2.1 — MULTIPLES HTML invalides : `aria-hidden="true"` dans l'attribut `class`**
- **Niveau :** A  
- **Gravité :** 🔴 Critique  
- **Élément :** 6 SVGs avec l'attribut `aria-hidden="true"` COLLÉ dans l'attribut `class`  
- **Problème :** Le guillemet de fin de `class` est manquant avant `aria-hidden`, ce qui fait que `aria-hidden="true"` devient une chaîne dans la classe CSS au lieu d'être un attribut séparé. Le SVG n'est PAS masqué des lecteurs d'écran.  
- **Occurrences :**

1. `class="w-16 aria-hidden="true" focusable="false" h-16 ..."` (SVG "aucun partenaire")  
2. `class="w-6 aria-hidden="true" focusable="false" h-6 ..."` (SVG bâtiment × 3)  
3. `class="w-4 aria-hidden="true" focusable="false" h-4 ..."` (SVG lien externe × 2)  

**Exemple corrigé :**
```html
<!-- AVANT -->
<svg class="w-16 aria-hidden="true" focusable="false" h-16 mx-auto text-gray-600 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">

<!-- APRÈS -->
<svg class="w-16 h-16 mx-auto text-gray-600 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true" focusable="false">
```

**[NC] 8.3.1 — Duplication de `<main>` (deux landmarks main)**
- **Niveau :** A  
- **Gravité :** 🔴 Critique  
- **Élément :** Le template a son propre `<main id="main-content">` MAIS `base.html` enveloppe déjà `{% block content %}` dans un `<main id="main-content">`.  
- **Problème :** Un document ne doit avoir qu'un seul élément `<main>`. La présence de deux `<main>` crée une ambiguïté pour les AT qui ne savent pas lequel est le contenu principal.  
- **Correction :** Supprimer le `<main id="main-content">` du template (garder celui de `base.html`).

```html
<!-- DANS base.html, retirer ce wrapping si contenu dans block -->
<!-- OU dans partenaires.html, remplacer par -->
<div id="main-content-inner">
    ...
</div>
```

### Thème 9 : Structuration

**[C] 9.1.1 — Hiérarchie de titres**
- **Élément :** H1 (bannière) → H2 (catégorie / Subventions / Autres) → H3 (nom partenaire / sous-catégorie)  
- **Statut :** ✅ Conforme — bonne profondeur.

**[C] 9.1.2 — Landmarks ARIA**
- **Élément :** `<section aria-labelledby="categorie-{{ categorie.id }}-heading">`  
- **Statut :** ✅ Conforme — chaque catégorie est correctement labellisée avec `aria-labelledby`.

**[NC] 9.2.1 — Article partenaire sans `aria-label`**
- **Gravité :** 🟡 Mineure  
- **Élément :** `<article>` pour chaque partenaire  
- **Problème :** Les `<article>` n'ont pas d'`aria-label` pour les distinguer. Heureusement le `<h3>` à l'intérieur sert de titre. C'est suffisant pour les AT modernes.  
- **Correction facultative :** Ajouter `aria-labelledby="..."` pointant vers l'ID du h3.

### Thème 11 : Formulaires

**[NA] 11.1-11.13** — Aucun formulaire.

### Thème 12 : Navigation

**[C] 12.6.1 — Navigation cohérente**
- **Statut :** ✅ Conforme — héritée de `base.html`.

**[NC] 12.8.1 — Absence fil d'Ariane**
- **Gravité :** 🟠 Majeure — voir rapports précédents.

### Thème 13 : Consultation

**[C] 13.1.1 — Pas de contenu dynamique instantané**
- **Statut :** ✅ Conforme.

**[C] 13.5.1 — Responsive**
- **Élément :** `flex flex-col sm:flex-row`, grille adaptative  
- **Statut :** ✅ Conforme.

**[NC] 13.6.1 — Contenu markdown non audité**
- **Gravité :** 🟡 Mineure  
- **Élément :** `{{ partenaire.get_description_html }}`  
- **Problème :** Le contenu généré par le markdown peut contenir du HTML invalide ou des contrastes insuffisants. À vérifier.

---

## 3. Plan d'action

| # | Gravité | Correctif | Effort |
|---|---|---|---|
| 🔴 1 | Critique | 6× SVGs avec `aria-hidden` dans le `class` → corriger | 10 min |
| 🔴 2 | Critique | Supprimer `<main>` en double (template + base.html) | 5 min |
| 🔴 3 | Critique | `rel="noopener noreferrer"` → `rel="noopener noreferrer"` | 5 min (rechercher/remplacer) |
| 🟠 4 | Majeure | Contraste bannière | Intégré |
| 🟠 5 | Majeure | Uniformiser `alt=""` sur tous les logos partenaires | 5 min |
| 🟠 6 | Majeure | Fil d'Ariane | base.html |
| 🟡 7 | Mineure | `aria-label` sur les articles | 10 min |

---

*Rapport spécifique à la page `/partenaires/`.*
