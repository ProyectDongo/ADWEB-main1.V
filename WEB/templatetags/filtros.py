from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Filtra las notificaciones por el ID de VigenciaPlan.
    """
    return dictionary.get(key, [])