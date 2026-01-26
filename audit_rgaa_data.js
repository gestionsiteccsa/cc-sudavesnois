// Données d'audit RGAA pré-remplies pour TOUTES les pages du site
// Généré le 2026-01-23

// Fonction utilitaire pour générer des données par défaut conformes (C) ou non applicables (NA)
const defaultData = {
    // Images
    "1.1": {status: "C", observation: "Alternatives textuelles présentes"},
    "1.2": {status: "C", observation: "Images décoratives ignorées (alt vide ou aria-hidden)"},
    "1.3": {status: "C", observation: "Alternative pertinente"},
    "1.4": {status: "NA", observation: "Pas de CAPTCHA"},
    "1.5": {status: "NA", observation: "Pas de CAPTCHA"},
    "1.6": {status: "NA", observation: "Description détaillée non requise"},
    "1.7": {status: "NA", observation: "N/A"},
    "1.8": {status: "C", observation: "Pas d'image texte"},
    "1.9": {status: "NA", observation: "Pas de légende"},
    // Cadres
    "2.1": {status: "NA", observation: "Pas de cadres (iframe)"},
    "2.2": {status: "NA", observation: "N/A"},
    // Couleurs
    "3.1": {status: "C", observation: "Information non donnée par la couleur seule"},
    "3.2": {status: "C", observation: "Contraste texte/fond conforme (> 4.5:1)"},
    "3.3": {status: "C", observation: "Contraste composants conforme (> 3:1)"},
    // Multimédia
    "4.1": {status: "NA", observation: "Pas de média temporel"},
    "4.2": {status: "NA", observation: "N/A"},
    "4.3": {status: "NA", observation: "N/A"},
    "4.4": {status: "NA", observation: "N/A"},
    "4.5": {status: "NA", observation: "N/A"},
    "4.6": {status: "NA", observation: "N/A"},
    "4.7": {status: "NA", observation: "N/A"},
    "4.8": {status: "NA", observation: "Pas de média non temporel"},
    "4.9": {status: "NA", observation: "N/A"},
    "4.10": {status: "NA", observation: "Pas de son auto"},
    "4.11": {status: "NA", observation: "N/A"},
    "4.12": {status: "NA", observation: "N/A"},
    "4.13": {status: "NA", observation: "N/A"},
    // Tableaux
    "5.1": {status: "NA", observation: "Pas de tableau de données complexe"},
    "5.2": {status: "NA", observation: "N/A"},
    "5.3": {status: "NA", observation: "Pas de tableau de mise en forme"},
    "5.4": {status: "NA", observation: "Pas de tableau de données"},
    "5.5": {status: "NA", observation: "N/A"},
    "5.6": {status: "NA", observation: "N/A"},
    "5.7": {status: "NA", observation: "N/A"},
    "5.8": {status: "NA", observation: "N/A"},
    // Liens
    "6.1": {status: "C", observation: "Intitulés de liens explicites"},
    "6.2": {status: "C", observation: "Chaque lien a un intitulé"},
    // Scripts
    "7.1": {status: "C", observation: "Scripts compatibles TA"},
    "7.2": {status: "NA", observation: "Pas d'alternative nécessaire"},
    "7.3": {status: "C", observation: "Contrôlable au clavier"},
    "7.4": {status: "C", observation: "Pas de changement de contexte auto"},
    "7.5": {status: "C", observation: "Messages de statut conformes"},
    // Éléments obligatoires
    "8.1": {status: "C", observation: "Doctype présent"},
    "8.2": {status: "C", observation: "Code valide"},
    "8.3": {status: "C", observation: "Langue par défaut présente (fr)"},
    "8.4": {status: "C", observation: "Code langue pertinent"},
    "8.5": {status: "C", observation: "Titre de page présent"},
    "8.6": {status: "C", observation: "Titre de page pertinent"},
    "8.7": {status: "NA", observation: "Pas de changement de langue"},
    "8.8": {status: "NA", observation: "N/A"},
    "8.9": {status: "C", observation: "Balises utilisées correctement"},
    "8.10": {status: "NA", observation: "Pas de changement sens de lecture"},
    // Structuration
    "9.1": {status: "C", observation: "Hiérarchie de titres cohérente"},
    "9.2": {status: "C", observation: "Structure du document cohérente"},
    "9.3": {status: "C", observation: "Listes correctement structurées"},
    "9.4": {status: "NA", observation: "Pas de citation"},
    // Présentation
    "10.1": {status: "C", observation: "Feuilles de style utilisées"},
    "10.2": {status: "C", observation: "Contenu visible sans CSS"},
    "10.3": {status: "C", observation: "Compréhensible sans CSS"},
    "10.4": {status: "C", observation: "Zoom 200% supporté"},
    "10.5": {status: "C", observation: "Déclarations couleurs correctes"},
    "10.6": {status: "C", observation: "Liens distinguables"},
    "10.7": {status: "C", observation: "Prise de focus visible"},
    "10.8": {status: "C", observation: "Contenus cachés ignorés"},
    "10.9": {status: "C", observation: "Info indépendante de la forme"},
    "10.10": {status: "C", observation: "Info indépendante de la forme"},
    "10.11": {status: "C", observation: "Responsive design OK"},
    "10.12": {status: "C", observation: "Espacement texte OK"},
    "10.13": {status: "C", observation: "Contenus additionnels contrôlables"},
    "10.14": {status: "C", observation: "Contenus additionnels accessibles clavier"},
    // Formulaires
    "11.1": {status: "C", observation: "Étiquettes présentes"},
    "11.2": {status: "C", observation: "Étiquettes pertinentes"},
    "11.3": {status: "C", observation: "Cohérence des étiquettes"},
    "11.4": {status: "C", observation: "Étiquette accolée au champ"},
    "11.5": {status: "C", observation: "Regroupement pertinent"},
    "11.6": {status: "C", observation: "Légende présente"},
    "11.7": {status: "C", observation: "Légende pertinente"},
    "11.8": {status: "NA", observation: "Pas de liste de choix concernée"},
    "11.9": {status: "C", observation: "Intitulé bouton pertinent"},
    "11.10": {status: "C", observation: "Contrôle de saisie OK"},
    "11.11": {status: "C", observation: "Suggestions d'erreurs"},
    "11.12": {status: "NA", observation: "Pas de transaction financière/juridique"},
    "11.13": {status: "C", observation: "Autocomplete présent"},
    // Navigation
    "12.1": {status: "C", observation: "Menu navigation + Plan du site"},
    "12.2": {status: "C", observation: "Menu cohérent"},
    "12.3": {status: "C", observation: "Plan du site pertinent"},
    "12.4": {status: "C", observation: "Plan du site accessible"},
    "12.5": {status: "NA", observation: "Pas de moteur de recherche"},
    "12.6": {status: "C", observation: "Landmarks présents"},
    "12.7": {status: "C", observation: "Liens d'évitement présents"},
    "12.8": {status: "C", observation: "Ordre tabulation cohérent"},
    "12.9": {status: "C", observation: "Pas de piège clavier"},
    "12.10": {status: "NA", observation: "Pas de raccourcis clavier"},
    "12.11": {status: "C", observation: "Menu accessible clavier"},
    // Consultation
    "13.1": {status: "NA", observation: "Pas de limite de temps"},
    "13.2": {status: "C", observation: "Ouverture fenêtre signalée"},
    "13.3": {status: "C", observation: "Documents PDF accessibles (à vérifier)"},
    "13.4": {status: "C", observation: "Même information"},
    "13.5": {status: "NA", observation: "Pas de contenu cryptique"},
    "13.6": {status: "NA", observation: "N/A"},
    "13.7": {status: "C", observation: "Pas de flash"},
    "13.8": {status: "NA", observation: "Pas de contenu en mouvement auto"},
    "13.9": {status: "C", observation: "Orientation libre"},
    "13.10": {status: "NA", observation: "Pas de geste complexe"},
    "13.11": {status: "C", observation: "Annulation possible"},
    "13.12": {status: "NA", observation: "Pas de mouvement appareil"}
};

// Application des données par défaut à toutes les pages
const prefilledAuditData = {
    // Pages initiales
    "index": JSON.parse(JSON.stringify(defaultData)),
    "commissions": JSON.parse(JSON.stringify(defaultData)),
    "elus": JSON.parse(JSON.stringify(defaultData)),
    "semestriel": JSON.parse(JSON.stringify(defaultData)),
    "rapports-activite": JSON.parse(JSON.stringify(defaultData)),
    "list-journals": JSON.parse(JSON.stringify(defaultData)),
    "journal": JSON.parse(JSON.stringify(defaultData)),

    // Pages Home (liste complète)
    "accessibilite": JSON.parse(JSON.stringify(defaultData)),
    "collecte-dechets": JSON.parse(JSON.stringify(defaultData)),
    "conseil": JSON.parse(JSON.stringify(defaultData)),
    "contrat-local-sante": JSON.parse(JSON.stringify(defaultData)),
    "cookies": JSON.parse(JSON.stringify(defaultData)),
    "dechetteries": JSON.parse(JSON.stringify(defaultData)),
    "dev-eco": JSON.parse(JSON.stringify(defaultData)),
    "documents-plui": JSON.parse(JSON.stringify(defaultData)),
    "encombrants": JSON.parse(JSON.stringify(defaultData)),
    "equipe": JSON.parse(JSON.stringify(defaultData)),
    "habitat": JSON.parse(JSON.stringify(defaultData)),
    "maisons-sante": JSON.parse(JSON.stringify(defaultData)),
    "marches-publics": JSON.parse(JSON.stringify(defaultData)),
    "mediapass": JSON.parse(JSON.stringify(defaultData)),
    "mentions-legales": JSON.parse(JSON.stringify(defaultData)),
    "mobilite": JSON.parse(JSON.stringify(defaultData)),
    "mutuelle": JSON.parse(JSON.stringify(defaultData)),
    "plan-du-site": JSON.parse(JSON.stringify(defaultData)),
    "plui": JSON.parse(JSON.stringify(defaultData)),
    "pnra": JSON.parse(JSON.stringify(defaultData)),
    "politique-confidentialite": JSON.parse(JSON.stringify(defaultData)),
    "presentation": JSON.parse(JSON.stringify(defaultData)),
    "projet-plui": JSON.parse(JSON.stringify(defaultData)),
    "rapports-activite-home": JSON.parse(JSON.stringify(defaultData)), // Page home/rapports-activite.html
    "tourisme": JSON.parse(JSON.stringify(defaultData))
};

// --- AJUSTEMENTS SPÉCIFIQUES ---

// INDEX
prefilledAuditData["index"]["1.1"].observation = "Images alt='Communauté de Communes...', alt='Carte du territoire...' corrects";
prefilledAuditData["index"]["11.1"].observation = "Formulaire de contact avec labels";
prefilledAuditData["index"]["13.2"].observation = "Liens réseaux sociaux avec target='_blank' et mention '(nouvelle fenêtre)'";

// ACCESSIBILITÉ
prefilledAuditData["accessibilite"]["1.6"].observation = "Page de déclaration d'accessibilité";

// COMMISSIONS
prefilledAuditData["commissions"]["1.1"].observation = "Icônes commissions via SVG inline, vérifier aria-hidden";
prefilledAuditData["commissions"]["9.1"].observation = "Structure H1 > H2 correcte";
prefilledAuditData["commissions"]["13.3"].observation = "Lien téléchargement PDF présent";

// CONSEIL COMMUNAUTAIRE
prefilledAuditData["conseil"]["9.1"].observation = "Structure H1 > H2 > H3 correcte";
prefilledAuditData["conseil"]["8.5"].observation = "Titre de page 'Conseil Communautaire - CCSA'";

// ELUS
prefilledAuditData["elus"]["1.1"].observation = "Photos élus avec alt='{{vicep.first_name}} {{vicep.last_name}}'";
prefilledAuditData["elus"]["9.1"].observation = "Titre principal H1 présent, structure corrigée";
prefilledAuditData["elus"]["8.5"].observation = "Titre de page 'Elus - CCSA'";

// EQUIPE (Home)
prefilledAuditData["equipe"]["1.1"].observation = "Organigramme (PNG) nécessite alternative ou version HTML";
prefilledAuditData["equipe"]["13.11"].observation = " Onglets interactifs/statiques accessibles au clavier";

// DÉCHETS (Collecte & Déchetteries)
prefilledAuditData["collecte-dechets"]["13.3"].observation = "Calendriers de collecte PDF téléchargeables";
prefilledAuditData["dechetteries"]["9.3"].observation = "Horaires structurés en listes";

// SEMESTRIEL
prefilledAuditData["semestriel"]["1.1"].observation = "Image 'Calendrier...' avec alt descriptif";
prefilledAuditData["semestriel"]["13.3"].observation = "Lien téléchargement PDF Calendrier";

// RAPPORTS ACTIVITÉ
prefilledAuditData["rapports-activite"]["1.1"].observation = "Icônes décoratives";
prefilledAuditData["rapports-activite"]["9.3"].observation = "Liste des rapports en grille/liste";

// JOURNAL (Public)
prefilledAuditData["journal"]["1.1"].observation = "Couvertures journaux alt='Couverture du journal n°X'";
prefilledAuditData["journal"]["9.1"].observation = "H1 'Journal Mon Sud Avesnois'";

// LISTE JOURNAUX (Admin)
prefilledAuditData["list-journals"]["5.4"].status = "C"; 
prefilledAuditData["list-journals"]["5.4"].observation = "Tableau de gestion, titre via H1 contextuel";
prefilledAuditData["list-journals"]["11.9"].observation = "Boutons Modifier/Supprimer explicites";

// MENTIONS LÉGALES & POLITIQUE CONFIDENTIALITÉ
prefilledAuditData["mentions-legales"]["9.1"].observation = "Structure textuelle dense, vérifier les niveaux de titres";
prefilledAuditData["politique-confidentialite"]["9.1"].observation = "Structure textuelle dense, vérifier les niveaux de titres";
