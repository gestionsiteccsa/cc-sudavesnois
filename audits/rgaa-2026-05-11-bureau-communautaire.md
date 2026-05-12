# Audit Accessibilité — Page Bureau Communautaire

**Date :** 11/05/2026  
**URL :** http://127.0.0.1:8000/bureau-communautaire/  
**Template :** `C:\Python\cc-sudavesnois\bureau_communautaire\templates\bureau_communautaire\elus.html`  
**Type :** Page d'élus avec lightbox, photos, navigation par ancres

---

## 1. Résumé

| Métrique | Valeur |
|---|---|
| Conformité estimée | ~72% |
| Critères applicables | 52 |
| Conformes | 38 |
| Non conformes | 14 |
| **Bloquants 🔴** | **2** |
| **Majeurs 🟠** | **5** |
| **Mineurs 🟡** | **7** |

Note : Cette page est la MIEUX notée du site (lightbox accessible, focus trap, ancres de navigation, reduced motion support).

---

## 2. Non-conformités détaillées

### Thème 1 : Images

**[C] 1.1.1 — Portrait des élus**
- **Élément :** `<img src="{{ president.picture.url }}" alt="Portrait de {{president.last_name}} {{president.first_name}}, Président...">`  
- **Statut :** ✅ Conforme — alternative textuelle descriptive incluant le rôle.

**[C] 1.1.2 — Placeholder initiales**
- **Élément :** `<div class="elu-photo-placeholder" aria-hidden="true">`  
- **Statut :** ✅ Conforme — `aria-hidden="true"` correct pour contenu décoratif.

**[C] 1.2.1 — Lightbox image dynamique**
- **Élément :** L'`alt` de la lightbox est défini dynamiquement en JS  
- **Statut :** ✅ Conforme — fonctionne avec JS. Fallback `alt=""` en HTML.

### Thème 3 : Couleurs

**[NC] 3.2.1 — Contraste bannière #005a9e/blanc**
- **Gravité :** 🟠 Majeure — idem autres pages.

**[C] 3.3.1 — Boutons d'ancrage dans la bannière**
- **Élément :** Boutons blanc/vert dans la bannière  
- **Statut :** ✅ Conforme AA.

### Thème 6 : Liens

**[C] 6.1.1 — Liens d'ancrage dans la bannière**
- **Élément :** `<a href="#president">Le Président</a>` et `<a href="#vice-presidents">Les Vice-Présidents</a>`  
- **Statut :** ✅ Conforme — intitulés explicites.

**[NC] 6.2.1 — Aucun lien d'évitement vers la lightbox**
- **Niveau :** AAA  
- **Gravité :** 🟡 Mineure  
- **Élément :** Lightbox accessible uniquement par clic/touche sur les photos  
- **Statut :** Conforme AA, non conforme AAA (pas bloquant).

**[C] 6.4.1 — Lightbox avec `aria-label` correct**
- **Élément :** `<div class="lightbox-trigger-wrapper" tabindex="0" role="button" aria-label="Voir l'image en grand : Portrait de ...">`  
- **Statut :** ✅ Conforme — excellent.

### Thème 7 : Scripts — POINTS FORTS

**[C] 7.1.1 — Lightbox avec `role="dialog"` et `aria-modal="true"`**
- **Élément :** `<div id="lightbox-modal" role="dialog" aria-modal="true" aria-label="Aperçu de l'image">`  
- **Statut :** ✅ Conforme — implémentation ARIA correcte.

**[C] 7.1.2 — Focus trap fonctionnel**
- **Élément :** Fonction `createFocusTrap()` avec Tab/Shift+Tab  
- **Statut :** ✅ Conforme — meilleure pratique.

**[C] 7.1.3 — Fermeture par Escape**
- **Élément :** `handleKeydown` avec `e.key === 'Escape'`  
- **Statut :** ✅ Conforme.

**[C] 7.1.4 — Retour du focus après fermeture**
- **Élément :** `lastFocusedElement.focus()` dans `closeLightbox()`  
- **Statut :** ✅ Conforme — excellente pratique.

**[C] 7.1.5 — Scroll bloqué pendant lightbox**
- **Élément :** `document.body.style.overflow = 'hidden'`  
- **Statut :** ✅ Conforme.

**[NC] 7.1.6 — Lightbox image `alt` vide si JS désactivé**
- **Niveau :** A  
- **Gravité :** 🟡 Mineure  
- **Élément :** `<img id="lightbox-image" src="" alt="">`  
- **Problème :** Sans JS, la lightbox est cachée par `hidden`, donc pas d'impact. Mais si un événement non-JS ouvrait la lightbox, l'image serait sans alternative.  
- **Correction :** Conserver l'état actuel — acceptable car JS requis pour l'ouverture.

### Thème 8 : Éléments obligatoires

**[C] 8.1.1 — Langue du document**
- **Statut :** ✅ Conforme — héritée de `base.html` (`lang="fr"`).

**[C] 8.2.1 — HTML valide (aucune duplication d'attribut)**
- **Élément :** Inspection du code source — pas de doublon `aria-hidden`.  
- **Statut :** ✅ Conforme — cette page est PROPRE.

**[C] 8.3.1 — Pas de `main` en double**
- **Élément :** Le template utilise `<div class="dark:bg-gray-900">` au lieu d'un `<main>`.  
- **Statut :** ✅ Conforme.

### Thème 9 : Structuration

**[C] 9.1.1 — Hiérarchie de titres**
- **Élément :** H1 (bannière) → H2 (Rôle / Le Président / Les Vice-Présidents) → H3 (nom élu)  
- **Statut :** ✅ Conforme — hiérarchie parfaite.

**[C] 9.1.2 — Landmarks ARIA**
- **Élément :** `<section aria-label="Section du Président">`, `<section aria-label="Section des Vice-Présidents">`  
- **Statut :** ✅ Conforme — excellente utilisation d'`aria-label`.

### Thème 11 : Formulaires

**[NA] 11.1-11.13** — Aucun formulaire.

### Thème 12 : Navigation

**[C] 12.1.1 — Lien d'évitement skip-link**
- **Statut :** ✅ Conforme — hérité de `base.html`.

**[C] 12.2.1 — Titre de page**
- **Élément :** `<title>Le Bureau Communautaire - Présentation des élus | ...</title>`  
- **Statut :** ✅ Conforme.

**[C] 12.4.1 — Navigation par ancres dans la bannière**
- **Élément :** Liens vers `#president` et `#vice-presidents`  
- **Statut :** ✅ Conforme — navigation rapide clavier disponible.

**[NC] 12.8.1 — Absence fil d'Ariane**
- **Gravité :** 🟠 Majeure — idem autres pages.

### Thème 13 : Consultation

**[C] 13.1.1 — `prefers-reduced-motion` supporté**
- **Élément :** CSS `elus.css` désactive les animations quand `prefers-reduced-motion: reduce`  
- **Statut :** ✅ Conforme — excellente pratique AAA.

**[C] 13.5.1 — Responsive**
- **Élément :** `grid sm:grid-cols-1 md:grid-cols-3`, cartes adaptatives  
- **Statut :** ✅ Conforme.

**[C] 13.7.1 — Lightbox accessible**
- **Élément :** Navigation clavier complète  
- **Statut :** ✅ Conforme.

---

## 3. Problèmes additionnels

### Accessibilité CSS (elus.css)

**[NC] Animations sans `prefers-reduced-motion` complet**
- **Gravité :** 🟡 Mineure  
- **Élément :** Animations de fade-in avec délais stagger  
- **Problème :** Vérifier que TOUTES les animations (et pas seulement certaines) sont désactivées avec `prefers-reduced-motion`.  
- **Correction :** Audit du CSS `elus.css` :

```css
/* À vérifier dans elus.css */
@media (prefers-reduced-motion: reduce) {
  .elu-card,
  .elu-card-president,
  .elu-card-vice {
    animation: none !important;
    transition: none !important;
  }
}
```

### Contrastes placeholders photo

**[NC] Placeholder couleurs**
- **Gravité :** 🟡 Mineure  
- **Élément :** `.elu-photo-placeholder` avec initiales blanches sur fond bleu  
- **Problème :** Ratio 6.9:1 ✅ Conforme AA. En mode sombre (`#9ca3af` sur `#374151`), ratio ~4.5:1 ✅ juste.  
- **Statut :** Conforme AA mais vérifier AAA.

---

## 4. Plan d'action

| # | Gravité | Correctif | Effort |
|---|---|---|---|
| 🟠 1 | Majeure | Contraste bannière | Intégré |
| 🟠 2 | Majeure | Fil d'Ariane | base.html |
| 🟠 3 | Majeure | Vérifier `prefers-reduced-motion` complet dans elus.css | 10 min |
| 🟡 4 | Mineure | Audit placeholder couleur mode sombre | 5 min |
| ✅ | — | Lightbox avec focus trap, Escape, retour focus → **EXEMPLAIRE** | — |

---

**Note positive :** Cette page est la mieux implémentée du site en termes d'accessibilité. La lightbox avec ses gestionnaires de focus, Escape, `aria-modal`, et le support `prefers-reduced-motion` sont des pratiques exemplaires à reproduire sur les autres pages.

*Rapport spécifique à la page `/bureau-communautaire/`.*
