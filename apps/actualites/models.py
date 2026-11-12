from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models
from django.utils import timezone
from wagtail.admin.panels import FieldPanel
from wagtail.fields import StreamField
from wagtail.models import Page
from wagtail.search import index

from apps.core.blocks import CorpsBlock

CATEGORIES = [("actualite", "Actualité"), ("communique", "Communiqué"), ("vie", "Vie de l'entreprise")]


class NewsIndexPage(Page):
    introduction = models.TextField(max_length=500, blank=True)

    content_panels = Page.content_panels + [FieldPanel("introduction")]
    subpage_types = ["actualites.NewsPage"]
    max_count = 1

    class Meta:
        verbose_name = "Liste des actualités"

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        articles = NewsPage.objects.child_of(self).live().public().order_by("-date_publication")
        categorie = request.GET.get("categorie")
        if categorie in dict(CATEGORIES):
            articles = articles.filter(categorie=categorie)
        paginator = Paginator(articles, 9)
        try:
            page_articles = paginator.page(request.GET.get("page", 1))
        except (PageNotAnInteger, EmptyPage):
            page_articles = paginator.page(1)
        context.update(articles=page_articles, categories=CATEGORIES, categorie_active=categorie)
        return context


class NewsPage(Page):
    date_publication = models.DateField("Date", default=timezone.localdate)
    categorie = models.CharField("Catégorie", max_length=20, choices=CATEGORIES, default="actualite")
    image = models.ForeignKey("wagtailimages.Image", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    chapo = models.TextField("Chapô", max_length=300, help_text="Résumé affiché dans les listes (2 à 3 phrases).")
    corps = StreamField(CorpsBlock(), blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("date_publication"), FieldPanel("categorie"), FieldPanel("image"), FieldPanel("chapo"), FieldPanel("corps"),
    ]
    search_fields = Page.search_fields + [index.SearchField("chapo"), index.SearchField("corps")]
    parent_page_types = ["actualites.NewsIndexPage"]
    subpage_types = []

    class Meta:
        verbose_name = "Article"
