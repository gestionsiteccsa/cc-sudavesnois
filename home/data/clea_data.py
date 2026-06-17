"""Données structurées pour la page CLÉA+.

Le CLÉA+ (Contrat Local d'Éducation Artistique) est un dispositif de
résidence-mission visant à démocratiser l'accès à la culture et à l'art
contemporain sur le territoire de la Communauté de Communes Sud-Avesnois.

Ce module respecte le principe de responsabilité unique (SRP) en isolant
le contenu éditorial de la couche présentation.
"""

PAGE_TITLE = "CLÉA+"
PAGE_SUBTITLE = "Contrat local d'éducation artistique"
META_DESCRIPTION = (
    "Découvrez le CLÉA+ de la Communauté de Communes Sud-Avesnois : "
    "résidence-mission, axes prioritaires et actions pour démocratiser "
    "l'accès à la culture et à l'art contemporain."
)

RESIDENCE_MISSION = {
    "title": "Une résidence mission, qu'est-ce que c'est ?",
    "paragraphs": [
        (
            "Une résidence-mission n'est pas une résidence de création, "
            "il n'y a, ni commande d'œuvre ni enjeu de production conséquent."
        ),
        (
            "Il s'agit pour l'artiste-résident de s'engager artistiquement "
            "dans une démarche d'expérimentation artistique à des fins de "
            "démocratisation culturelle."
        ),
        (
            "Celui-ci est invité à donner à voir, à comprendre, à ressentir, "
            "à vivre même, de manière innovante, la recherche artistique qui "
            "l'anime ainsi que les processus de création qu'il met en œuvre."
        ),
        "Chaque année, les rencontres prennent des formes très variées.",
    ],
}

AXES_SECTION = {
    "title": "Nos axes pour le CLÉA nouvelle génération",
    "introduction": (
        "Rappel des axes prioritaires choisis en 2023 pour notre CLÉA "
        "nouvelle génération, parmi 5 axes proposés par la DRAC pour les "
        "CLEA+, notre COPIL a choisi les deux suivants :"
    ),
    "axes": [
        {
            "id": "temps-culture",
            "title": "Les temps de la culture : nouveaux temps, nouveaux lieux",
            "content": (
                "Au travers de cet axe, l'objectif est d'investir, de "
                "réenchanter les lieux et les temps du quotidien afin d'aller "
                "toucher les habitants dans d'autres temps de vie et de faire "
                "émerger de nouveaux espaces de dialogue avec les présences "
                "artistiques."
            ),
            "theme": "blue",
        },
        {
            "id": "jeunesses",
            "title": "Les jeunesses",
            "content": (
                "Le CLÉA en Sud-Avesnois étant tout au long de la vie, il "
                "associe l'éducation nationale, de la maternelle au lycée, "
                "mais également d'autres partenaires du hors temps scolaire. "
                "Les 3-14 ans sont un public phare du dispositif depuis sa "
                "création et l'objectif du nouveau conventionnement est de "
                "toucher la jeunesse dans son ensemble de 0 à 25 ans."
            ),
            "theme": "green",
        },
    ],
}

INFO_CARDS = [
    {
        "id": "quoi",
        "title": "Quoi ?",
        "icon": "target",
        "content": (
            "L'objectif principal est de favoriser l'accès à la culture et "
            "à l'art contemporain au plus grand nombre."
        ),
    },
    {
        "id": "qui",
        "title": "Qui ?",
        "icon": "users",
        "content": (
            "Tous les habitants du territoire de la CCSA et des artistes "
            "professionnels."
        ),
    },
    {
        "id": "quand",
        "title": "Quand ?",
        "icon": "calendar",
        "content": ("Chaque année, pour une durée de quatre mois consécutifs."),
    },
    {
        "id": "comment",
        "title": "Comment ?",
        "icon": "sparkles",
        "content": (
            "Par des rencontres entre les artistes et les habitants, la "
            "diffusion d'œuvres et l'expérimentation de gestes artistiques."
        ),
    },
]
