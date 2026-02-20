"""Données de collecte des déchets pour génération PDF."""

# Structure des données de collecte
city_data = {
    "Anor": {
        "ordures": "mercredi",
        "verre": {
            "jour": "mercredi",
            "dates": [
                "2026-01-07", "2026-02-04", "2026-03-04", "2026-04-08",
                "2026-05-06", "2026-06-03", "2026-07-08", "2026-08-05",
                "2026-09-09", "2026-10-07", "2026-11-04", "2026-12-09",
                "2027-01-06", "2027-02-03", "2027-03-03", "2027-04-07",
                "2027-05-05", "2027-06-09", "2027-07-07", "2027-08-04",
                "2027-09-08", "2027-10-06", "2027-11-03", "2027-12-08"
            ]
        }
    },
    "Baives": {
        "ordures": "lundi",
        "verre": {
            "jour": "lundi",
            "dates": [
                "2026-01-12", "2026-02-09", "2026-03-09", "2026-04-13",
                "2026-05-11", "2026-06-08", "2026-07-13", "2026-08-10",
                "2026-09-14", "2026-10-12", "2026-11-09", "2026-12-14",
                "2027-01-11", "2027-02-08", "2027-03-08", "2027-04-12",
                "2027-05-10", "2027-06-14", "2027-07-12", "2027-08-09",
                "2027-09-13", "2027-10-11", "2027-11-08", "2027-12-13"
            ]
        }
    },
    "Wallers-en-Fagne": {
        "ordures": "lundi",
        "verre": {
            "jour": "lundi",
            "dates": [
                "2026-01-12", "2026-02-09", "2026-03-09", "2026-04-13",
                "2026-05-11", "2026-06-08", "2026-07-13", "2026-08-10",
                "2026-09-14", "2026-10-12", "2026-11-09", "2026-12-14",
                "2027-01-11", "2027-02-08", "2027-03-08", "2027-04-12",
                "2027-05-10", "2027-06-14", "2027-07-12", "2027-08-09",
                "2027-09-13", "2027-10-11", "2027-11-08", "2027-12-13"
            ]
        }
    },
    "Moustier-en-Fagne": {
        "ordures": "lundi",
        "verre": {
            "jour": "lundi",
            "dates": [
                "2026-01-12", "2026-02-09", "2026-03-09", "2026-04-13",
                "2026-05-11", "2026-06-08", "2026-07-13", "2026-08-10",
                "2026-09-14", "2026-10-12", "2026-11-09", "2026-12-14",
                "2027-01-11", "2027-02-08", "2027-03-08", "2027-04-12",
                "2027-05-10", "2027-06-14", "2027-07-12", "2027-08-09",
                "2027-09-13", "2027-10-11", "2027-11-08", "2027-12-13"
            ]
        }
    },
    "Eppe-Sauvage": {
        "ordures": "lundi",
        "verre": {
            "jour": "lundi",
            "dates": [
                "2026-01-12", "2026-02-09", "2026-03-09", "2026-04-13",
                "2026-05-11", "2026-06-08", "2026-07-13", "2026-08-10",
                "2026-09-14", "2026-10-12", "2026-11-09", "2026-12-14",
                "2027-01-11", "2027-02-08", "2027-03-08", "2027-04-12",
                "2027-05-10", "2027-06-14", "2027-07-12", "2027-08-09",
                "2027-09-13", "2027-10-11", "2027-11-08", "2027-12-13"
            ]
        }
    },
    "Willies": {
        "ordures": "lundi",
        "verre": {
            "jour": "lundi",
            "dates": [
                "2026-01-12", "2026-02-09", "2026-03-09", "2026-04-13",
                "2026-05-11", "2026-06-08", "2026-07-13", "2026-08-10",
                "2026-09-14", "2026-10-12", "2026-11-09", "2026-12-14",
                "2027-01-11", "2027-02-08", "2027-03-08", "2027-04-12",
                "2027-05-10", "2027-06-14", "2027-07-12", "2027-08-09",
                "2027-09-13", "2027-10-11", "2027-11-08", "2027-12-13"
            ]
        }
    },
    "Féron": {
        "ordures": "jeudi",
        "verre": {
            "jeudi": [
                "2026-01-08", "2026-02-05", "2026-03-05", "2026-04-09",
                "2026-05-07", "2026-06-04", "2026-07-09", "2026-08-06",
                "2026-09-10", "2026-10-08", "2026-11-05", "2026-12-10",
                "2027-01-07", "2027-02-04", "2027-03-04", "2027-04-08",
                "2027-05-06", "2027-06-10", "2027-07-08", "2027-08-05",
                "2027-09-09", "2027-10-07", "2027-11-04", "2027-12-09"
            ]
        }
    },
    "Glageon": {
        "ordures": "mardi",
        "verre": {
            "jour": "mardi",
            "dates": [
                "2026-01-13", "2026-02-10", "2026-03-10", "2026-04-14",
                "2026-05-12", "2026-06-09", "2026-07-14", "2026-08-11",
                "2026-09-15", "2026-10-13", "2026-11-10", "2026-12-15",
                "2027-01-12", "2027-02-09", "2027-03-09", "2027-04-13",
                "2027-05-11", "2027-06-15", "2027-07-13", "2027-08-10",
                "2027-09-14", "2027-10-12", "2027-11-09", "2027-12-14"
            ]
        }
    },
    "Ohain": {
        "ordures": "jeudi",
        "verre": {
            "jour": "jeudi",
            "dates": [
                "2026-01-15", "2026-02-12", "2026-03-12", "2026-04-16",
                "2026-05-14", "2026-06-11", "2026-07-16", "2026-08-13",
                "2026-09-17", "2026-10-15", "2026-11-12", "2026-12-17",
                "2027-01-14", "2027-02-11", "2027-03-11", "2027-04-15",
                "2027-05-13", "2027-06-17", "2027-07-15", "2027-08-12",
                "2027-09-16", "2027-10-14", "2027-11-11", "2027-12-16"
            ]
        }
    },
    "Wignehies": {
        "ordures": "jeudi",
        "verre": {
            "jour": "jeudi",
            "dates": [
                "2026-01-08", "2026-02-05", "2026-03-05", "2026-04-09",
                "2026-05-07", "2026-06-04", "2026-07-09", "2026-08-06",
                "2026-09-10", "2026-10-08", "2026-11-05", "2026-12-10",
                "2027-01-07", "2027-02-04", "2027-03-04", "2027-04-08",
                "2027-05-06", "2027-06-10", "2027-07-08", "2027-08-05",
                "2027-09-09", "2027-10-07", "2027-11-04", "2027-12-09"
            ]
        }
    },
    "Fourmies": {
        "ordures": {
            "lundi": [
                "rue du 8 mai 1945", "rue aldred maton", "rue alphonse moreau",
                "square ampère", "rue anatole France", "impasse andré wannin",
                "rue andré wannin", "rue baligant", "residence bellevue",
                "chemin des blés", "rue du bois", "rue boris vian",
                "rue bouret", "avenue des bureaux", "rue des catelets",
                "rue des champs", "rue du chanoine thuliez", "rue des charbonniers",
                "rue charles petit", "rue du chauffour", "rue des cléments",
                "rue du conditionnement", "rue courtecuisse", "impasse curie",
                "rue curie", "rue danièle casanova", "rue delval",
                "impasse des écoles", "rue edouard verpraet", "rue de l'égalité",
                "rue des éliets", "rue de l'entrepot", "rue ernest thomas",
                "impasse des étangs", "rue des étangs", "impasse fauchart",
                "rue felix labourdette", "rue fernand pecheux", "impasse fossé des vœux",
                "rue gambetta", "rue de la gare", "rue du général gouttiére",
                "place georges coppeaux", "rue de grenoble", "rue guy môquet",
                "rue de l'hôpital", "rue des howis", "rue des jardins",
                "rue jean moulin", "rue jean baptiste lebas", "avenue joliot-curie",
                "impasse jules guesde", "rue jules guesdes", "résidence le clos sollier",
                "rue des lilas", "rue louis braille", "rue louise michel",
                "rue marcel ulrici", "impasse marchand", "impaase marcy",
                "rue marie-louise meyer", "rue marius eldert", "rue michel dubois",
                "rue ninite", "rue du nouveau monde", "cité nouvelle",
                "cité des oiseaux", "rue d'orient", "rue pasteur",
                "rue paul lafargue", "rue pilette", "résidence de la plaine à joncs",
                "rue de la plaine à joncs", "rue de la planchette",
                "avenue du président kennedy", "rue proisy", "rue raoul delvaux",
                "rue de la république", "rue de la république prolongée",
                "rue robespierre", "rue des rouets", "rue des rousseaux",
                "rue sencier", "rue thierry", "résidence des tilleuls",
                "rue sans pareille", "résidence de la vallée de l'helpe",
                "rue des verreries", "impasse verte"
            ],
            "mardi": [
                "Rue Alexandre Mulat", "place alfred derigny", "square allende",
                "Rue Alphonse Staincq", "rue antoine renaud", "avenue des astronautes",
                "rue d'avesnes", "rue basse du moulin", "rue de bernburg",
                "rue berthelot", "rue bleue", "rue branly", "rue de la brasserie",
                "place claude jourdain", "rue de la commune de paris", "rue de la concorde",
                "rue cousin corbier", "rue croizet-eliet", "impasse du défriché",
                "rue du défriché", "rue de douai", "quartier dury",
                "rue édouard flament", "rue de l'émaillerie", "rue émile zola",
                "rue de l'espérance", "residence de l'étang", "rue eugène paris",
                "rue faidherbe", "rue de la fontaine rouge", "rue françois delaplace",
                "rue de la fraternité", "rue gabriel zaya", "rue gaston torlet",
                "rue des glycines", "rue du gymnase", "rue des haies",
                "rue haute du moulin", "rue de l'helpe", "rue henri dunant",
                "rue de la houppe du bois", "rue jacques duclos", "impasse jean jaurès",
                "rue jean jaurès", "rue jean-pierre dupont", "rue jean pierre lenoble",
                "impasse jeanne d'arc", "rue de là-haut", "rue léo lagrange",
                "rue de la Liberté", "rue de lille", "rue du maire coppeaux",
                "cité droulers", "résidence le malakoff", "rue marceau batteux",
                "place maria blondeau", "avenue de la marliére", "rue de minonsars",
                "rue du moulin", "rue du nord", "rue de la paix",
                "impasse du paradis", "rue du paradis", "allée des renvideurs",
                "place de la republique", "avenue roger couderc", "boulevard sadi carnot",
                "rue serpentine", "rue théophile legrand", "rue traversiére",
                "rue des troenes", "rue de valenciennes", "rue du vallon",
                "place de verdun", "rue victor hugo", "rue xavier clavon"
            ],
            "mercredi": [
                "rue adolphe hugé", "rue d'anor", "rue de la cense",
                "rue de colnet", "rue du dachet", "rue du fief",
                "rue de la fontaine à l'tuerie", "rue des noires terres",
                "rue des pierres", "rue saint louis", "rue saint pierre",
                "rue saint pierre prolongée", "rue de la savonnerie",
                "rue du terne", "rue tranquille"
            ],
            "jeudi": [
                "residence bellevue", "rue de craonne", "quartier flament",
                "rue de la forge", "rue de fridley", "rue du général leclerc",
                "square jean mermoz", "rue de jeanne III", "rue de la lamberie",
                "rue du marais", "sqare saint exupery", "impasse du temple",
                "rue victor delloue", "Vieux Chemin de Wignehies",
                "Vieux Chemin de Fourmies"
            ]
        },
        "verre": {
            "lundi": [
                "2026-01-05", "2026-02-02", "2026-03-02", "2026-04-06",
                "2026-05-04", "2026-06-01", "2026-07-06", "2026-08-03",
                "2026-09-07", "2026-10-05", "2026-11-02", "2026-12-07",
                "2027-01-04", "2027-02-01", "2027-03-01", "2027-04-05",
                "2027-05-03", "2027-06-07", "2027-07-05", "2027-08-02",
                "2027-09-06", "2027-10-04", "2027-11-01", "2027-12-06"
            ],
            "mardi": [
                "2026-01-06", "2026-02-03", "2026-03-03", "2026-04-07",
                "2026-05-05", "2026-06-02", "2026-07-07", "2026-08-04",
                "2026-09-08", "2026-10-06", "2026-11-03", "2026-12-08",
                "2027-01-05", "2027-02-02", "2027-03-02", "2027-04-06",
                "2027-05-04", "2027-06-08", "2027-07-06", "2027-08-03",
                "2027-09-07", "2027-10-05", "2027-11-02", "2027-12-07"
            ],
            "mercredi": [
                "2026-01-07", "2026-02-04", "2026-03-04", "2026-04-08",
                "2026-05-06", "2026-06-03", "2026-07-08", "2026-08-05",
                "2026-09-09", "2026-10-07", "2026-11-04", "2026-12-09",
                "2027-01-06", "2027-02-03", "2027-03-03", "2027-04-07",
                "2027-05-05", "2027-06-09", "2027-07-07", "2027-08-04",
                "2027-09-08", "2027-10-06", "2027-11-03", "2027-12-08"
            ],
            "jeudi": [
                "2026-01-08", "2026-02-05", "2026-03-05", "2026-04-09",
                "2026-05-07", "2026-06-04", "2026-07-09", "2026-08-06",
                "2026-09-10", "2026-10-08", "2026-11-05", "2026-12-10",
                "2027-01-07", "2027-02-04", "2027-03-04", "2027-04-08",
                "2027-05-06", "2027-06-10", "2027-07-08", "2027-08-05",
                "2027-09-09", "2027-10-07", "2027-11-04", "2027-12-09"
            ]
        }
    },
    "Trélon": {
        "ordures": {
            "mercredi": [
                "Rue Victor Hugo", "Rue Aristide Briand", "Place du Maréchal Joffre",
                "Rue Delval", "Rue Emile Zola", "Rue des hirondelles",
                "Rue Neuve", "Rue Lobet", "rue des champs", "Rue Calmette",
                "Rue Guérin", "Rue du Maréchal Foch", "Chemin des sars",
                "Moulin de la Carnaille", "rue des Glycines",
                "Rue Robert Fontesse", "Résidence de la pierre trouée",
                "rue des églantines", "rue de Bellevue", "Rue Ernest Dimnet",
                "Rue des lilas", "rue de l'espérance", "rue de l'étoile",
                "rue du champ d'asile", "rue du fourneau", "rue du pont seru",
                "rue de la liberté", "route de chimay", "rue de la coulonnière",
                "impasse pasteur", "rue heureuse", "impasse ramon",
                "rue du quartier du tissage", "rue françois ansieau",
                "rue du petit marché", "rue guillaume deltour", "rue de la halle",
                "rue clavon collignon", "rue thiers", "rue gambetta",
                "rue andré daubercies", "rue escalier royal",
                "place léon comerre", "place de la piquerie",
                "chemin de la brasserie", "rue du belvédère",
                "rue georges clémenceau", "rue de la fonderie", "chemin vert",
                "avenue léo lagrange", "résidence les carmes",
                "cité le calloy", "rue du terne", "rue de verdun",
                "chemin de Laudrissart"
            ],
            "jeudi": [
                "rue Roger salengro", "rue du Canada", "Rue chartiaux",
                "rue augustin dimanche", "chemin des jardins", "rue des haies",
                "chemin des haies", "impasse des jardins", "impasse les carmes"
            ]
        },
        "verre": {
            "mercredi": [
                "2026-01-14", "2026-02-11", "2026-03-11", "2026-04-15",
                "2026-05-13", "2026-06-10", "2026-07-15", "2026-08-12",
                "2026-09-16", "2026-10-14", "2026-11-11", "2026-12-16",
                "2027-01-13", "2027-02-10", "2027-03-10", "2027-04-14",
                "2027-05-12", "2027-06-16", "2027-07-14", "2027-08-11",
                "2027-09-15", "2027-10-13", "2027-11-10", "2027-12-15"
            ],
            "jeudi": [
                "2026-01-15", "2026-02-12", "2026-03-12", "2026-04-16",
                "2026-05-14", "2026-06-11", "2026-07-16", "2026-08-13",
                "2026-09-17", "2026-10-15", "2026-11-12", "2026-12-17",
                "2027-01-14", "2027-02-11", "2027-03-11", "2027-04-15",
                "2027-05-13", "2027-06-17", "2027-07-15", "2027-08-12",
                "2027-09-16", "2027-10-14", "2027-11-11", "2027-12-16"
            ]
        }
    }
}


def get_dates_verre(commune, jour=None):
    """
    Récupère les dates de collecte du verre pour une commune.
    
    Args:
        commune: Nom de la commune
        jour: Jour de collecte (optionnel, pour Fourmies/Trélon)
    
    Returns:
        Liste des dates ou None si pas trouvé
    """
    if commune not in city_data:
        return None
    
    verre_data = city_data[commune].get("verre", {})
    
    # Si c'est un dictionnaire avec un seul jour
    if "dates" in verre_data:
        return verre_data["dates"]
    
    # Si c'est un dictionnaire avec plusieurs jours (Fourmies/Trélon)
    if jour and jour.lower() in verre_data:
        return verre_data[jour.lower()]
    
    # Si pas de jour spécifié mais qu'il y a un jour par défaut
    if "jour" in verre_data and verre_data["jour"] in verre_data:
        return verre_data[verre_data["jour"]]
    
    return None


def get_jour_ordures(commune, rue=None):
    """
    Récupère le jour de collecte des ordures.
    
    Args:
        commune: Nom de la commune
        rue: Nom de la rue (optionnel, pour Fourmies/Trélon)
    
    Returns:
        Tuple (jour, rue) ou (None, None) si pas trouvé
    """
    if commune not in city_data:
        return None, None
    
    ordures_data = city_data[commune].get("ordures", {})
    
    # Si c'est un string (jour unique pour toute la commune)
    if isinstance(ordures_data, str):
        return ordures_data, None
    
    # Si c'est un dict avec des rues (Fourmies/Trélon)
    if rue:
        rue_lower = rue.lower()
        for jour, rues in ordures_data.items():
            for r in rues:
                if r.lower() == rue_lower:
                    return jour, r
    
    return None, None


def get_available_cities():
    """Retourne la liste des communes disponibles."""
    return sorted(city_data.keys())
