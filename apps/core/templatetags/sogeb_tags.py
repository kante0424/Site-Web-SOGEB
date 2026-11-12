from django import template
from wagtail.models import Site

from apps.core.models import ChiffreCle, Valeur

register = template.Library()


@register.simple_tag(takes_context=True)
def menu_principal(context):
    """Pages enfants de l'accueil cochées « Afficher dans les menus »."""
    site = Site.find_for_request(context["request"])
    if not site:
        return []
    return site.root_page.get_children().live().in_menu().specific()


@register.simple_tag(takes_context=True)
def accueil(context):
    site = Site.find_for_request(context["request"])
    return site.root_page if site else None


@register.simple_tag
def chiffres_cles():
    return ChiffreCle.objects.all()


@register.simple_tag
def valeurs():
    return Valeur.objects.all()


@register.filter
def est_dans(page, courante):
    """Vrai si la page courante est cette page ou l'une de ses descendantes (menu actif)."""
    return courante is not None and courante.path.startswith(page.path)
