from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.fields import StreamField
from wagtail.models import Page

from apps.core.blocks import CorpsBlock

PILIERS = [("backbone", "Backbone national (transport)"), ("datacenter", "Data center (hébergement)")]


class ServiceIndexPage(Page):
    introduction = models.TextField(max_length=500, blank=True)

    content_panels = Page.content_panels + [FieldPanel("introduction")]
    subpage_types = ["services.ServicePage"]
    max_count = 1

    class Meta:
        verbose_name = "Liste des services"

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        services = ServicePage.objects.child_of(self).live().public()
        context["groupes"] = [
            {"code": code, "titre": titre, "services": [s for s in services if s.pilier == code]}
            for code, titre in PILIERS
        ]
        return context


class ServicePage(Page):
    pilier = models.CharField(max_length=20, choices=PILIERS)
    resume = models.CharField("Résumé", max_length=220, help_text="Phrase affichée sur la carte du service.")
    publics = models.CharField(max_length=200, blank=True, help_text="Ex. : opérateurs, FAI, entreprises, institutions.")
    image = models.ForeignKey("wagtailimages.Image", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    corps = StreamField(CorpsBlock(), blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("pilier"), FieldPanel("resume"), FieldPanel("publics"), FieldPanel("image"), FieldPanel("corps"),
    ]
    parent_page_types = ["services.ServiceIndexPage"]
    subpage_types = []

    class Meta:
        verbose_name = "Fiche service"
