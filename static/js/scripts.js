// Scripts pour la Communauté de Communes du Sud Avesnois

document.addEventListener('DOMContentLoaded', function() {    
    // Navigation principale
    initMainNavigation();
    
    // Navigation mobile
    initMobileMenu();
    
    // Bouton retour en haut
    initBackToTopButton();
    
    // Animations au défilement
    initScrollAnimations();
    
    // Fonctionnalités d'accessibilité
    initAccessibilityFeatures();
    
    // // Formulaire de contact
    // initContactForm();
    
    // Formulaire de recherche
    initSearchForm();
});

// Navigation principale
function initMainNavigation() {
    const navButtons = document.querySelectorAll('.nav-dropdown > button');

    function checkSubmenuPosition() {
        const submenus = document.querySelectorAll('.submenu-level-2');
        submenus.forEach(submenu => {
            const rect = submenu.getBoundingClientRect();
            if (rect.right > window.innerWidth) {
                submenu.classList.add('submenu-right');
            } else {
                submenu.classList.remove('submenu-right');
            }
        });
    }

    // Fermer tous les sous-menus
    function closeAllSubmenus() {
        const allButtons = document.querySelectorAll('button[aria-haspopup="true"]');
        allButtons.forEach(button => {
            const submenuId = button.getAttribute('aria-controls');
            const submenu = document.getElementById(submenuId);
            if (submenu) {
                button.setAttribute('aria-expanded', 'false');
                submenu.setAttribute('aria-hidden', 'true');
                submenu.classList.add('hidden');
                submenu.classList.remove('submenu-visible');
                submenu.classList.add('opacity-0');
                submenu.classList.remove('opacity-100');
            }
        });
    }

    // Vérifier la position des sous-menus au redimensionnement de la fenêtre
    window.addEventListener('resize', checkSubmenuPosition);

    // Initialiser tous les boutons de navigation (y compris les sous-menus)
    const allNavButtons = document.querySelectorAll('button[aria-haspopup="true"]');
    allNavButtons.forEach(button => {
        const submenuId = button.getAttribute('aria-controls');
        const submenu = document.getElementById(submenuId);

        if (!submenu) return;

        // Gestionnaire de clic sur le bouton
        button.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();

            const isExpanded = button.getAttribute('aria-expanded') === 'true';

            // Si c'est un sous-menu de niveau 2, ne pas fermer le parent
            const isLevel2 = button.closest('.submenu-level-1') !== null;
            
            if (!isLevel2) {
                // Fermer tous les autres sous-menus de niveau 1
                navButtons.forEach(otherButton => {
                    if (otherButton !== button) {
                        const otherSubmenuId = otherButton.getAttribute('aria-controls');
                        const otherSubmenu = document.getElementById(otherSubmenuId);
                        if (otherSubmenu) {
                            otherButton.setAttribute('aria-expanded', 'false');
                            otherSubmenu.setAttribute('aria-hidden', 'true');
                            otherSubmenu.classList.add('hidden');
                            otherSubmenu.classList.remove('submenu-visible');
                            otherSubmenu.classList.add('opacity-0');
                            otherSubmenu.classList.remove('opacity-100');
                        }
                    }
                });
            } else {
                // Pour les sous-menus de niveau 2, fermer les autres sous-menus de niveau 2 dans le même parent
                const parentSubmenu = button.closest('.submenu-level-1');
                const siblingButtons = parentSubmenu.querySelectorAll('button[aria-haspopup="true"]');
                siblingButtons.forEach(siblingButton => {
                    if (siblingButton !== button) {
                        const siblingSubmenuId = siblingButton.getAttribute('aria-controls');
                        const siblingSubmenu = document.getElementById(siblingSubmenuId);
                        if (siblingSubmenu) {
                            siblingButton.setAttribute('aria-expanded', 'false');
                            siblingSubmenu.setAttribute('aria-hidden', 'true');
                            siblingSubmenu.classList.add('hidden');
                            siblingSubmenu.classList.remove('submenu-visible');
                            siblingSubmenu.classList.add('opacity-0');
                            siblingSubmenu.classList.remove('opacity-100');
                        }
                    }
                });
            }

            // Basculer l'état du sous-menu actuel
            button.setAttribute('aria-expanded', !isExpanded);
            submenu.setAttribute('aria-hidden', isExpanded);
            
            if (isExpanded) {
                submenu.classList.add('hidden');
                submenu.classList.remove('submenu-visible');
                submenu.classList.add('opacity-0');
                submenu.classList.remove('opacity-100');
            } else {
                submenu.classList.remove('hidden');
                submenu.classList.add('submenu-visible');
                submenu.classList.remove('opacity-0');
                submenu.classList.add('opacity-100');
                checkSubmenuPosition();
            }
        });

        // Gestion du clavier
        button.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                button.click();
            } else if (e.key === 'Escape') {
                button.setAttribute('aria-expanded', 'false');
                submenu.setAttribute('aria-hidden', 'true');
                submenu.classList.add('hidden');
                submenu.classList.remove('submenu-visible');
                submenu.classList.add('opacity-0');
                submenu.classList.remove('opacity-100');
                button.focus();
            } else if (e.key === 'ArrowDown' && button.getAttribute('aria-expanded') === 'true') {
                e.preventDefault();
                const firstLink = submenu.querySelector('a, button');
                if (firstLink) firstLink.focus();
            }
        });

        // Gestion du clavier dans le sous-menu
        submenu.addEventListener('keydown', (e) => {
            const focusableElements = submenu.querySelectorAll('a, button');
            const firstFocusable = focusableElements[0];
            const lastFocusable = focusableElements[focusableElements.length - 1];

            if (e.key === 'ArrowUp' && document.activeElement === firstFocusable) {
                e.preventDefault();
                button.focus();
            } else if (e.key === 'Escape') {
                e.preventDefault();
                button.setAttribute('aria-expanded', 'false');
                submenu.setAttribute('aria-hidden', 'true');
                submenu.classList.add('hidden');
                submenu.classList.remove('submenu-visible');
                submenu.classList.add('opacity-0');
                submenu.classList.remove('opacity-100');
                button.focus();
            }
        });
    });

    // Fermer les sous-menus lorsqu'on clique en dehors
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.nav-dropdown')) {
            closeAllSubmenus();
        }
    });
}

// Navigation mobile
function initMobileMenu() {
    const menuToggle = document.getElementById('menu-toggle');
    const mobileMenu = document.getElementById('mobile-menu');
    const menuIconOpen = document.getElementById('menu-icon-open');
    const menuIconClose = document.getElementById('menu-icon-close');
    
    if (menuToggle && mobileMenu) {
        menuToggle.addEventListener('click', function() {
            mobileMenu.classList.toggle('hidden');
            menuIconOpen.classList.toggle('hidden');
            menuIconClose.classList.toggle('hidden');
            
            const isExpanded = menuToggle.getAttribute('aria-expanded') === 'true';
            menuToggle.setAttribute('aria-expanded', !isExpanded);
        });
    }
    
    // Gestion des sous-menus dans le menu mobile
    const mobileSubmenuButtons = document.querySelectorAll('#mobile-menu button[aria-controls]');
    
    mobileSubmenuButtons.forEach(button => {
        button.addEventListener('click', function() {
            const targetId = this.getAttribute('aria-controls');
            const targetMenu = document.getElementById(targetId);
            const isExpanded = this.getAttribute('aria-expanded') === 'true';
            
            // Fermer tous les sous-menus du même niveau
            const parentUl = this.closest('ul');
            const siblingButtons = parentUl.querySelectorAll('button[aria-controls]');
            
            siblingButtons.forEach(siblingButton => {
                if (siblingButton !== this) {
                    const siblingTargetId = siblingButton.getAttribute('aria-controls');
                    const siblingMenu = document.getElementById(siblingTargetId);
                    
                    if (siblingMenu && !siblingMenu.classList.contains('hidden')) {
                        siblingMenu.classList.add('hidden');
                        siblingButton.setAttribute('aria-expanded', 'false');
                        siblingButton.querySelector('svg').classList.remove('rotate-180');
                    }
                }
            });
            
            // Ouvrir/fermer le sous-menu actuel
            if (targetMenu) {
                targetMenu.classList.toggle('hidden');
                this.setAttribute('aria-expanded', !isExpanded);
                this.querySelector('svg').classList.toggle('rotate-180');
            }
        });
    });
    
    // Fermer le menu mobile lors d'un clic à l'extérieur
    document.addEventListener('click', function(event) {
        if (mobileMenu && !mobileMenu.classList.contains('hidden') && 
            !mobileMenu.contains(event.target) && 
            !menuToggle.contains(event.target)) {
            mobileMenu.classList.add('hidden');
            menuIconOpen.classList.remove('hidden');
            menuIconClose.classList.add('hidden');
            menuToggle.setAttribute('aria-expanded', 'false');
        }
    });
}

// Bouton retour en haut
function initBackToTopButton() {
    const backToTopButton = document.getElementById('back-to-top');
    
    if (backToTopButton) {
        window.addEventListener('scroll', function() {
            if (window.pageYOffset > 300) {
                backToTopButton.classList.remove('opacity-0', 'invisible');
                backToTopButton.classList.add('opacity-100', 'visible');
            } else {
                backToTopButton.classList.remove('opacity-100', 'visible');
                backToTopButton.classList.add('opacity-0', 'invisible');
            }
        });
        
        backToTopButton.addEventListener('click', function() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }
}

// Animations au défilement
function initScrollAnimations() {
    // Animation pour les éléments avec la classe animate-on-scroll
    const animatedElements = document.querySelectorAll('.animate-on-scroll');
    
    if (animatedElements.length > 0) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-active');
                }
            });
        }, { threshold: 0.1 });
        
        animatedElements.forEach(element => {
            observer.observe(element);
        });
    }
    
    // Animation pour les éléments avec la classe reveal (ancien système)
    const revealElements = document.querySelectorAll('.reveal');
    
    if (revealElements.length > 0) {
        const revealObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('active');
                }
            });
        }, { threshold: 0.1 });
        
        revealElements.forEach(element => {
            revealObserver.observe(element);
        });
    }
}

// Fonctionnalités d'accessibilité
function initAccessibilityFeatures() {
    // Menu d'accessibilité
    const accessibilityButton = document.getElementById('accessibility-button');
    const accessibilityMenu = document.getElementById('accessibility-menu');
    
    if (accessibilityButton && accessibilityMenu) {
        accessibilityButton.addEventListener('click', function() {
            const isExpanded = accessibilityButton.getAttribute('aria-expanded') === 'true';
            toggleAccessibilityMenu(!isExpanded);
        });
        
        // Gestion des événements au clavier
        accessibilityButton.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                const isExpanded = accessibilityButton.getAttribute('aria-expanded') === 'true';
                toggleAccessibilityMenu(!isExpanded);
            }
        });
        
        // Fermer le menu si on clique ailleurs
        document.addEventListener('click', function(event) {
            if (!accessibilityButton.contains(event.target) && !accessibilityMenu.contains(event.target)) {
                toggleAccessibilityMenu(false);
            }
        });
        
        // Fermer le menu avec Escape
        accessibilityMenu.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                toggleAccessibilityMenu(false);
                accessibilityButton.focus();
            }
        });
        
        // Fonction pour ouvrir/fermer le menu
        function toggleAccessibilityMenu(open) {
            accessibilityButton.setAttribute('aria-expanded', open);
            accessibilityMenu.setAttribute('aria-hidden', !open);
            
            if (open) {
                accessibilityMenu.classList.remove('hidden');
            } else {
                accessibilityMenu.classList.add('hidden');
            }
        }
    }
    
    // Contraste élevé
    const contrastToggle = document.getElementById('contrast-toggle');
    const contrastReset = document.getElementById('contrast-reset');
    
    if (contrastToggle) {
        contrastToggle.addEventListener('click', function() {
            document.body.classList.toggle('high-contrast');
            const isHighContrast = document.body.classList.contains('high-contrast');
            localStorage.setItem('high-contrast', isHighContrast);
            contrastToggle.setAttribute('aria-pressed', isHighContrast);
            
            // Mettre à jour l'apparence du bouton
            if (isHighContrast) {
                contrastToggle.classList.add('bg-primary', 'text-white');
                contrastToggle.classList.remove('border-gray-300', 'hover:bg-gray-100');
            } else {
                contrastToggle.classList.remove('bg-primary', 'text-white');
                contrastToggle.classList.add('border-gray-300', 'hover:bg-gray-100');
            }
        });
        
        // Restaurer le paramètre de contraste
        const savedContrast = localStorage.getItem('high-contrast');
        if (savedContrast === 'true') {
            document.body.classList.add('high-contrast');
            contrastToggle.setAttribute('aria-pressed', 'true');
            contrastToggle.classList.add('bg-primary', 'text-white');
            contrastToggle.classList.remove('border-gray-300', 'hover:bg-gray-100');
        }
    }
    
    if (contrastReset) {
        contrastReset.addEventListener('click', function() {
            document.body.classList.remove('high-contrast');
            localStorage.removeItem('high-contrast');
            contrastToggle.setAttribute('aria-pressed', 'false');
            contrastToggle.classList.remove('bg-primary', 'text-white');
            contrastToggle.classList.add('border-gray-300', 'hover:bg-gray-100');
        });
    }
    
    // Taille de police
    const fontSizeIncrease = document.getElementById('font-size-increase');
    const fontSizeDecrease = document.getElementById('font-size-decrease');
    const fontSizeReset = document.getElementById('font-size-reset');
    
    let currentFontSize = 100;
    
    if (fontSizeIncrease) {
        fontSizeIncrease.addEventListener('click', function() {
            if (currentFontSize < 150) {
                currentFontSize += 10;
                updateFontSize();
            }
        });
    }
    
    if (fontSizeDecrease) {
        fontSizeDecrease.addEventListener('click', function() {
            if (currentFontSize > 70) {
                currentFontSize -= 10;
                updateFontSize();
            }
        });
    }
    
    if (fontSizeReset) {
        fontSizeReset.addEventListener('click', function() {
            currentFontSize = 100;
            updateFontSize();
        });
    }
    
    function updateFontSize() {
        document.documentElement.style.fontSize = `${currentFontSize}%`;
        localStorage.setItem('font-size', currentFontSize);
    }
    
    // Restaurer la taille de police
    const savedFontSize = localStorage.getItem('font-size');
    if (savedFontSize) {
        currentFontSize = parseInt(savedFontSize);
        updateFontSize();
    }
    
    // Interlignage
    const lineHeightToggle = document.getElementById('line-height-toggle');
    const lineHeightReset = document.getElementById('line-height-reset');
    
    if (lineHeightToggle) {
        lineHeightToggle.addEventListener('click', function() {
            document.body.classList.toggle('increased-line-height');
            const isIncreasedLineHeight = document.body.classList.contains('increased-line-height');
            localStorage.setItem('increased-line-height', isIncreasedLineHeight);
            lineHeightToggle.setAttribute('aria-pressed', isIncreasedLineHeight);
            
            // Mettre à jour l'apparence du bouton
            if (isIncreasedLineHeight) {
                lineHeightToggle.classList.add('bg-primary', 'text-white');
                lineHeightToggle.classList.remove('border-gray-300', 'hover:bg-gray-100');
            } else {
                lineHeightToggle.classList.remove('bg-primary', 'text-white');
                lineHeightToggle.classList.add('border-gray-300', 'hover:bg-gray-100');
            }
        });
        
        // Restaurer le paramètre d'interlignage
        const savedLineHeight = localStorage.getItem('increased-line-height');
        if (savedLineHeight === 'true') {
            document.body.classList.add('increased-line-height');
            lineHeightToggle.setAttribute('aria-pressed', 'true');
            lineHeightToggle.classList.add('bg-primary', 'text-white');
            lineHeightToggle.classList.remove('border-gray-300', 'hover:bg-gray-100');
        }
    }
    
    if (lineHeightReset) {
        lineHeightReset.addEventListener('click', function() {
            document.body.classList.remove('increased-line-height');
            localStorage.removeItem('increased-line-height');
            lineHeightToggle.setAttribute('aria-pressed', 'false');
            lineHeightToggle.classList.remove('bg-primary', 'text-white');
            lineHeightToggle.classList.add('border-gray-300', 'hover:bg-gray-100');
        });
    }
    
    // Espacement des caractères
    const letterSpacingToggle = document.getElementById('letter-spacing-toggle');
    const letterSpacingReset = document.getElementById('letter-spacing-reset');
    
    if (letterSpacingToggle) {
        letterSpacingToggle.addEventListener('click', function() {
            document.body.classList.toggle('increased-letter-spacing');
            const isIncreasedLetterSpacing = document.body.classList.contains('increased-letter-spacing');
            localStorage.setItem('increased-letter-spacing', isIncreasedLetterSpacing);
            letterSpacingToggle.setAttribute('aria-pressed', isIncreasedLetterSpacing);
            
            // Mettre à jour l'apparence du bouton
            if (isIncreasedLetterSpacing) {
                letterSpacingToggle.classList.add('bg-primary', 'text-white');
                letterSpacingToggle.classList.remove('border-gray-300', 'hover:bg-gray-100');
            } else {
                letterSpacingToggle.classList.remove('bg-primary', 'text-white');
                letterSpacingToggle.classList.add('border-gray-300', 'hover:bg-gray-100');
            }
        });
        
        // Restaurer le paramètre d'espacement
        const savedLetterSpacing = localStorage.getItem('increased-letter-spacing');
        if (savedLetterSpacing === 'true') {
            document.body.classList.add('increased-letter-spacing');
            letterSpacingToggle.setAttribute('aria-pressed', 'true');
            letterSpacingToggle.classList.add('bg-primary', 'text-white');
            letterSpacingToggle.classList.remove('border-gray-300', 'hover:bg-gray-100');
        }
    }
    
    if (letterSpacingReset) {
        letterSpacingReset.addEventListener('click', function() {
            document.body.classList.remove('increased-letter-spacing');
            localStorage.removeItem('increased-letter-spacing');
            letterSpacingToggle.setAttribute('aria-pressed', 'false');
            letterSpacingToggle.classList.remove('bg-primary', 'text-white');
            letterSpacingToggle.classList.add('border-gray-300', 'hover:bg-gray-100');
        });
    }
    
    // Réinitialiser tous les paramètres
    const resetAllButton = document.getElementById('accessibility-reset-all');
    
    if (resetAllButton) {
        resetAllButton.addEventListener('click', function() {
            // Réinitialiser le contraste
            document.body.classList.remove('high-contrast');
            localStorage.removeItem('high-contrast');
            if (contrastToggle) {
                contrastToggle.setAttribute('aria-pressed', 'false');
                contrastToggle.classList.remove('bg-primary', 'text-white');
                contrastToggle.classList.add('border-gray-300', 'hover:bg-gray-100');
            }
            
            // Réinitialiser la taille de police
            currentFontSize = 100;
            document.documentElement.style.fontSize = '100%';
            localStorage.removeItem('font-size');
            
            // Réinitialiser l'interlignage
            document.body.classList.remove('increased-line-height');
            localStorage.removeItem('increased-line-height');
            if (lineHeightToggle) {
                lineHeightToggle.setAttribute('aria-pressed', 'false');
                lineHeightToggle.classList.remove('bg-primary', 'text-white');
                lineHeightToggle.classList.add('border-gray-300', 'hover:bg-gray-100');
            }
            
            // Réinitialiser l'espacement des caractères
            document.body.classList.remove('increased-letter-spacing');
            localStorage.removeItem('increased-letter-spacing');
            if (letterSpacingToggle) {
                letterSpacingToggle.setAttribute('aria-pressed', 'false');
                letterSpacingToggle.classList.remove('bg-primary', 'text-white');
                letterSpacingToggle.classList.add('border-gray-300', 'hover:bg-gray-100');
            }
            
            // Afficher un message de confirmation
            alert('Tous les paramètres d\'accessibilité ont été réinitialisés.');
        });
    }
}

// Formulaire de contact
// function initContactForm() {
//     const contactForm = document.querySelector('#contact form');
//     const formFeedback = document.getElementById('form-feedback');
    
//     if (contactForm) {
//         // Validation des champs en temps réel
//         const formFields = contactForm.querySelectorAll('input, textarea');
//         formFields.forEach(field => {
//             field.addEventListener('blur', function() {
//                 validateField(field);
//             });
            
//             field.addEventListener('input', function() {
//                 // Réinitialiser les erreurs lors de la saisie
//                 if (field.getAttribute('aria-invalid') === 'true') {
//                     resetFieldError(field);
//                 }
//             });
//         });
        
//         contactForm.addEventListener('submit', function(e) {
//             e.preventDefault();
            
//             // Validation de tous les champs
//             let isValid = true;
//             formFields.forEach(field => {
//                 if (field.hasAttribute('required') || field.value.trim() !== '') {
//                     const fieldIsValid = validateField(field);
//                     isValid = isValid && fieldIsValid;
//                 }
//             });
            
//             if (!isValid) {
//                 showFormMessage('Veuillez corriger les erreurs dans le formulaire.', 'error');
//                 // Focus sur le premier champ en erreur
//                 const firstInvalidField = contactForm.querySelector('[aria-invalid="true"]');
//                 if (firstInvalidField) {
//                     firstInvalidField.focus();
//                 }
//                 return;
//             }
            
//             // Récupération des valeurs du formulaire
//             const formData = {
//                 nom: document.getElementById('nom').value,
//                 prenom: document.getElementById('prenom').value,
//                 email: document.getElementById('email').value,
//                 telephone: document.getElementById('telephone').value,
//                 message: document.getElementById('message').value,
//                 rgpd: document.getElementById('rgpd').checked
//             };
            
//             // Simulation d'envoi (à remplacer par un vrai envoi AJAX)
//             // Dans un environnement Django, vous utiliseriez un token CSRF et une requête fetch
//             console.log('Formulaire soumis avec succès', formData);
            
//             // Réinitialisation du formulaire et des états d'erreur
//             contactForm.reset();
//             formFields.forEach(field => {
//                 resetFieldError(field);
//             });
            
//             // Affichage d'un message de succès
//             showFormMessage('Votre message a été envoyé avec succès. Nous vous répondrons dans les plus brefs délais.', 'success');
//         });
//     }
// }

// Validation d'un champ individuel
function validateField(field) {
    const fieldId = field.id;
    const errorElement = document.getElementById(`${fieldId}-error`);
    
    // Réinitialiser l'état précédent
    resetFieldError(field);
    
    // Vérifier si le champ est valide
    let isValid = true;
    let errorMessage = '';
    
    // Validation spécifique selon le type de champ
    if (field.hasAttribute('required') && field.value.trim() === '') {
        isValid = false;
        errorMessage = 'Ce champ est obligatoire';
    } else if (field.type === 'email' && field.value.trim() !== '') {
        // Validation simple d'email
        const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailPattern.test(field.value)) {
            isValid = false;
            errorMessage = 'Veuillez entrer une adresse email valide';
        }
    } else if (field.type === 'tel' && field.value.trim() !== '') {
        // Validation simple de téléphone français
        const telPattern = /^(?:(?:\+|00)33|0)\s*[1-9](?:[\s.-]*\d{2}){4}$/;
        if (!telPattern.test(field.value)) {
            isValid = false;
            errorMessage = 'Veuillez entrer un numéro de téléphone valide';
        }
    } else if (field.type === 'checkbox' && field.hasAttribute('required') && !field.checked) {
        isValid = false;
        errorMessage = 'Vous devez accepter cette condition';
    }
    
    // Mettre à jour l'état du champ et afficher l'erreur si nécessaire
    if (!isValid) {
        field.setAttribute('aria-invalid', 'true');
        if (errorElement) {
            errorElement.textContent = errorMessage;
            errorElement.classList.remove('hidden');
        }
    }
    
    return isValid;
}

// Réinitialiser l'état d'erreur d'un champ
function resetFieldError(field) {
    const fieldId = field.id;
    const errorElement = document.getElementById(`${fieldId}-error`);
    
    field.setAttribute('aria-invalid', 'false');
    if (errorElement) {
        errorElement.textContent = '';
        errorElement.classList.add('hidden');
    }
}

// Afficher un message global pour le formulaire
function showFormMessage(message, type) {
    // Créer ou réutiliser l'élément de message
    const formFeedback = document.getElementById('form-feedback');
    
    // Configurer le message
    formFeedback.className = `p-4 rounded-md mb-6 ${type === 'error' ? 'bg-red-600' : 'bg-green-600'}`;
    formFeedback.textContent = message;
    formFeedback.classList.remove('hidden');
    
    // Disparition automatique après 5 secondes pour les messages de succès
    if (type === 'success') {
        setTimeout(() => {
            formFeedback.classList.add('opacity-0');
            setTimeout(() => {
                formFeedback.classList.add('hidden');
                formFeedback.classList.remove('opacity-0');
            }, 300);
        }, 5000);
    }
}

// Formulaire de recherche
function initSearchForm() {
    const searchToggle = document.getElementById('search-toggle');
    const searchForm = document.getElementById('search-form');
    const searchInput = document.getElementById('search-input');
    
    if (searchToggle && searchForm && searchInput) {
        // Ouvrir/fermer le formulaire de recherche
        searchToggle.addEventListener('click', function() {
            const isExpanded = searchToggle.getAttribute('aria-expanded') === 'true';
            toggleSearchForm(!isExpanded);
        });
        
        // Gestion des événements au clavier
        searchToggle.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                const isExpanded = searchToggle.getAttribute('aria-expanded') === 'true';
                toggleSearchForm(!isExpanded);
                
                if (!isExpanded) {
                    // Donner le focus au champ de recherche après ouverture
                    setTimeout(() => {
                        searchInput.focus();
                    }, 100);
                }
            }
        });
        
        // Fermer le formulaire avec Escape
        searchInput.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                e.preventDefault();
                toggleSearchForm(false);
                searchToggle.focus();
            }
        });
        
        // Fermer le formulaire si on clique ailleurs
        document.addEventListener('click', function(event) {
            if (!searchToggle.contains(event.target) && !searchForm.contains(event.target)) {
                toggleSearchForm(false);
            }
        });
        
        // Fonction pour ouvrir/fermer le formulaire
        function toggleSearchForm(open) {
            searchToggle.setAttribute('aria-expanded', open);
            searchForm.setAttribute('aria-hidden', !open);
            
            if (open) {
                searchForm.classList.remove('hidden');
            } else {
                searchForm.classList.add('hidden');
            }
        }
    }
}
