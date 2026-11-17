"""Blocs de contenu réutilisables : l'équipe les empile pour composer le corps des pages."""
from wagtail import blocks
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.images.blocks import ImageChooserBlock

RICHTEXT_FEATURES = ["h2", "h3", "bold", "italic", "ol", "ul", "link", "document-link"]


class SectionBlock(blocks.StructBlock):
    titre = blocks.CharBlock(max_length=120, help_text="Intertitre de la section (H2).")
    texte = blocks.RichTextBlock(features=RICHTEXT_FEATURES)

    class Meta:
        icon = "doc-full"
        label = "Section avec titre"
        template = "blocks/section.html"


class ImageBlock(blocks.StructBlock):
    image = ImageChooserBlock()
    texte_alternatif = blocks.CharBlock(
        max_length=125, required=False,
        help_text="Description de l'image pour l'accessibilité (30 à 80 caractères). Par défaut : titre de l'image.",
    )
    legende = blocks.CharBlock(max_length=200, required=False, label="Légende")

    class Meta:
        icon = "image"
        label = "Image"
        template = "blocks/image.html"


class ChiffreBlock(blocks.StructBlock):
    valeur = blocks.CharBlock(max_length=20, help_text="Ex. : 4 500")
    unite = blocks.CharBlock(max_length=20, required=False, label="Unité", help_text="Ex. : km")
    libelle = blocks.CharBlock(max_length=80, label="Libellé")


class ChiffresBlock(blocks.StructBlock):
    titre = blocks.CharBlock(max_length=120, required=False)
    chiffres = blocks.ListBlock(ChiffreBlock(), min_num=1, max_num=6)

    class Meta:
        icon = "pick"
        label = "Chiffres clés"
        template = "blocks/chiffres.html"


class CitationBlock(blocks.StructBlock):
    texte = blocks.TextBlock()
    auteur = blocks.CharBlock(max_length=120, required=False)

    class Meta:
        icon = "openquote"
        label = "Citation"
        template = "blocks/citation.html"


class ListeBlock(blocks.StructBlock):
    titre = blocks.CharBlock(max_length=120, required=False)
    elements = blocks.ListBlock(blocks.CharBlock(max_length=200), label="Éléments")

    class Meta:
        icon = "list-ul"
        label = "Liste à puces en colonnes"
        template = "blocks/liste.html"


class BoutonBlock(blocks.StructBlock):
    texte = blocks.CharBlock(max_length=60)
    page = blocks.PageChooserBlock(required=False)
    lien_externe = blocks.URLBlock(required=False)

    class Meta:
        icon = "link"
        label = "Bouton"
        template = "blocks/bouton.html"


class GalerieBlock(blocks.StructBlock):
    titre = blocks.CharBlock(max_length=120)
    images = blocks.ListBlock(ImageChooserBlock(), min_num=1)

    class Meta:
        icon = "image"
        label = "Album photo"
        template = "blocks/galerie.html"


class DocumentItemBlock(blocks.StructBlock):
    document = DocumentChooserBlock()
    description = blocks.CharBlock(max_length=200, required=False)


class DocumentsBlock(blocks.StructBlock):
    titre = blocks.CharBlock(max_length=120)
    documents = blocks.ListBlock(DocumentItemBlock(), min_num=1)

    class Meta:
        icon = "doc-full-inverse"
        label = "Liste de documents"
        template = "blocks/documents.html"


ICONES_MISSIONS = [
    ("reseau", "Réseau"), ("reglages", "Réglages"), ("poignee", "Poignée de main"), ("globe", "Globe"),
    ("serveur", "Serveur"), ("bouclier", "Bouclier"), ("antenne", "Antenne"), ("activite", "Activité"),
]


class MissionBlock(blocks.StructBlock):
    icone = blocks.ChoiceBlock(choices=ICONES_MISSIONS, default="reseau")
    titre = blocks.CharBlock(max_length=40)
    texte = blocks.TextBlock(max_length=220)

    class Meta:
        icon = "pick"
        label = "Mission"


class MissionsBlock(blocks.StructBlock):
    titre = blocks.CharBlock(max_length=120, required=False)
    missions = blocks.ListBlock(MissionBlock(), min_num=1, max_num=8)

    class Meta:
        icon = "pick"
        label = "Cartes de missions"
        template = "blocks/missions.html"


class TexteImageBlock(blocks.StructBlock):
    titre = blocks.CharBlock(max_length=120)
    texte = blocks.RichTextBlock(features=RICHTEXT_FEATURES)
    image = ImageChooserBlock(required=False, help_text="Laisser vide pour afficher une illustration en attendant la photo.")
    illustration = blocks.ChoiceBlock(
        choices=[("reseau", "Réseau"), ("fibre", "Fibre optique"), ("datacenter", "Data center")],
        default="reseau", help_text="Illustration affichée tant qu'aucune image n'est choisie.",
    )
    image_a_droite = blocks.BooleanBlock(required=False, default=True, label="Image à droite")

    class Meta:
        icon = "image"
        label = "Texte et image côte à côte"
        template = "blocks/texte_image.html"


class CorpsBlock(blocks.StreamBlock):
    """Blocs disponibles dans le corps des pages."""
    paragraphe = blocks.RichTextBlock(features=RICHTEXT_FEATURES, template="blocks/paragraphe.html")
    section = SectionBlock()
    image = ImageBlock()
    chiffres = ChiffresBlock()
    liste = ListeBlock()
    citation = CitationBlock()
    bouton = BoutonBlock()
    texte_image = TexteImageBlock()
    missions = MissionsBlock()


class MediathequeBlock(blocks.StreamBlock):
    documents = DocumentsBlock()
    galerie = GalerieBlock()
    paragraphe = blocks.RichTextBlock(features=RICHTEXT_FEATURES, template="blocks/paragraphe.html")


# ---------- Organigramme ----------
class EntiteBlock(blocks.StructBlock):
    intitule = blocks.CharBlock(max_length=120, label="Intitulé", help_text="Ex. : Direction marketing et communication")
    sigle = blocks.CharBlock(max_length=20, required=False)
    responsable = blocks.CharBlock(max_length=120, required=False,
                                   help_text="Nom et fonction. Laisser vide si la publication n'est pas autorisée.")
    photo = ImageChooserBlock(required=False)


class DirectionBlock(EntiteBlock):
    services = blocks.ListBlock(blocks.CharBlock(max_length=120), required=False, default=[],
                                help_text="Départements ou services rattachés à cette direction.")

    class Meta:
        icon = "group"
        label = "Direction"
