from django import template

register = template.Library()

# Mapping des jours de la semaine en français
JOURS_SEMAINE = {
    0: "Lundi",
    1: "Mardi",
    2: "Mercredi",
    3: "Jeudi",
    4: "Vendredi",
    5: "Samedi",
    6: "Dimanche",
}

# Mapping des mois en français
MOIS = {
    1: "janvier",
    2: "février",
    3: "mars",
    4: "avril",
    5: "mai",
    6: "juin",
    7: "juillet",
    8: "août",
    9: "septembre",
    10: "octobre",
    11: "novembre",
    12: "décembre",
}

# Mapping des mois en français abrégés
MOIS_ABREGE = {
    1: "janv.",
    2: "févr.",
    3: "mars",
    4: "avr.",
    5: "mai",
    6: "juin",
    7: "juil.",
    8: "août",
    9: "sept.",
    10: "oct.",
    11: "nov.",
    12: "déc.",
}


@register.filter
def date_fr_complete(date):
    """
    Formate une date au format français complet : "Lundi 15 janvier 2024"
    """
    if not date:
        return ""

    jour_semaine = JOURS_SEMAINE[date.weekday()]
    jour = date.day
    mois = MOIS[date.month]
    annee = date.year

    # Formater le jour avec "1er" pour le premier du mois
    jour_str = "1er" if jour == 1 else str(jour)

    return f"{jour_semaine} {jour_str} {mois} {annee}"


@register.filter
def mois_fr_abrege(date):
    """
    Formate le mois en français abrégé : "févr." pour février
    """
    if not date:
        return ""

    return MOIS_ABREGE[date.month]



