from django import template

register = template.Library()
ETATS = {"respectee": "Respectée", "a_risque": "À risque", "violee": "Violée"}


@register.filter
def etat_regle(code):
    return ETATS.get(code, code)
