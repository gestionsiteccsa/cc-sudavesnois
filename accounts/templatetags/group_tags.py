from django import template

register = template.Library()


@register.filter(name="is_in_group")
def is_in_group(user, group_name):
    """
    Retourne True si l'utilisateur appartient au groupe spécifié
    ou si il est superutilisateur, sinon False.
    """
    if user.groups.filter(name=group_name).exists() or user.is_superuser:
        return True
    return False
