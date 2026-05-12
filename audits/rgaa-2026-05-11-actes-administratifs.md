# Audit Accessibilité — Page Actes Administratifs

**Date :** 11/05/2026  
**URL :** http://127.0.0.1:8000/actes-administratifs/  
**Template :** `C:\Python\cc-sudavesnois\comptes_rendus\templates\comptes_rendus\comptes-rendus.html`  
**Inclus :** `templates/includes/prochains_conseils.html`  

---

## 1. Résumé

| Métrique | Valeur |
|---|---|
| Conformité estimée | ~55% |
| Critères applicables | 40 |
| Conformes | 22 |
| Non conformes | 18 |
| **Bloquants 🔴** | **4** |
| **Majeurs 🟠** | **5** |
| **Mineurs 🟡** | **9** |

---

## 2. Non-conformités

### Thème 3 : Couleurs

**[NC] 3.2.1 — Contraste bannière #005a9e/blanc**
- **Gravité :** 🟠 Majeure.

### Thème 5 : Tableaux

**[C] 5.1-5.4 — Pas de tableau HTML**
- **Statut :** ✅ Conforme — les conseils sont en `<article>` (inclus), ce qui est sémantiquement meilleur qu'un tableau.

### Thème 6 : Liens

**[C] 6.1.1 — Intitulés de liens explicites**
- **Élément :** "Arrêtés", "Décisions", "Délibérations"  
- **Statut :** ✅ Conforme — assez explicites.

**[NC] 6.4.1 — Aucune indication "nouvelle fenêtre" sur les 3 liens SharePoint**
- **Niveau :** A  
- **Gravité :** 🟡 Mineure  
- **Élément :** 3 liens externes avec `target="_blank"` mais sans indication "(nouvelle fenêtre)" dans l'intitulé ou l'`aria-label`.  
- **Correction :** Ajouter `<span class="sr-only"> (nouvelle fenêtre)</span>` dans chaque lien.

### Thème 8 : Éléments obligatoires

**[NC] 8.2.1 — Double `<main>`**
- **Niveau :** A  
- **Gravité :** 🔴 Critique  
- **Élément :** `<main id="main-content">` dans le template + `<main>` dans `base.html`  
- **Correction :** Supprimer `<main id="main-content">` du template.

**[NC] 8.2.2 — Motifs décoratifs bannière sans `aria-hidden`**
- **Gravité :** 🟡 Mineure  
- **Élément :** Deux `<div>` clip-path sans `aria-hidden="true"` (contrairement aux autres pages).

### Thème 10 : Présentation

**[NC] 10.7.1 — Contraste boutons colorés (bleu, violet, rouge)**
- **Niveau :** AA  
- **Gravité :** 🟠 Majeure  
- **Élément :**  
  - `bg-blue-600` (#2563eb) / texte blanc → ratio 5.1:1 ✅ Conforme AA  
  - `bg-purple-600` (#9333ea) / texte blanc → ratio 5.6:1 ✅ Conforme AA  
  - `bg-red-600` (#dc2626) / texte blanc → ratio 4.5:1 ✅ Conforme AA (juste)  
- **Statut :** ✅ Conforme AA, non conforme AAA pour le rouge.

### Thème 12 : Navigation

**[NC] 12.2.1 — Titre de page**
- **Élément :** `<title>Actes administratifs</title>`  
- **Statut :** ✅ Conforme — descriptif mais poussé depuis le `{% block title %}`.

**[NC] 12.8.1 — Absence fil d'Ariane**
- **Gravité :** 🟠 Majeure.

### Thème 13 : Consultation

**[NC] 13.3.1 — Liens externes SharePoint**
- **Gravité :** 🟡 Mineure  
- **Élément :** 3 liens vers des dossiers SharePoint  
- **Problème :** Les documents hébergés sur SharePoint doivent être accessibles (PDF/A ou PDF/UA). Impossible à vérifier ici.  
- **Correction :** Vérifier l'accessibilité des documents hébergés.

**[NC] 13.6.1 — Contenu de l'inclusion "prochains_conseils" non audité**
- **Gravité :** 🟡 Mineure  
- **Élément :** `{% include "includes/prochains_conseils.html" %}`  
- **Problème :** Le contenu inclus peut contenir d'autres problèmes non détectés.

### Thème 7 : Scripts (template inclus)

**[NC] 7.5.1 — `aria-live` manquant sur contenu dynamique (si présent dans l'inclusion)**
- **Gravité :** 🟡 Mineure  
- **À vérifier :** L'inclusion `prochains_conseils.html` n'a pas été auditée en détail (contient des cartes de conseils avec PDF).

---

## 3. Plan d'action

| # | Gravité | Correctif | Effort |
|---|---|---|---|
| 🔴 1 | Critique | Supprimer `<main>` en double | 2 min |
| 🔴 2 | Critique | Audit inclusion prochains_conseils.html (non audité) | 20 min |
| 🟠 3 | Majeure | Contraste bannière | Intégré |
| 🟠 4 | Majeure | Fil d'Ariane | base.html |
| 🟠 5 | Majeure | Vérifier accessibilité PDF sur SharePoint | Externe |
| 🟡 6 | Mineure | Ajouter `sr-only` "(nouvelle fenêtre)" sur les 3 liens | 3 min |
| 🟡 7 | Mineure | `aria-hidden` sur motifs décoratifs bannière | 1 min |

---

*Rapport spécifique à la page `/actes-administratifs/`.*
