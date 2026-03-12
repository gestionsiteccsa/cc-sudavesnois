// Test de debug pour vérifier que le menu fonctionne
console.log('=== DEBUG MENU ===');

// Vérifier si les boutons sont trouvés
const buttons = document.querySelectorAll('button[aria-haspopup]');
console.log('Nombre de boutons aria-haspopup trouvés:', buttons.length);

buttons.forEach((btn, index) => {
    console.log(`Bouton ${index}:`, btn.textContent.trim(), '- aria-controls:', btn.getAttribute('aria-controls'));
});

// Vérifier si les sous-menus existent
buttons.forEach(btn => {
    const submenuId = btn.getAttribute('aria-controls');
    const submenu = document.getElementById(submenuId);
    console.log(`Sous-menu ${submenuId}:`, submenu ? 'TROUVÉ' : 'NON TROUVÉ');
});

console.log('==================');
