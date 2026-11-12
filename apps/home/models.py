from django.db import models
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import StreamField
from wagtail.models import Page

from apps.core.blocks import CorpsBlock, MissionBlock  # noqa: F401 (MissionBlock : référencé par les migrations)


class HomePage(Page):
    surtitre = models.CharField(max_length=60, default="Infrastructure numérique nationale", blank=True,
                                help_text="Petite ligne dorée au-dessus du titre.")
    accroche = models.CharField(
        max_length=120,
        help_text="Titre principal de la page d'accueil (H1). Entourer un mot d'astérisques pour le mettre en "
                  "couleur, par exemple : Le réseau qui *relie* la Guinée.",
    )
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

    presentation_titre = models.CharField(
        "Titre", max_length=120, blank=True, default="Un acteur stratégique du numérique en Guinée")
    presentation_texte = models.TextField(
        "Texte", max_length=700, blank=True,
        default="La SOGEB gère et exploite le Backbone national à fibre optique, qui relie les 8 gouvernorats, "
                "les 33 préfectures et plus de 45 localités. Avec son data center Tier III, elle accompagne "
                "opérateurs, entreprises et institutions dans la transformation numérique de la Guinée.")
    presentation_points = models.TextField(
        "Points forts", max_length=400, blank=True,
        default="Infrastructure publique au service de l'État\nRéseau interconnecté aux pays voisins\n"
                "Data center Tier III supervisé 24 h/24",
        help_text="Un point par ligne.")
    presentation_image = models.ForeignKey(
        "wagtailimages.Image", null=True, blank=True, on_delete=models.SET_NULL, related_name="+",
        verbose_name="Image", help_text="Photo des équipes ou d'une infrastructure. Vide : illustration par défaut.")
    missions = StreamField([("mission", MissionBlock())], blank=True, max_num=4,
                           help_text="Les quatre missions affichées sous les chiffres clés.")
    corps = StreamField(CorpsBlock(), blank=True, help_text="Contenus complémentaires, affichés avant les actualités.")

    content_panels = Page.content_panels + [
        MultiFieldPanel([FieldPanel("surtitre"), FieldPanel("accroche"), FieldPanel("sous_titre"), FieldPanel("image_banniere"),
                         FieldPanel("bouton_texte"), FieldPanel("bouton_page")], heading="Bannière"),
        MultiFieldPanel([FieldPanel("backbone_titre"), FieldPanel("backbone_texte"), FieldPanel("backbone_page"),
                         FieldPanel("datacenter_titre"), FieldPanel("datacenter_texte"), FieldPanel("datacenter_page")],
                        heading="Les deux piliers"),
        MultiFieldPanel([FieldPanel("presentation_titre"), FieldPanel("presentation_texte"),
                         FieldPanel("presentation_points"), FieldPanel("presentation_image")],
                        heading="Présentation (Qui sommes-nous)"),
        FieldPanel("missions"),
        FieldPanel("corps"),
    ]

    max_count = 1
    parent_page_types = ["wagtailcore.Page"]

    class Meta:
        verbose_name = "Page d'accueil"

    def get_context(self, request, *args, **kwargs):
        from apps.actualites.models import NewsPage
        from apps.contact.models import ContactPage
        from apps.services.models import ServiceIndexPage, ServicePage

        context = super().get_context(request, *args, **kwargs)
        context["page_services"] = ServiceIndexPage.objects.live().public().first()
        context["services"] = ServicePage.objects.live().public().order_by("path")[:6]
        context["page_contact"] = ContactPage.objects.live().public().first()
        enfants = self.get_children().live().public()
        context["page_sogeb"] = enfants.filter(slug="la-sogeb").first()
        context["page_missions"] = Page.objects.live().public().filter(slug="missions").descendant_of(self).first()
        context["points_presentation"] = [p.strip() for p in self.presentation_points.splitlines() if p.strip()]
        context["dernieres_actualites"] = (
            NewsPage.objects.live().public().exclude(categorie="vie").order_by("-date_publication")[:3]
        )
        return context
