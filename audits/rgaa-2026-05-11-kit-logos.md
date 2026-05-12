# Audit Accessibilité — Page Kit Logos

**Date :** 11/05/2026  
**URL :** http://127.0.0.1:8000/kit-logos/  
**Template :** `home/templates/home/kit-logos.html`  

---

## 1. Résumé

| Métrique | Valeur |
|---|---|
| Conformité estimée | ~55% |
| Critères applicables | 38 |
| Conformes | 21 |
| Non conformes | 17 |
| **Bloquants 🔴** | **4** |
| **Majeurs 🟠** | **5** |
| **Mineurs 🟡** | **8** |

---

## 2. Non-conformités

### Thème 1 : Images

**[C] 1.1.1 — Logos avec `alt` descriptifs**
- **Élément :** `alt="Logo de la Communauté de Communes Sud-Avesnois - version couleur"`  
- **Statut :** ✅ Conforme — alternatives textuelles détaillées et uniques.

**[C] 1.2.1 — Images décoratives absentes**
- **Statut :** ✅ Conforme.

### Thème 3 : Couleurs

**[NC] 3.2.1 — Contraste bannière #005a9e/blanc**
- **Gravité :** 🟠 Majeure.

**[NC] 3.2.2 — Contraste mode sombre (identique à la page accessibilité)**
- **Niveau :** AA  
- **Gravité :** 🔴 Critique  
- **Élément :** `text-gray-700 dark:text-gray-700` sur fond `dark:bg-gray-700`  
- **Problème :** Texte invisible en mode sombre (ratio 1:1). Présent sur tous les paragraphes et listes.  
- **Occurrences :** Lignes 28, 37, 46, 52, 66, 76, 83, 97, 107, 122, 130, 148, 158, 172, 182, 198, 208, 222, 233  
- **Correction :** Remplacer `dark:text-gray-700` par `dark:text-gray-300` partout.

### Thème 6 : Liens

**[C] 6.1.1 — Liens de téléchargement avec `aria-describedby`**
- **Élément :** 5 liens de téléchargement avec `aria-describedby` pointant vers des spans `sr-only` décrivant le format.  
- **Statut :** ✅ Conforme — excellente implémentation.

**[C] 6.4.1 — Nouvelle fenêtre signalée (aucun lien externe)**
- **Statut :** ✅ Conforme — pas de `target="_blank"`.

### Thème 7 : Scripts

**[NA] 7.1-7.5** — Aucun script spécifique.

### Thème 8 : Éléments obligatoires

**[NC] 8.2.1 — TOUS LES SVGs avec `aria-hidden` dans l'attribut `class`**
- **Niveau :** A  
- **Gravité :** 🔴 Critique  
- **Élément :** Tous les ~20 SVGs de la page (icônes info, téléchargement, check)  
- **Problème :** `class="w-6 aria-hidden="true" ..."` → `aria-hidden` jamais appliqué. SVGs exposés aux AT.  
- **Correction :** Même correctif que pour toutes les autres pages.

**[NC] 8.2.2 — Motifs décoratifs bannière sans `aria-hidden`**
- **Gravité :** 🟡 Mineure.

**[C] 8.3.1 — Pas de double `<main>`**
- **Statut :** ✅ Conforme — le template n'ajoute pas de `<main>`.

### Thème 10 : Présentation

**[NC] 10.10.1 — Images logos sans `width`/`height`**
- **Niveau :** A  
- **Gravité :** 🟡 Mineure  
- **Élément :** 5 images logos sans dimensions explicites (utilisent `object-contain` + `h-48`)  
- **Problème :** Les images n'ont pas de `width`/`height` définis dans le HTML. Le CLS (Cumulative Layout Shift) peut en souffrir.  
- **Correction :** Ajouter `width` et `height` basés sur les dimensions réelles des images.

### Thème 12 : Navigation

**[NC] 12.2.1 — Titre de page**
- **Élément :** `<title>Kit de logos - Communauté de Communes Sud-Avesnois</title>`  
- **Statut :** ✅ Conforme.

**[NC] 12.8.1 — Absence fil d'Ariane**
- **Gravité :** 🟠 Majeure.

### Thème 13 : Consultation

**[C] 13.5.1 — Responsive**
- **Élément :** `grid md:grid-cols-3`, `grid md:grid-cols-2`, `object-contain`  
- **Statut :** ✅ Conforme.

**[C] 13.6.1 — Textes lisibles**
- **Statut :** ✅ Conforme — `text-sm` pour les descriptions, OK.

---

## 3. Plan d'action

| # | Gravité | Correctif | Effort |
|---|---|---|---|
| 🔴 1 | Critique | ~20 SVGs avec `aria-hidden` dans `class` → corriger | 10 min |
| 🔴 2 | Critique | Mode sombre `dark:text-gray-700` invisible → `dark:text-gray-300` | 8 min |
| 🟠 3 | Majeure | Contraste bannière | Intégré |
| 🟠 4 | Majeure | Fil d'Ariane | base.html |
| 🟡 5 | Mineure | Ajouter `width`/`height` aux 5 images logos | 5 min |

*Rapport spécifique à la page `/kit-logos/`.*
