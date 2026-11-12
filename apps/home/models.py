from django.db import models
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import StreamField
from wagtail.models import Page

from apps.core.blocks import CorpsBlock


class HomePage(Page):
    accroche = models.CharField(max_length=120, help_text="Titre principal de la page d'accueil (H1).")
    sous_titre = models.TextField(max_length=300, blank=True)
    image_banniere = models.ForeignKey(
        "wagtailimages.Image", null=True, blank=True, on_delete=models.SET_NULL, related_name="+",
        help_text="Photographie réelle d'une infrastructure SOGEB, format paysage, 1920 px de large au minimum.",
    )
    bouton_texte = models.CharField(max_length=40, default="Découvrir nos services")
    bouton_page = models.ForeignKey("wagtailcore.Page", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")

    backbone_titre = models.CharField(max_length=80, default="Backbone national")
    backbone_texte = models.TextField(max_length=400, blank=True)
    backbone_page = models.ForeignKey("wagtailcore.Page", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    datacenter_titre = models.CharField(max_length=80, default="Data center Tier III")
    datacenter_texte = models.TextField(max_length=400, blank=True)
    datacenter_page = models.ForeignKey("wagtailcore.Page", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")

    corps = StreamField(CorpsBlock(), blank=True, help_text="Contenus complémentaires, affichés avant les actualités.")

    content_panels = Page.content_panels + [
        MultiFieldPanel([FieldPanel("accroche"), FieldPanel("sous_titre"), FieldPanel("image_banniere"),
                         FieldPanel("bouton_texte"), FieldPanel("bouton_page")], heading="Bannière"),
        MultiFieldPanel([FieldPanel("backbone_titre"), FieldPanel("backbone_texte"), FieldPanel("backbone_page"),
                         FieldPanel("datacenter_titre"), FieldPanel("datacenter_texte"), FieldPanel("datacenter_page")],
                        heading="Les deux piliers"),
        FieldPanel("corps"),
    ]

    max_count = 1
    parent_page_types = ["wagtailcore.Page"]

    class Meta:
        verbose_name = "Page d'accueil"

    def get_context(self, request, *args, **kwargs):
        from apps.actualites.models import NewsPage

        context = super().get_context(request, *args, **kwargs)
        context["dernieres_actualites"] = (
            NewsPage.objects.live().public().exclude(categorie="vie").order_by("-date_publication")[:3]
        )
        return context
