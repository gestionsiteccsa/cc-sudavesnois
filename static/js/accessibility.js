/**
 * Script pour améliorer l'accessibilité du site
 * Conforme aux normes WCAG 2.1 (Web Content Accessibility Guidelines)
 */

document.addEventListener('DOMContentLoaded', function() {
    // Appliquer la taille minimale à tous les éléments interactifs (WCAG 2.1 Success Criterion 2.5.5 - Target Size)
    applyMinimumTargetSize();

    // Initialiser le filtre bleu
    initBlueFilter();
    
    // Initialiser le mode nuit
    initDarkMode();

    // Autres fonctions d'accessibilité peuvent être ajoutées ici
});

/**
 * Applique une taille minimale de 44x44 pixels à tous les éléments interactifs
 * Conforme à WCAG 2.1 Success Criterion 2.5.5 - Target Size (AAA)
 */
function applyMinimumTargetSize() {
    // Sélectionner tous les liens qui ne sont pas déjà stylés avec les classes min-height et min-width
    const interactiveElements = document.querySelectorAll('a:not([class*="min-h-"]):not([class*="min-w-"]), button:not([class*="min-h-"]):not([class*="min-w-"])');
    
    interactiveElements.forEach(element => {
        // Vérifier si l'élément a déjà un style d'affichage
        const computedStyle = window.getComputedStyle(element);
        const displayValue = computedStyle.getPropertyValue('display');
        
        // Ajouter les classes pour la taille minimale
        if (displayValue === 'inline') {
            // Si l'élément est en display inline, le convertir en inline-flex
            element.classList.add('inline-flex');
        } else if (displayValue === 'block') {
            // Si l'élément est en display block, ajouter flex
            element.classList.add('flex');
        } else if (!displayValue.includes('flex')) {
            // Pour les autres cas, utiliser inline-flex
            element.classList.add('inline-flex');
        }
        
        // Ajouter les classes pour centrer le contenu
        element.classList.add('items-center');
        
        // Ajouter les classes pour la taille minimale
        element.classList.add('min-h-[44px]');
        element.classList.add('min-w-[44px]');
        
        // Si l'élément n'a pas de padding, ajouter un padding minimal
        const paddingLeft = parseInt(computedStyle.getPropertyValue('padding-left'));
        const paddingRight = parseInt(computedStyle.getPropertyValue('padding-right'));
        
        if (paddingLeft < 8 || paddingRight < 8) {
            element.classList.add('px-2');
        }
    });
    
    // Note: Les éléments ont été ajustés pour respecter la taille minimale de 44x44 pixels
}

/**
 * Initialise la fonctionnalité de filtre bleu pour réduire la fatigue oculaire
 */
function initBlueFilter() {
    const blueFilterToggle = document.getElementById('blue-filter-toggle');
    const resetAllButton = document.getElementById('accessibility-reset-all');
    
    if (!blueFilterToggle) return;
    
    // Vérifier si le filtre bleu était activé précédemment
    const isBlueFilterEnabled = localStorage.getItem('blueFilterEnabled') === 'true';
    
    // Créer l'élément de style pour le filtre bleu s'il n'existe pas déjà
    let blueFilterStyle = document.getElementById('blue-filter-style');
    if (!blueFilterStyle) {
        blueFilterStyle = document.createElement('style');
        blueFilterStyle.id = 'blue-filter-style';
        document.head.appendChild(blueFilterStyle);
    }
    
    // Fonction pour appliquer ou supprimer le filtre bleu
    const toggleBlueFilter = (enable) => {
        if (enable) {
            // CSS pour le filtre bleu - réduit la lumière bleue
            blueFilterStyle.textContent = `
                html {
                    filter: sepia(20%) brightness(90%) hue-rotate(180deg) !important;
                }
            `;
            blueFilterToggle.textContent = 'Désactiver le filtre bleu';
            blueFilterToggle.setAttribute('aria-pressed', 'true');
            document.documentElement.classList.add('blue-filter-enabled');
        } else {
            blueFilterStyle.textContent = '';
            blueFilterToggle.textContent = 'Activer le filtre bleu';
            blueFilterToggle.setAttribute('aria-pressed', 'false');
            document.documentElement.classList.remove('blue-filter-enabled');
        }
        
        // Sauvegarder la préférence utilisateur
        localStorage.setItem('blueFilterEnabled', enable);
    };
    
    // Initialiser l'état du filtre bleu
    toggleBlueFilter(isBlueFilterEnabled);
    
    // Ajouter l'écouteur d'événement pour le bouton de filtre bleu
    blueFilterToggle.addEventListener('click', function() {
        const isCurrentlyEnabled = blueFilterToggle.getAttribute('aria-pressed') === 'true';
        toggleBlueFilter(!isCurrentlyEnabled);
    });
    
    // Ajouter la réinitialisation du filtre bleu au bouton de réinitialisation global
    if (resetAllButton) {
        resetAllButton.addEventListener('click', function() {
            toggleBlueFilter(false);
        });
    }
    
    // Filtre bleu initialisé
}

/**
 * Initialise le mode nuit en utilisant les classes de Tailwind CSS 4
 * Améliore l'accessibilité pour les utilisateurs sensibles à la luminosité
 */
function initDarkMode() {
    const darkModeToggle = document.getElementById('dark-mode-toggle');
    const resetAllButton = document.getElementById('accessibility-reset-all');
    const htmlElement = document.documentElement;
    
    if (!darkModeToggle) return;
    
    // Vérifier si le mode nuit était activé précédemment
    const isDarkModeEnabled = localStorage.getItem('darkModeEnabled') === 'true';
    
    // Fonction pour activer ou désactiver le mode nuit
    const toggleDarkMode = (enable) => {
        if (enable) {
            htmlElement.classList.add('dark');
            darkModeToggle.textContent = 'Désactiver le mode nuit';
            darkModeToggle.setAttribute('aria-pressed', 'true');
        } else {
            htmlElement.classList.remove('dark');
            darkModeToggle.textContent = 'Activer le mode nuit';
            darkModeToggle.setAttribute('aria-pressed', 'false');
        }
        
        // Sauvegarder la préférence utilisateur
        localStorage.setItem('darkModeEnabled', enable);
    };
    
    // Initialiser l'état du mode nuit
    toggleDarkMode(isDarkModeEnabled);
    
    // Ajouter l'écouteur d'événement pour le bouton de mode nuit
    darkModeToggle.addEventListener('click', function() {
        const isCurrentlyEnabled = darkModeToggle.getAttribute('aria-pressed') === 'true';
        toggleDarkMode(!isCurrentlyEnabled);
    });
    
    // Ajouter la réinitialisation du mode nuit au bouton de réinitialisation global
    if (resetAllButton) {
        resetAllButton.addEventListener('click', function() {
            toggleDarkMode(false);
        });
    }
    
    // Mode nuit initialisé
}

/**
 * Fonction utilitaire pour vérifier si un élément a une classe spécifique
 */
function hasClass(element, className) {
    return element.classList.contains(className);
}
