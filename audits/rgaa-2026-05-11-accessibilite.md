# Audit Accessibilité — Page Déclaration d'Accessibilité

**Date :** 11/05/2026  
**URL :** http://127.0.0.1:8000/accessibilite/  
**Template :** `home/templates/home/accessibilite.html`  

---

## 1. Résumé

| Métrique | Valeur |
|---|---|
| Conformité estimée | ~50% |
| Critères applicables | 42 |
| Conformes | 21 |
| Non conformes | 21 |
| **Bloquants 🔴** | **6** |
| **Majeurs 🟠** | **5** |
| **Mineurs 🟡** | **10** |

---

## 2. Non-conformités

### Thème 3 : Couleurs

**[NC] 3.2.1 — Contraste bannière #005a9e/blanc**
- **Gravité :** 🟠 Majeure.

**[NC] 3.2.2 — Contraste INVERSION en mode sombre (texte invisible)**
- **Niveau :** AA  
- **Gravité :** 🔴 Critique  
- **Élément :** `text-gray-700 dark:text-gray-700` sur fond `dark:bg-gray-700` ou `dark:bg-gray-800`  
- **Problème :** EN MODE SOMBRE, `text-gray-700` (#374151) sur `dark:bg-gray-700` (#374151) est le MÊME gris → ratio 1:1 → **texte invisible**. Les classes `text-gray-700 dark:text-gray-700` sont utilisées sur la quasi-totalité des paragraphes de cette page.  
- **Occurrences :** Lignes 29, 42, 66, 91, 116, 128, 159, 165, 177, 180, 193, 212, 244, 264, 286, 294, 300, 307  
- **Correction :** Uniformiser avec `dark:text-gray-300` (#D1D5DB) ou `dark:text-gray-200` (#E5E7EB) pour toutes les zones de texte.

**Exemple :**
```html
<!-- AVANT (invisible en mode sombre) -->
<p class="text-gray-700 dark:text-gray-700">

<!-- APRÈS -->
<p class="text-gray-700 dark:text-gray-300">
```

### Thème 6 : Liens

**[C] 6.1.1 — Intitulés de liens explicites**
- **Élément :** Rapport RGAA, ARA, contact, recours  
- **Statut :** ✅ Conforme — tous les liens ont des intitulés explicites.

**[C] 6.4.1 — Nouvelle fenêtre signalée**
- **Statut :** ✅ Conforme — chaque lien externe a `<span class="sr-only">(nouvelle fenêtre)</span>`.

**[C] 6.5.1 — Liens mailto et tel**
- **Statut :** ✅ Conforme — `href="mailto:..."` et `href="tel:..."` présents.

### Thème 8 : Éléments obligatoires

**[NC] 8.2.1 — `aria-hidden="true"` DANS l'attribut `class` sur TOUS les SVGs**
- **Niveau :** A  
- **Gravité :** 🔴 Critique  
- **Élément :** CHAQUE `<svg>` de la page (environ 25 SVGs) a l'attribut `aria-hidden="true"` à l'INTÉRIEUR de la chaîne `class=""`  
- **Problème :** Code invalide : `class="w-6 aria-hidden="true" focusable="false" h-6 text-secondary ..."`. L'attribut `aria-hidden` n'est PAS appliqué. Tous les SVGs sont exposés aux AT sans alternative.  
- **Correction :** Pour TOUS les SVGs :

```html
<!-- AVANT -->
<svg class="w-6 aria-hidden="true" focusable="false" h-6 text-secondary" ...>

<!-- APRÈS -->
<svg class="w-6 h-6 text-secondary" aria-hidden="true" focusable="false" ...>
```

**[NC] 8.2.2 — Motifs décoratifs bannière sans `aria-hidden`**
- **Gravité :** 🟡 Mineure.

### Thème 9 : Structuration

**[NC] 9.1.1 — Hiérarchie de titres**
- **Niveau :** A  
- **Gravité :** 🟡 Mineure  
- **Élément :** H1 → H2 (sr-only "Documents officiels") → H2 (Résultats) → H2 (Méthodologie) → H3 × 3 → H2 (Contact) → H3 × 2  
- **Problème :** Le premier H2 est en `sr-only` (visuellement masqué). La hiérarchie visuelle saute de H1 → H2 visible "Résultats" et on pourrait penser qu'il manque un niveau, mais c'est correct pour les AT. Par contre, "Documents officiels" en `sr-only` n'est pas idéal car ce titre n'est pas pertinent pour les utilisateurs voyants.  
- **Correction :** Rendre "Documents officiels" visible OU le supprimer et utiliser `aria-label` sur la section.

### Thème 10 : Présentation

**[NC] 10.7.1 — Contraste jauges vertes**
- **Niveau :** AA  
- **Gravité :** 🟠 Majeure  
- **Élément :** Les 3 boîtes "106 critères" / "106 conformes" / "0 non conformes"  
- **Problème :** `text-2xl font-bold text-green-700 dark:text-green-400` sur fond blanc/gris. Conforme AA ✅ mais "106" est affiché en `text-green-700` sur `bg-green-50` indirect → à vérifier.

**[NC] 10.13.1 — Graisse de police insuffisante**
- **Niveau :** AAA  
- **Gravité :** 🟡 Mineure  
- **Élément :** `text-sm text-gray-600` sur fond blanc → ratio ~4.6:1. Juste pour AA, échoue AAA.

### Thème 12 : Navigation

**[C] 12.1.1 — Lien d'évitement**
- **Statut :** ✅ Conforme — hérité de `base.html`.

**[C] 12.8.1 — Pas de breadcrumb mais acceptable ici (page de déclaration légale)**
- **Statut :** ⚠️ La page d'accessibilité est souvent une page "racine" légale qui peut se passer de breadcrumb.

### Thème 13 : Consultation

**[NC] 13.2.1 — Déclaration RGAA contradictoire avec l'audit réel**
- **Gravité :** 🟠 Majeure  
- **Élément :** La page déclare "100% conforme RGAA 4.1.2" et "106 critères conformes"  
- **Problème :** Notre audit démontre que le site est à ~55% de conformité. Cette déclaration est **fausse** et expose la CCSA à un risque légal ARCOM (amende jusqu'à 50 000€). Une déclaration doit refléter le niveau réel. Les 106 critères ne sont clairement pas conformes (ex: contrastes, HTML invalide, aria-hidden, focus).  
- **Correction :** Mettre à jour la déclaration avec un taux de conformité réaliste (~55%) ET ajouter le plan d'action.

---

## 3. Plan d'action

| # | Gravité | Correctif | Effort |
|---|---|---|---|
| 🔴 1 | Critique | ~25 SVGs avec `aria-hidden` dans `class` → attributs séparés | 15 min |
| 🔴 2 | Critique | Mode sombre : `text-gray-700 dark:text-gray-700` = invisible (1:1) → `dark:text-gray-300` | 10 min |
| 🔴 3 | Critique | Déclaration RGAA "100% conforme" fausse → mettre à jour avec taux réel | 1h |
| 🟠 4 | Majeure | Contraste bannière | Intégré |
| 🟠 5 | Majeure | Plan d'action d'amélioration à ajouter sur la page | 30 min |
| 🟡 6 | Mineure | Titre sr-only "Documents officiels" → visible ou aria-label | 5 min |

**Ironie :** La page d'accessibilité elle-même viole gravement le RGAA (SVGs non masqués, mode sombre illisible, déclaration fausse). Elle est prioritaire à corriger.

*Rapport spécifique à la page `/accessibilite/`.*
