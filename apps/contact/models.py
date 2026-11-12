from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, FieldRowPanel, InlinePanel, MultiFieldPanel
from wagtail.contrib.forms.models import AbstractEmailForm, AbstractFormField
from wagtail.contrib.forms.panels import FormSubmissionsPanel

# Champ piège invisible : un humain le laisse vide, un robot le remplit
CHAMP_PIEGE = "site_web"


class FormField(AbstractFormField):
    page = ParentalKey("ContactPage", on_delete=models.CASCADE, related_name="form_fields")


class ContactPage(AbstractEmailForm):
    introduction = models.TextField(max_length=500, blank=True)
    texte_confirmation = models.TextField(default="Merci, votre message a bien été transmis. Nous vous répondrons dans les meilleurs délais.")

    content_panels = AbstractEmailForm.content_panels + [
        FormSubmissionsPanel(),
        FieldPanel("introduction"),
        InlinePanel("form_fields", label="Champs du formulaire"),
        FieldPanel("texte_confirmation"),
        MultiFieldPanel([
            FieldRowPanel([FieldPanel("from_address", classname="col6"), FieldPanel("to_address", classname="col6")]),
            FieldPanel("subject"),
        ], heading="Envoi par courriel"),
    ]
    landing_page_template = "contact/contact_page_confirmation.html"
    subpage_types = []
    max_count = 1

    class Meta:
        verbose_name = "Page contact"

    def serve(self, request, *args, **kwargs):
        if request.method == "POST" and request.POST.get(CHAMP_PIEGE):
            # Robot détecté : on affiche la confirmation sans rien enregistrer ni envoyer
            return self.render_landing_page(request, None, *args, **kwargs)
        return super().serve(request, *args, **kwargs)
