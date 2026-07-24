from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
@stringfilter
def flag_emoji(country_code: str) -> str:
    if not country_code or len(country_code) != 2:
        return ""
    code = country_code.upper()
    points = [127462 + ord(c) - ord("A") for c in code]
    return chr(points[0]) + chr(points[1])


@register.filter
def country_name(code: str) -> str:
    names = {
        "FR": "France",
        "BE": "Belgique",
        "CH": "Suisse",
        "LU": "Luxembourg",
        "DE": "Allemagne",
        "IT": "Italie",
        "ES": "Espagne",
        "GB": "Royaume-Uni",
        "NL": "Pays-Bas",
        "PT": "Portugal",
        "CA": "Canada",
        "US": "États-Unis",
        "MA": "Maroc",
        "DZ": "Algérie",
        "TN": "Tunisie",
        "SN": "Sénégal",
        "CI": "Côte d'Ivoire",
        "CM": "Cameroun",
        "CD": "République Démocratique du Congo",
        "HT": "Haïti",
        "LB": "Liban",
        "SY": "Syrie",
        "VN": "Vietnam",
        "CN": "Chine",
        "JP": "Japon",
        "KR": "Corée du Sud",
        "IN": "Inde",
        "RU": "Russie",
        "BR": "Brésil",
        "AR": "Argentine",
        "CL": "Chili",
        "MX": "Mexique",
        "AU": "Australie",
        "NZ": "Nouvelle-Zélande",
        "SE": "Suède",
        "NO": "Norvège",
        "DK": "Danemark",
        "FI": "Finlande",
        "IE": "Irlande",
        "AT": "Autriche",
        "PL": "Pologne",
        "CZ": "République Tchèque",
        "SK": "Slovaquie",
        "HU": "Hongrie",
        "RO": "Roumanie",
        "BG": "Bulgarie",
        "GR": "Grèce",
        "TR": "Turquie",
        "IL": "Israël",
        "AE": "Émirats Arabes Unis",
        "ZA": "Afrique du Sud",
        "NG": "Nigeria",
        "EG": "Égypte",
        "KE": "Kenya",
        "SG": "Singapour",
        "HK": "Hong Kong",
        "TW": "Taïwan",
        "TH": "Thaïlande",
        "MY": "Malaisie",
        "ID": "Indonésie",
        "PH": "Philippines",
        "PK": "Pakistan",
        "BD": "Bangladesh",
        "SA": "Arabie Saoudite",
        "QA": "Qatar",
        "KW": "Koweït",
        "OM": "Oman",
        "PE": "Pérou",
        "CO": "Colombie",
        "VE": "Venezuela",
    }
    return names.get(code.upper(), code)
