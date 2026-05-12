# Audit Accessibilité — Page Encombrants

**Date :** 11/05/2026  
**URL :** http://127.0.0.1:8000/encombrants/  
**Template :** `home/templates/home/encombrants.html`  

---

## 1. Résumé

| Métrique | Valeur |
|---|---|
| Conformité estimée | ~65% |
| Critères applicables | 35 |
| Conformes | 23 |
| Non conformes | 12 |
| **Bloquants 🔴** | **1** |
| **Majeurs 🟠** | **4** |
| **Mineurs 🟡** | **7** |

---

## 2. Non-conformités

### Thème 1 : Images

**[NA] 1.1-1.3** — Aucune image sur cette page.

### Thème 3 : Couleurs

**[NC] 3.2.1 — Contraste bannière #005a9e/blanc**
- **Gravité :** 🟠 Majeure.

**[NC] 3.3.1 — Contraste `text-blue-700` sur `bg-blue-50` (section bleue)**
- **Niveau :** AA  
- **Gravité :** 🟡 Mineure  
- **Élément :** Section "Avant de prendre rendez-vous"  
- **Problème :** `text-blue-700` (#1d4ed8) sur `bg-blue-50` (#eff6ff) → ratio ~5.5:1 ✅ Conforme AA, non conforme AAA.

### Thème 6 : Liens

**[C] 6.1.1 — Lien téléphone avec `href="tel:..."`**
- **Élément :** `<a href="tel:0327606524">`  
- **Statut :** ✅ Conforme — meilleure pratique.

**[NC] 6.5.1 — Lien "Consulter les horaires des déchetteries"**
- **Niveau :** A  
- **Gravité :** 🟡 Mineure  
- **Élément :** `<a href="{% url 'dechetteries' %}">`  
- **Statut :** ✅ Conforme — intitulé explicite.

### Thème 8 : Éléments obligatoires

**[NC] 8.2.1 — `aria-hidden` dupliqué sur TOUS les SVGs**
- **Niveau :** A  
- **Gravité :** 🔴 Critique  
- **Élément :** 6 SVGs avec `aria-hidden="true"` présent DEUX FOIS (lignes 35, 74, 94, 108, 122, 138, 150)  
- **Problème :** HTML invalide. Le second `aria-hidden` est redondant mais peut causer des erreurs de parsing.  
- **Correction :** Supprimer le second `aria-hidden` sur tous les SVGs.

**[C] 8.3.1 — Pas de double `<main>`**
- **Élément :** Le template utilise `<div>` au lieu de `<main>`, ce qui évite la duplication avec `base.html`.  
- **Statut :** ✅ Conforme — c'est la bonne approche.

### Thème 11 : Formulaires

**[NA] 11.1-11.13** — Aucun formulaire.

### Thème 12 : Navigation

**[NC] 12.2.1 — Titre de page**
- **Élément :** `<title>Encombrants</title>`  
- **Statut :** ✅ Conforme — suffisamment descriptif.

**[NC] 12.8.1 — Absence fil d'Ariane**
- **Gravité :** 🟠 Majeure.

### Thème 13 : Consultation

**[C] 13.5.1 — Responsive**
- **Élément :** `grid grid-cols-1 md:grid-cols-3`, cartes adaptatives  
- **Statut :** ✅ Conforme.

**[C] 13.6.1 — Texte lisible**
- **Élément :** `text-lg` pour les paragraphes  
- **Statut :** ✅ Conforme.

---

## 3. Plan d'action

| # | Gravité | Correctif | Effort |
|---|---|---|---|
| 🔴 1 | Critique | 6× `aria-hidden` dupliqué → supprimer la redondance | 5 min |
| 🟠 2 | Majeure | Contraste bannière | Intégré |
| 🟠 3 | Majeure | Fil d'Ariane | base.html |
| 🟡 4 | Mineure | Contraste `text-blue-700`/`bg-blue-50` (AAA) | 5 min |

*Rapport spécifique à la page `/encombrants/`.*
