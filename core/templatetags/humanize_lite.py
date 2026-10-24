from django import template

register = template.Library()


@register.filter
def thousands(value):
    """12500 -> '12,500'. Leaves non-numbers untouched."""
    try:
        return f"{int(value):,}"
    except (TypeError, ValueError):
        return value
