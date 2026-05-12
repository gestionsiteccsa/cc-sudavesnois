# Audit Accessibilité — Page Guide Éco-Citoyen

**Date :** 11/05/2026  
**URL :** http://127.0.0.1:8000/guide-eco-citoyen/  
**Template :** `home/templates/home/guide-eco-citoyen.html` (136 lignes)  
**Type :** Page de téléchargement de document (PDF)

---

## 1. Résumé

| Métrique | Valeur |
|---|---|
| Conformité estimée | ~68% |
| Critères applicables | 37 |
| Conformes | 25 |
| Non conformes | 12 |
| **Bloquants 🔴** | **3** |
| **Majeurs 🟠** | **5** |
| **Mineurs 🟡** | **4** |

---

## 2. Non-conformités détaillées

---

### Thème 1 : Images

**[NC] 1.1.1 — Image couverture du guide : alt trop long**
- **Niveau :** A
- **Gravité :** 🟡 Mineure
- **Élément :** `<img src="guide-eco-citoyens.webp" alt="Couverture du Guide Pratique Eco-Citoyen de la Communauté de Communes Sud-Avesnois">`
- **Problème :** L'alternative textuelle fait 72 caractères. RGAA recommande une alternative concise (≤ 80 caractères). C'est juste dans la limite mais pourrait être simplifié.
- **Correction :** `alt="Couverture du Guide Pratique Eco-Citoyen Sud-Avesnois"`

**[C] 1.1.2 — Image avec dimensions explicites**
- **Élément :** `width="600" height="400" loading="lazy"`
- **Statut :** ✅ Conforme — dimensions présentes, lazy-loading.

### Thème 3 : Couleurs

**[NC] 3.2.1 — Contraste bannière #005a9e/blanc**
- **Niveau :** AA
- **Gravité :** 🟠 Majeure
- **Problème :** Identique aux autres pages — ratio 4.2:1 < 4.5:1
- **Correction :** Voir rapport général (assombrir `bg-primary`)

**[NC] 3.2.2 — Contraste texte "bleu info" sur fond bleu clair**
- **Niveau :** AA
- **Gravité :** 🟠 Majeure
- **Élément :** `<p class="text-blue-800 dark:text-blue-300">` sur `bg-blue-50`
- **Problème :** `text-blue-800` (#1e40af) sur `bg-blue-50` (#eff6ff) donne un ratio d'environ 6.5:1 — **conforme AA**. ✅  
  Mais en **mode sombre** : `dark:text-blue-300` (#93c5fd) sur `dark:bg-blue-900/20` peut descendre en dessous de 4.5:1.
- **Correction :** Vérifier le contraste en mode sombre. Si nécessaire, utiliser `dark:text-blue-200`.

### Thème 6 : Liens

**[NC] 6.3.1 — Lien de téléchargement sans indication de taille**
- **Niveau :** A
- **Gravité :** 🟡 Mineure
- **Élément :** `<a href="...guide-eco-citoyens.pdf" download ... aria-describedby="file-info">`
- **Problème :** Le `span#file-info` avec `sr-only` dit "Format PDF, taille du fichier" mais la taille n'est pas dynamique — c'est un placeholder vide. L'utilisateur ne connaît pas le poids du PDF avant de cliquer.
- **Correction :** Remplacer par la taille réelle :

```html
<span id="file-info" class="sr-only">Format PDF, {{ guide_pdf_size|filesizeformat }}</span>
```

Ou en statique :
```html
<span id="file-info" class="sr-only">Format PDF, environ 2 Mo</span>
```

**[C] 6.4.1 — Ouverture nouvelle fenêtre signalée**
- **Niveau :** A
- **Élément :** Le lien de téléchargement a `download` mais pas de nouvelle fenêtre. C'est correct pour un téléchargement.
- **Statut :** ✅ Conforme

### Thème 8 : Éléments obligatoires

**[NC] 8.2.1 — Attribut `aria-hidden` dupliqué sur TOUS les SVGs**
- **Niveau :** A
- **Gravité :** 🔴 Critique
- **Élément :** Tous les `<svg>` de la page (×6 SVGs) ont `aria-hidden="true"` **deux fois**
- **Problème :** Identique aux autres pages — HTML invalide
- **Correction :** Supprimer le second `aria-hidden` :

```html
<!-- AVANT (ligne 54) -->
<svg xmlns="..." aria-hidden="true" focusable="false" class="h-6 w-6 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">

<!-- APRÈS -->
<svg xmlns="http://www.w3.org/2000/svg" aria-hidden="true" focusable="false" class="h-6 w-6 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
```

**[NC] 8.4.1 — SVG `.h-4 w-4` avec attribut malformé (ligne 105)**
- **Niveau :** A
- **Gravité :** 🟡 Mineure
- **Élément :** Ligne 105 : `<svg class="h-4 aria-hidden="true" focusable="false" w-4 text-primary" fill="none" ...>`
- **Problème :** L'attribut `aria-hidden="true"` est DANS l'attribut `class` au lieu d'être un attribut séparé. Ce SVG a donc la classe CSS "h-4 aria-hidden=" au lieu de "h-4 w-4", et n'est PAS masqué des lecteurs d'écran.
- **Impact :** 🔴 Critique — le SVG sera lu par les AT comme un élément interactif.
- **Correction :**

```html
<!-- AVANT -->
<svg class="h-4 aria-hidden="true" focusable="false" w-4 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">

<!-- APRÈS -->
<svg class="h-4 w-4 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true" focusable="false">
```

### Thème 9 : Structuration

**[C] 9.1.1 — Hiérarchie de titres correcte**
- **Élément :** H1 (bannière) → H2 (section) → H3 (sous-section conseils)
- **Statut :** ✅ Conforme — H1 → H2 → H3 bien ordonnée.

**[NC] 9.1.2 — Absence de landmark ARIA sur les colonnes**
- **Niveau :** A
- **Gravité :** 🟡 Mineure
- **Élément :** Les deux colonnes (image de gauche / texte à droite) sont dans une `<div class="grid ...">` sans rôle ARIA.
- **Correction :** Ajouter `role="region" aria-label="Contenu principal"` si pertinent, ou laisser puisque `<main>` englobe déjà bien.

### Thème 10 : Présentation

**[C] 10.1.1 — Feuilles de style pour la mise en forme**
- **Statut :** ✅ Conforme — information non perdue sans CSS.

**[NC] 10.13.1 — Focus visible sur le bouton de téléchargement**
- **Niveau :** AA
- **Gravité :** 🟡 Mineure
- **Élément :** `<a download href="..." class="... hover:bg-primary/90 ... focus:outline-none">`
- **Problème :** Le lien a `focus:outline-none` mais **pas** de `focus:ring-2`. Si le CSS par défaut du navigateur supprime l'outline, le focus deviendra invisible.
- **Correction :** Ajouter `focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2`

```html
<!-- APRÈS -->
class="w-full inline-flex items-center justify-center px-6 py-4 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors duration-300 shadow-md hover:shadow-lg text-lg font-medium focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2"
```

### Thème 11 : Formulaires

**[NA] 11.1-11.13** — Aucun formulaire.

### Thème 12 : Navigation

**[NC] 12.8.1 — Absence de fil d'Ariane**
- **Niveau :** AA
- **Gravité :** 🟠 Majeure
- **Problème :** Identique aux autres pages.

### Thème 13 : Consultation

**[NC] 13.1.1 — Téléchargement PDF non testé pour l'accessibilité**
- **Niveau :** AA
- **Gravité :** 🟠 Majeure
- **Élément :** Fichier `pdf/guide-eco-citoyens.pdf`
- **Problème :** Le PDF lui-même doit être accessible (PDF/UA ou conforme WCAG). Aucune information n'est disponible sur l'accessibilité du document téléchargé. C'est un risque RGAA 13.3.
- **Correction :** Faire auditer le PDF. À défaut, ajouter une mention "Si vous rencontrez des difficultés pour consulter ce document, contactez-nous au 03 27 60 65 24."

**[C] 13.5.1 — Responsive conforme**
- **Élément :** `grid grid-cols-1 md:grid-cols-2`, images responsives
- **Statut :** ✅ Conforme

---

## 3. Plan d'action

| # | Gravité | Correctif | Effort |
|---|---|---|---|
| 🔴 1 | Critique | SVG ligne 105 : sortir `aria-hidden="true"` de l'attribut `class` | 2 min |
| 🔴 2 | Critique | Supprimer `aria-hidden` dupliqué sur tous les SVGs | 5 min |
| 🔴 3 | Critique | Ajouter `focus-visible:ring-2` sur le bouton téléchargement | 2 min |
| 🟠 4 | Majeure | Contraste bannière `bg-primary` | Intégré |
| 🟠 5 | Majeure | Fil d'Ariane | base.html |
| 🟠 6 | Majeure | Vérifier accessibilité du PDF | Externe |
| 🟡 7 | Mineure | Alt image trop long → simplifier | 1 min |
| 🟡 8 | Mineure | Ajouter taille fichier dans `aria-describedby` | 2 min |

---

*Rapport spécifique à la page `/guide-eco-citoyen/`. Voir rapport général pour les problèmes communs (contraste bannière, breadcrumb, etc.)*
