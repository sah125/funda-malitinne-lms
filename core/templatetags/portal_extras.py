# core/templatetags/portal_extras.py
from django import template

register = template.Library()

@register.filter
def risk_bootstrap_class(risk):
    """Convert risk level to Bootstrap class"""
    mapping = {
        'high': 'danger',
        'medium': 'warning',
        'low': 'success',
    }
    return mapping.get(risk, 'secondary')

@register.filter
def risk_color(risk):
    """Convert risk level to text color"""
    mapping = {
        'high': 'text-danger',
        'medium': 'text-warning',
        'low': 'text-success',
    }
    return mapping.get(risk, 'text-secondary')


@register.filter
def get_item(mapping, key):
    """{{ my_dict|get_item:key }} — dictionary lookup in templates."""
    try:
        return mapping.get(key)
    except AttributeError:
        return None
