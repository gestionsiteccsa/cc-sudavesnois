from django import template

register = template.Library()


@register.filter
def format_phone_number(phone_number):
    """
    Formate un numéro de téléphone au format français.
    0123439434 -> 01 23 43 94 34
    """
    if not phone_number:
        return ""

    # Supprimer les espaces
    phone_number = phone_number.replace(" ", "")

    # Vérifier si le numéro est valide
    if len(phone_number) != 10 or not phone_number.isdigit():
        return phone_number

    # Formater le numéro
    formatted_number = f"{phone_number[:2]} {phone_number[2:4]} {phone_number[4:6]} \
                         {phone_number[6:8]} {phone_number[8:]}"

    return formatted_number


@register.filter
def format_phone_to_link(phone_number):
    """
    Formate un numéro de téléphone pour l'affichage dans un lien tel.
    0123456789 -> +33123456789
    """
    if not phone_number:
        return ""

    # Ajouter +33 pour les numéros français
    if phone_number.startswith("0"):
        phone_number = "+33" + phone_number[1:]
    else:
        phone_number = "+33" + phone_number

    return phone_number
