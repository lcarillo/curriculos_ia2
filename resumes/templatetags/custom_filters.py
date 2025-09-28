from django import template

register = template.Library()


@register.filter
def title_case(value):
    """Converte texto para Title Case"""
    if not value:
        return value
    return value.replace('_', ' ').title()


@register.filter
def replace(value, arg):
    """
    Replace filter for template
    Usage: {{ value|replace:"from_text,to_text" }}
    """
    if not value:
        return value

    args = arg.split(',')
    if len(args) != 2:
        return value

    return value.replace(args[0], args[1])