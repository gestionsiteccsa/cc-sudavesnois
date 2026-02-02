---
description: Agent de design UI/UX avec esthétique distinctive anti-AI slop pour landing pages, composants et interfaces web
---

# Agent Antigravity Design System

Cet agent définit les directives de design par défaut pour créer des interfaces web distinctives et mémorables.

## ⚠️ DÉCLENCHEMENT AUTOMATIQUE

**Cet agent DOIT être appliqué automatiquement lors de :**
- Création de landing pages
- Design de composants UI
- Pages marketing ou produit
- Dashboards et interfaces applicatives
- Tout design web sans brief visuel spécifique

---

## Étape 1 : Réflexion design obligatoire

**Avant de coder, répondre à ces 3 questions :**

### 1. Objectif
> Quel problème cette interface résout-elle ? Pour qui ?

### 2. Direction esthétique
Choisir **UNE** direction audacieuse parmi :

| Direction | Caractéristiques |
|-----------|------------------|
| **Brutalement minimal** | Épuré, essentiel, contrastes forts |
| **Maximaliste contrôlé** | Dense mais organisé, riche visuellement |
| **Rétro-futuriste** | Nostalgique + moderne, néons, chrome |
| **Organique/naturel** | Courbes, textures, couleurs terre |
| **Luxe/raffiné** | Élégant, espaces généreux, or/noir |
| **Ludique** | Couleurs vives, formes rondes, animations fun |
| **Éditorial/magazine** | Typographie forte, grille éditoriale |
| **Brutaliste/brut** | Sans fioritures, bordures visibles, cru |
| **Art déco/géométrique** | Symétrie, motifs, dorures |
| **Soft/pastel** | Doux, arrondi, couleurs désaturées |
| **Industriel/utilitaire** | Fonctionnel, grilles, monospace |

### 3. Différenciation
> Qu'est-ce qui rendra ce design **MÉMORABLE** ?

---

## Étape 2 : Directives esthétiques

### Typographie

```css
/* ✅ BON - Polices distinctives */
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Outfit:wght@300;400;600&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600&family=DM+Serif+Display&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Clash+Display:wght@400;600;700&display=swap');

/* Associations recommandées */
--font-display: 'Playfair Display', serif;      /* Titres élégants */
--font-body: 'Outfit', sans-serif;               /* Corps moderne */

--font-display: 'Clash Display', sans-serif;     /* Titres bold */
--font-body: 'Sora', sans-serif;                 /* Corps géométrique */

--font-display: 'DM Serif Display', serif;       /* Titres éditorial */
--font-body: 'DM Sans', sans-serif;              /* Corps assorti */
```

**Polices recommandées :**
- Display : Playfair Display, Clash Display, DM Serif Display, Fraunces, Instrument Serif
- Body : Outfit, Sora, DM Sans, Plus Jakarta Sans, Satoshi
- Mono : JetBrains Mono, Fira Code, IBM Plex Mono

### Couleurs et thème

```css
/* ✅ BON - Palette audacieuse avec accents */
:root {
  /* Couleurs dominantes */
  --color-bg: #0a0a0a;
  --color-text: #fafafa;
  
  /* Accent principal tranchant */
  --color-accent: #ff6b35;
  --color-accent-soft: rgba(255, 107, 53, 0.1);
  
  /* Gradients sophistiqués */
  --gradient-hero: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  --gradient-mesh: radial-gradient(at 40% 20%, #1a1a2e 0%, transparent 50%),
                   radial-gradient(at 80% 0%, #16213e 0%, transparent 50%);
}

/* Thème clair alternatif */
[data-theme="light"] {
  --color-bg: #f8f7f4;
  --color-text: #1a1a1a;
  --color-accent: #2563eb;
}
```

### Backgrounds et atmosphère

```css
/* ✅ BON - Créer de la profondeur, pas de couleurs plates */

/* Noise texture overlay */
.noise-overlay::before {
  content: '';
  position: fixed;
  inset: 0;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E");
  opacity: 0.03;
  pointer-events: none;
  z-index: 1000;
}

/* Gradient mesh background */
.gradient-mesh {
  background: 
    radial-gradient(at 0% 0%, var(--color-accent-soft) 0%, transparent 50%),
    radial-gradient(at 100% 0%, rgba(139, 92, 246, 0.15) 0%, transparent 50%),
    radial-gradient(at 100% 100%, rgba(236, 72, 153, 0.1) 0%, transparent 50%),
    var(--color-bg);
}

/* Glassmorphism */
.glass {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}
```

### Animations et mouvement

```css
/* ✅ BON - Animations orchestrées à fort impact */

/* Page load - révélations décalées */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.hero-title {
  animation: fadeInUp 0.8s ease-out forwards;
  animation-delay: 0.1s;
  opacity: 0;
}

.hero-subtitle {
  animation: fadeInUp 0.8s ease-out forwards;
  animation-delay: 0.2s;
  opacity: 0;
}

.hero-cta {
  animation: fadeInUp 0.8s ease-out forwards;
  animation-delay: 0.4s;
  opacity: 0;
}

/* Hover states surprenants */
.card {
  transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1),
              box-shadow 0.3s ease;
}

.card:hover {
  transform: translateY(-8px) rotate(1deg);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
}

/* Bouton avec effet de brillance */
.button-shine {
  position: relative;
  overflow: hidden;
}

.button-shine::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
  transition: left 0.5s ease;
}

.button-shine:hover::before {
  left: 100%;
}
```

### Composition spatiale

```css
/* ✅ BON - Layouts inattendus */

/* Asymétrie */
.section-asymmetric {
  display: grid;
  grid-template-columns: 1fr 1.5fr;
  gap: 4rem;
}

/* Éléments qui cassent la grille */
.break-grid {
  margin-left: -5vw;
  width: calc(100% + 10vw);
}

/* Superposition (overlap) */
.overlap-section {
  margin-top: -8rem;
  position: relative;
  z-index: 10;
}

/* Espace négatif généreux */
.luxury-spacing {
  padding: clamp(4rem, 10vw, 12rem) 0;
}
```

---

## ❌ INTERDITS ABSOLUS

### Polices interdites

```css
/* ❌ NE JAMAIS UTILISER */
font-family: 'Inter', sans-serif;          /* Trop générique */
font-family: 'Roboto', sans-serif;         /* Google default */
font-family: 'Arial', sans-serif;          /* Système basique */
font-family: 'Space Grotesk', sans-serif;  /* Surexploitée par les LLMs */
font-family: sans-serif;                   /* Generic fallback seul */
```

### Couleurs interdites

```css
/* ❌ NE JAMAIS UTILISER */
/* Dégradés violets génériques sur blanc */
background: linear-gradient(to right, #8b5cf6, #a855f7);

/* Palettes "corporate" fades */
--color-primary: #3b82f6;  /* Blue-500 générique */
--color-secondary: #6b7280; /* Gray-500 fade */
```

### Patterns interdits

- Layouts prévisibles type "hero + 3 cards + features + footer"
- Structures cookie-cutter Bootstrap/Tailwind UI copiées
- Hero sections avec illustration à droite systématiques
- Cards parfaitement alignées sans surprise

---

## Règle de variation

**Chaque design DOIT être différent.**

| Variation | Options |
|-----------|---------|
| **Thème** | Alterner clair ↔ sombre |
| **Polices** | Varier les familles à chaque projet |
| **Esthétique** | Adapter au contexte (luxe, tech, créatif...) |
| **Layout** | Inventer de nouvelles compositions |

---

## Adaptation de la complexité

| Vision | Implémentation |
|--------|----------------|
| **Maximaliste** | Code élaboré, animations extensives, effets nombreux, détails riches |
| **Minimaliste** | Retenue, précision chirurgicale, attention aux espacements, typographie parfaite |

**L'élégance vient de l'exécution fidèle de la vision.**

---

## Checklist avant livraison

- [ ] Direction esthétique clairement définie
- [ ] Polices distinctives (pas de Inter/Roboto)
- [ ] Palette de couleurs cohésive avec accents forts
- [ ] Background avec atmosphère (pas de couleur plate)
- [ ] Animations orchestrées (page load, hovers)
- [ ] Layout avec au moins 1 élément surprenant
- [ ] Design mémorable et différencié

---

## Utilisation

```
/antigravity-design                    # Appliquer les directives
/antigravity-design --direction=luxe   # Forcer une direction
/antigravity-design --audit            # Vérifier un design existant
```
