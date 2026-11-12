from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.fields import StreamField
from wagtail.models import Page

from apps.core.blocks import CorpsBlock


class StandardPage(Page):
    """La SOGEB, mentions légales, politique de confidentialité…"""
    introduction = models.TextField(max_length=500, blank=True)
    image = models.ForeignKey("wagtailimages.Image", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    corps = StreamField(CorpsBlock(), blank=True)
    afficher_valeurs = models.BooleanField("Afficher les valeurs de la SOGEB", default=False)

    content_panels = Page.content_panels + [
        FieldPanel("introduction"), FieldPanel("image"), FieldPanel("corps"), FieldPanel("afficher_valeurs"),
    ]
    subpage_types = ["pages.StandardPage"]

    class Meta:
        verbose_name = "Page institutionnelle"


class InfrastructurePage(Page):
    """Backbone national et Data center."""
    introduction = models.TextField(max_length=500)
    image = models.ForeignKey("wagtailimages.Image", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    carte = models.ForeignKey(
        "wagtailimages.Image", null=True, blank=True, on_delete=models.SET_NULL, related_name="+",
        help_text="Carte simplifiée validée (villes et axes uniquement, sans tracé précis ni coordonnées).",
    )
    corps = StreamField(CorpsBlock(), blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("introduction"), FieldPanel("image"), FieldPanel("carte"), FieldPanel("corps"),
    ]
    subpage_types = []

    class Meta:
        verbose_name = "Page infrastructure"
