"""Informations saisies une seule fois et affichées sur tout le site."""
from django.db import models
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.snippets.models import register_snippet


@register_setting(icon="site")
class SiteSettings(BaseSiteSetting):
    signature = models.CharField(max_length=120, default="Transport & Hébergement de données")
    adresse = models.TextField("Adresse du siège", blank=True)
    telephone_principal = models.CharField("Téléphone principal", max_length=40, blank=True)
    telephone_secondaire = models.CharField("Téléphone secondaire", max_length=40, blank=True)
    email_contact = models.EmailField("Courriel affiché", blank=True)
    horaires = models.CharField("Horaires d'ouverture", max_length=120, blank=True)
    lien_carte = models.URLField("Lien vers le plan d'accès", blank=True, help_text="Ex. : lien Google Maps ou OpenStreetMap.")
    facebook = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)

    panels = [
        FieldPanel("signature"),
        MultiFieldPanel(
            [FieldPanel("adresse"), FieldPanel("telephone_principal"), FieldPanel("telephone_secondaire"),
             FieldPanel("email_contact"), FieldPanel("horaires"), FieldPanel("lien_carte")],
            heading="Coordonnées officielles",
        ),
        MultiFieldPanel([FieldPanel("facebook"), FieldPanel("instagram"), FieldPanel("linkedin")], heading="Réseaux sociaux"),
    ]

    class Meta:
        verbose_name = "Paramètres du site"


@register_snippet
class ChiffreCle(models.Model):
    valeur = models.CharField(max_length=20, help_text="Ex. : 4 500")
    unite = models.CharField("Unité", max_length=20, blank=True, help_text="Ex. : km")
    libelle = models.CharField("Libellé", max_length=80, help_text="Ex. : de fibre optique")
    ordre = models.PositiveSmallIntegerField(default=0)

    panels = [FieldPanel("valeur"), FieldPanel("unite"), FieldPanel("libelle"), FieldPanel("ordre")]

    class Meta:
        ordering = ["ordre"]
        verbose_name = "Chiffre clé"
        verbose_name_plural = "Chiffres clés"

    def __str__(self):
        return f"{self.valeur} {self.unite} {self.libelle}".strip()


@register_snippet
class Valeur(models.Model):
    ICONES = [
        ("passion", "Flamme"), ("disponibilite", "Casque"), ("rapidite", "Éclair"),
        ("fiabilite", "Bouclier"), ("solidarite", "Mains"), ("responsabilite", "Globe"),
    ]
    nom = models.CharField(max_length=60)
    description = models.CharField(max_length=160)
    icone = models.CharField("Icône", max_length=20, choices=ICONES)
    ordre = models.PositiveSmallIntegerField(default=0)

    panels = [FieldPanel("nom"), FieldPanel("description"), FieldPanel("icone"), FieldPanel("ordre")]

    class Meta:
        ordering = ["ordre"]
        verbose_name = "Valeur"
        verbose_name_plural = "Valeurs"

    def __str__(self):
        return self.nom
