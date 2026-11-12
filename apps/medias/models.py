from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.fields import StreamField
from wagtail.models import Page

from apps.core.blocks import MediathequeBlock


class MediaPage(Page):
    introduction = models.TextField(max_length=500, blank=True)
    contenu = StreamField(MediathequeBlock(), blank=True, help_text="Listes de documents publics et albums photos.")

    content_panels = Page.content_panels + [FieldPanel("introduction"), FieldPanel("contenu")]
    subpage_types = []
    max_count = 1

    class Meta:
        verbose_name = "Documents et médias"
