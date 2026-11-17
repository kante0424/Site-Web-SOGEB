from django.db import models
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import StreamField
from wagtail.models import Page

from apps.core.blocks import CorpsBlock, DirectionBlock, EntiteBlock


class StandardPage(Page):
    """La SOGEB, mentions légales, politique de confidentialité…"""
    introduction = models.TextField(max_length=500, blank=True)
    image = models.ForeignKey("wagtailimages.Image", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    corps = StreamField(CorpsBlock(), blank=True)
    afficher_valeurs = models.BooleanField("Afficher les valeurs de la SOGEB", default=False)

    content_panels = Page.content_panels + [
        FieldPanel("introduction"), FieldPanel("image"), FieldPanel("corps"), FieldPanel("afficher_valeurs"),
    ]
    subpage_types = ["pages.StandardPage", "pages.OrganigrammePage"]

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


class OrganigrammePage(Page):
    """Organisation de la SOGEB : Direction générale, entités rattachées et directions."""
    introduction = models.TextField(max_length=500, blank=True)
    dg_intitule = models.CharField("Intitulé", max_length=120, default="Direction générale")
    dg_responsable = models.CharField(
        "Responsable", max_length=120, blank=True,
        help_text="Nom et fonction. Laisser vide si la publication n'est pas autorisée.")
    dg_photo = models.ForeignKey("wagtailimages.Image", null=True, blank=True, on_delete=models.SET_NULL,
                                 related_name="+", verbose_name="Photo")
    rattachements = StreamField(
        [("entite", EntiteBlock(label="Entité rattachée"))], blank=True,
        verbose_name="Entités rattachées à la Direction générale",
        help_text="Ex. : secrétariat général, audit interne, conseillers.")
    directions = StreamField([("direction", DirectionBlock())], blank=True)
    image_organigramme = models.ForeignKey(
        "wagtailimages.Image", null=True, blank=True, on_delete=models.SET_NULL, related_name="+",
        verbose_name="Organigramme officiel (image)",
        help_text="Facultatif : version graphique validée, proposée en complément du schéma.")

    content_panels = Page.content_panels + [
        FieldPanel("introduction"),
        MultiFieldPanel([FieldPanel("dg_intitule"), FieldPanel("dg_responsable"), FieldPanel("dg_photo")],
                        heading="Direction générale"),
        FieldPanel("rattachements"),
        FieldPanel("directions"),
        FieldPanel("image_organigramme"),
    ]
    parent_page_types = ["pages.StandardPage"]
    subpage_types = []
    max_count = 1

    class Meta:
        verbose_name = "Organigramme"
