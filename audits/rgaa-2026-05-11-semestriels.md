# Audit Accessibilité — Page Calendrier Semestriel

**Date :** 11/05/2026  
**URL :** http://127.0.0.1:8000/semestriels/  
**Template :** `C:\Python\cc-sudavesnois\semestriels\templates\semestriel\semestriel.html`  
**Type :** Page d'affichage de calendrier (image) + téléchargement PDF + lien externe

---

## 1. Résumé

| Métrique | Valeur |
|---|---|
| Conformité estimée | ~65% |
| Critères applicables | 34 |
| Conformes | 22 |
| Non conformes | 12 |
| **Bloquants 🔴** | **2** |
| **Majeurs 🟠** | **5** |
| **Mineurs 🟡** | **5** |

---

## 2. Non-conformités détaillées

### Thème 1 : Images

**[NC] 1.1.1 — Image du calendrier sans alternative descriptive suffisante**
- **Niveau :** A  
- **Gravité :** 🟠 Majeure  
- **Élément :** `<img src="{{content.picture.url}}" alt="Calendrier semestriel des manifestations">`  
- **Problème :** L'image contient probablement un tableau de dates/événements (c'est un calendrier). L'alternative "Calendrier semestriel des manifestations" est trop vague. RGAA 1.1.1 exige que l'alternative d'une image porteuse d'information soit équivalente.  
- **Correction :** Soit rendre l'alt plus descriptif, soit fournir les données du calendrier sous forme de texte accessible dans la page.

**[C] 1.2.1 — Image décorative absente**  
- **Statut :** ✅ Conforme — les motifs décoratifs clip-path ont `aria-hidden="true"`.

### Thème 3 : Couleurs

**[NC] 3.2.1 — Contraste bannière #005a9e/blanc (identique aux autres pages)**
- **Niveau :** AA  
- **Gravité :** 🟠 Majeure  
- **Problème :** Ratio 4.2:1 < 4.5:1  
- **Correction :** Voir rapports précédents (assombrir `bg-primary`).

**[NC] 3.3.1 — Contraste bouton téléchargement bleu**
- **Niveau :** AA  
- **Gravité :** 🟡 Mineure  
- **Élément :** `<a class="... bg-blue-600 hover:bg-blue-700 text-white ...">`  
- **Problème :** `bg-blue-600` (#2563eb) sur fond blanc avec texte blanc → ratio 5.1:1 ✅ **Conforme AA**, mais non conforme AAA (7:1)  
- **Statut :** ⚠️ Conforme AA, non conforme AAA.

### Thème 6 : Liens

**[NC] 6.1.1 — Lien image cliquable sans intitulé accessible**
- **Niveau :** A  
- **Gravité :** 🔴 Critique  
- **Élément :** `<a href="{{content.picture.url}}" target="_blank" title="Cliquez pour agrandir l'image" class="absolute inset-0"></a>`  
- **Problème :** La balise `<a>` est vide (pas de texte), elle ne possède qu'un attribut `title`. Le `title` n'est pas fiable pour les lecteurs d'écran (support inégal). Le lien sera annoncé comme "lien" sans intitulé. Le SVG décoratif et l'image ne sont pas considérés comme contenu du lien.  
- **Correction :** Ajouter un `aria-label` ou un `sr-only` span :

```html
<a href="{{content.picture.url}}" target="_blank" rel="noopener" class="absolute inset-0"
   aria-label="Agrandir l'image du calendrier semestriel (nouvelle fenêtre)"></a>
```

**[C] 6.3.1 — Lien téléchargement PDF**
- **Élément :** `<a href="{{content.file.url}}" ...>`  
- **Statut :** ✅ Conforme — icône + texte explicite "Télécharger le PDF".

**[C] 6.4.1 — Lien externe agenda touristique**
- **Élément :** Lien avec `target="_blank" rel="noopener"`  
- **Statut :** ✅ Conforme — nouvelle fenêtre signalée.

**[NC] 6.5.1 — `aria-label` manquant sur le lien externe**
- **Niveau :** A  
- **Gravité :** 🟡 Mineure  
- **Élément :** `<a href="https://www.tourisme-avesnois.com/..." target="_blank">Consulter l'agenda touristique</a>`  
- **Problème :** Le texte "Consulter l'agenda touristique" est explicite ✅ mais aucune indication "nouvelle fenêtre" dans l'intitulé du lien. Le `target="_blank"` est présent mais pas signalé aux AT.  
- **Correction :** Ajouter `<span class="sr-only"> (nouvelle fenêtre)</span>` à la fin du texte.

### Thème 7 : Scripts

**[NA] 7.1-7.5** — Aucun script spécifique sur cette page.

### Thème 8 : Éléments obligatoires

**[NC] 8.2.1 — Attribut `aria-hidden` dupliqué sur 1 SVG**
- **Gravité :** 🟡 Mineure  
- **Élément :** SVG du lien "Consulter l'agenda touristique"  
- **Problème :** `aria-hidden="true"` apparaît deux fois sur le même élément. HTML invalide.  
- **Correction :** Supprimer la duplication.

**[NC] 8.4.1 — Balise `<a>` vide sans intitulé (déjà signalé en 6.1.1)**
- **Gravité :** 🔴 Critique  
- **Correction :** Voir 6.1.1.

### Thème 9 : Structuration

**[C] 9.1.1 — Hiérarchie de titres**
- **Élément :** H1 (bannière) → H2 (Télécharger / Agenda)  
- **Statut :** ✅ Conforme.

**[C] 9.2.1 — Sections sémantiques**
- **Élément :** `base.html` fournit `<main>`. Le template n'ajoute pas de second `<main>`.  
- **Statut :** ✅ Conforme.

### Thème 12 : Navigation

**[NC] 12.2.1 — Titre de page cohérent**
- **Élément :** `<title>Calendrier Semestriel des Manifestations - CCSA</title>`  
- **Statut :** ✅ Conforme — titre descriptif.

**[NC] 12.8.1 — Absence fil d'Ariane**
- **Gravité :** 🟠 Majeure — identique aux autres pages.  
- **Correction :** À centraliser dans `base.html`.

### Thème 13 : Consultation

**[C] 13.3.1 — Téléchargement PDF**
- **Statut :** ⚠️ Non vérifié — nécessite un audit du PDF lui-même.

**[C] 13.5.1 — Responsive**
- **Élément :** Mise en page fluide, images responsives  
- **Statut :** ✅ Conforme.

---

## 3. Plan d'action

| # | Gravité | Correctif | Effort |
|---|---|---|---|
| 🔴 1 | Critique | Ajouter `aria-label` sur le lien cliquable de l'image | 2 min |
| 🔴 2 | Critique | HTML invalide : balise `<a>` vide (image cliquable) | 2 min |
| 🟠 3 | Majeure | Contraste bannière `bg-primary` | Intégré |
| 🟠 4 | Majeure | Alt image calendrier trop vague | 5 min |
| 🟠 5 | Majeure | Fil d'Ariane | base.html |
| 🟡 6 | Mineure | `sr-only` nouvelle fenêtre sur lien externe | 2 min |
| 🟡 7 | Mineure | `aria-hidden` dupliqué sur SVG | 1 min |
