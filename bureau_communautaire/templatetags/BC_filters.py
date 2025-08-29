from django import template

register = template.Library()


@register.filter(name="divide")
def divide(value, arg):
    """Divides the value by the argument."""
    try:
        return float(value) / float(arg)
    except (ValueError, ZeroDivisionError):
        return 1


@register.filter(name="add_class")
def add_class(field, css_classes):
    return field.as_widget(attrs={"class": css_classes})
