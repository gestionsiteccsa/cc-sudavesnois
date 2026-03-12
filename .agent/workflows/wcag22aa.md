# WCAG 2.2 AA Analysis Skill

## Description

Ce skill analyse les projets web selon les normes WCAG 2.2 niveau AA pour identifier les problèmes d'accessibilité et proposer des solutions.

## Instructions

### 1. Analyse des templates HTML

Vérifier les critères suivants :

**1.1 Alternatives textuelles (Niveau A)**
- [ ] 1.1.1 : Toutes les images porteuses d'information ont un attribut `alt` pertinent
- [ ] Les images décoratives ont `alt=""` ou `role="presentation"`
- [ ] Les images complexes ont une description longue (aria-describedby, figure/figcaption)
- [ ] Les CAPTCHA ont une alternative textuelle

**1.3 Adaptable (Niveau A-AA)**
- [ ] 1.3.1 : Structure sémantique correcte (h1-h6, nav, main, article, section)
- [ ] 1.3.2 : Ordre de lecture logique (DOM visuellement cohérent)
- [ ] 1.3.5 : Identification des champs de formulaire (autocomplete)

**2.4 Navigable (Niveau A-AA)**
- [ ] 2.4.1 : Lien d'évitement présent et fonctionnel
- [ ] 2.4.2 : Titres de page uniques et descriptifs
- [ ] 2.4.4 : Intitulés de liens explicites
- [ ] 2.4.6 : En-têtes et étiquettes descriptives

**3.1 Lisible (Niveau A-AA)**
- [ ] 3.1.1 : Langue de la page déclarée (`lang`)
- [ ] 3.1.2 : Langue des passages étrangers déclarée

**3.3 Assistance à la saisie (Niveau A-AA)**
- [ ] 3.3.1 : Messages d'erreur identifiés
- [ ] 3.3.2 : Étiquettes associées aux champs (label/for ou aria-label)
- [ ] 3.3.8 : Prévention des erreurs réversibles

**4.1 Compatible (Niveau A-AA)**
- [ ] 4.1.2 : Nom, rôle, valeur des composants d'interface (boutons, liens, formulaires)

### 2. Analyse du CSS

**1.4 Distinguable (Niveau AA)**
- [ ] 1.4.3 : Contraste texte/fond ≥ 4.5:1 (3:1 pour gros texte)
- [ ] 1.4.4 : Redimensionnement texte à 200% sans perte
- [ ] 1.4.11 : Contraste éléments non-textuels ≥ 3:1
- [ ] 1.4.12 : Espacement du texte ajustable

**2.4 Navigable (Niveau AA)**
- [ ] 2.4.7 : Focus visible et contrasté
- [ ] 2.4.13 : Contenu au survol/focus contrôlable

### 3. Analyse du JavaScript

**2.1 Accessibilité au clavier (Niveau A)**
- [ ] 2.1.1 : Toutes les fonctionnalités accessibles au clavier
- [ ] 2.1.2 : Pas de piège au clavier
- [ ] 2.1.4 : Raccourcis clavier désactivables

**2.5 Modalités d'entrée (Niveau A-AA)**
- [ ] 2.5.1 : Gestes avec alternative au clavier
- [ ] 2.5.3 : Étiquette dans le nom accessible

**3.2 Prévisible (Niveau A)**
- [ ] 3.2.1 : Pas de changement de contexte au focus
- [ ] 3.2.2 : Pas de changement de contexte à la saisie

### 4. Rapport à générer

Structure du rapport :
1. Résumé exécutif (taux de conformité global)
2. Problèmes critiques (bloquants)
3. Problèmes majeurs (à corriger rapidement)
4. Problèmes mineurs (améliorations)
5. Bonnes pratiques identifiées
6. Recommandations prioritaires
7. Checklist de validation

## Checklist complète WCAG 2.2 AA

### Perceptible (1.x)

| Critère | Description | Niveau | Statut |
|---------|-------------|--------|--------|
| 1.1.1 | Contenu non textuel a alternative | A | |
| 1.2.2 | Vidéos : sous-titres | A | |
| 1.2.5 | Vidéos : audiodescription | AA | |
| 1.3.1 | Information et relations | A | |
| 1.3.2 | Ordre séquentiel | A | |
| 1.3.5 | Identification finalité champs | AA | |
| 1.4.1 | Utilisation couleur | A | |
| 1.4.3 | Contraste minimum | AA | |
| 1.4.4 | Redimensionnement texte | AA | |
| 1.4.5 | Images de texte | AA | |
| 1.4.10 | Reflow | AA | |
| 1.4.11 | Contraste non-textuel | AA | |
| 1.4.12 | Espacement texte | AA | |
| 1.4.13 | Contenu survol/focus | AA | |

### Utilisable (2.x)

| Critère | Description | Niveau | Statut |
|---------|-------------|--------|--------|
| 2.1.1 | Clavier | A | |
| 2.1.2 | Pas de piège clavier | A | |
| 2.2.1 | Réglage du délai | A | |
| 2.2.2 | Pause/arrêt/masquer | A | |
| 2.3.1 | Pas de flash | A | |
| 2.4.1 | Contournement blocs | A | |
| 2.4.2 | Titre de page | A | |
| 2.4.4 | Fonction du lien | A | |
| 2.4.5 | Accès multiples | AA | |
| 2.4.6 | En-têtes et étiquettes | AA | |
| 2.4.7 | Focus visible | AA | |
| 2.5.1 | Gestes pointage | A | |
| 2.5.2 | Annulation pointage | A | |
| 2.5.3 | Étiquette dans nom | A | |

### Compréhensible (3.x)

| Critère | Description | Niveau | Statut |
|---------|-------------|--------|--------|
| 3.1.1 | Langue de la page | A | |
| 3.1.2 | Langue passage | AA | |
| 3.2.1 | Au focus | A | |
| 3.2.2 | À la saisie | A | |
| 3.2.3 | Navigation cohérente | AA | |
| 3.2.4 | Identification cohérente | AA | |
| 3.3.1 | Identification erreurs | A | |
| 3.3.2 | Étiquettes instructions | A | |
| 3.3.3 | Suggestion erreur | AA | |
| 3.3.4 | Prévention erreurs | AA | |
| 3.3.8 | Prévention réversible | AA | |

### Robuste (4.x)

| Critère | Description | Niveau | Statut |
|---------|-------------|--------|--------|
| 4.1.1 | Analyse syntaxique | A | |
| 4.1.2 | Nom, rôle, valeur | A | |
| 4.1.3 | Messages d'état | AA | |

## Outils recommandés

- axe DevTools (extension navigateur)
- Lighthouse (Chrome DevTools)
- WAVE (WebAIM)
- Colour Contrast Analyser
- NVDA/JAWS (lecteurs d'écran)

## Workflow d'analyse

1. Scanner tous les templates HTML
2. Analyser les fichiers CSS pour les contrastes
3. Vérifier les scripts JS pour l'accessibilité clavier
4. Tester avec un lecteur d'écran
5. Vérifier la navigation au clavier
6. Tester le redimensionnement à 200%
7. Générer le rapport avec priorités
