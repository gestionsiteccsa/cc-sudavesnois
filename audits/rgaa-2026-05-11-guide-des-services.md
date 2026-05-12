# Audit Accessibilité — Page Guide des Services

**Date :** 11/05/2026  
**URL :** http://127.0.0.1:8000/guide-des-services/  
**Template :** `home/templates/home/equipe.html`  

---

## 1. Résumé

| Métrique | Valeur |
|---|---|
| Conformité estimée | ~70% |
| Critères applicables | 28 |
| Conformes | 20 |
| Non conformes | 8 |
| **Bloquants 🔴** | **1** |
| **Majeurs 🟠** | **3** |
| **Mineurs 🟡** | **4** |

---

## 2. Non-conformités

### Thème 1 : Images

**[C] 1.1.1 — Image guide des services**
- **Élément :** `alt="Guide des services de la Communauté de Communes Sud-Avesnois"`  
- **Statut :** ✅ Conforme.

**[NC] 1.1.2 — Image cliquable redondante**
- **Niveau :** A  
- **Gravité :** 🟡 Mineure  
- **Élément :** L'image est dans un `<a>` qui renvoie vers la même image, et aussi vers le même PDF dans 2 autres liens juste en dessous. L'image-link `aria-label="Agrandir l'image..."` ouvre la même image (pas une version agrandie). C'est trompeur.  
- **Correction :** Supprimer le lien overlay sur l'image, ou en faire un vrai lien vers une version haute résolution.

### Thème 6 : Liens

**[C] 6.1.1 — Intitulés de liens explicites**
- **Élément :** "Visualiser le PDF" et "Télécharger le PDF" avec `aria-label`  
- **Statut :** ✅ Conforme.

**[NC] 6.4.1 — Lien téléchargement sans `rel="noopener"`**
- **Niveau :** A  
- **Gravité :** 🟡 Mineure  
- **Élément :** Lien "Télécharger le PDF" (ligne 48) a `download` mais pas `rel="noopener"` contrairement au lien "Visualiser".  
- **Correction :** Ajouter `rel="noopener"` même sur les téléchargements.

```html
<a href="{% static 'pdf/Guidedesservicesdigital.pdf' %}" download
   rel="noopener" class="...">
```

### Thème 8 : Éléments obligatoires

**[C] 8.2.1 — Pas de double `<main>`**
- **Statut :** ✅ Conforme — le template n'ajoute PAS son propre `<main>`.

**[C] 8.3.1 — HTML valide**
- **Statut :** ✅ Conforme — pas d'attribut dupliqué détecté.

### Thème 9 : Structuration

**[C] 9.1.1 — Hiérarchie de titres**
- **Élément :** H1 (bannière) → H2 (Consulter le guide)  
- **Statut :** ✅ Conforme — page courte, pas besoin de niveaux plus profonds.

### Thème 12 : Navigation

**[NC] 12.2.1 — Titre de page**
- **Élément :** `<title>Guide des services - CCSA</title>`  
- **Statut :** ✅ Conforme.

**[NC] 12.8.1 — Absence fil d'Ariane**
- **Gravité :** 🟠 Majeure.

### Thème 13 : Consultation

**[NC] 13.3.1 — PDF non audité**
- **Gravité :** 🟠 Majeure  
- **Élément :** Fichier `pdf/Guidedesservicesdigital.pdf`  
- **Problème :** L'accessibilité du PDF lui-même n'est pas vérifiée. Risque RGAA 13.3.  
- **Correction :** Faire auditer le PDF. Ajouter une mention de contact en cas de difficulté.

---

## 3. Plan d'action

| # | Gravité | Correctif | Effort |
|---|---|---|---|
| 🔴 1 | Majeure | Audit accessibilité PDF guide des services | Externe |
| 🟠 2 | Majeure | Contraste bannière | Intégré |
| 🟠 3 | Majeure | Fil d'Ariane | base.html |
| 🟡 4 | Mineure | Lien overlay image trompeur → supprimer ou améliorer | 5 min |
| 🟡 5 | Mineure | Ajouter `rel="noopener"` sur lien téléchargement | 1 min |

*Rapport spécifique à la page `/guide-des-services/`.*
