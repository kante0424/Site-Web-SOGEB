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


class CorpsBlock(blocks.StreamBlock):
    """Blocs disponibles dans le corps des pages."""
    paragraphe = blocks.RichTextBlock(features=RICHTEXT_FEATURES, template="blocks/paragraphe.html")
    section = SectionBlock()
    image = ImageBlock()
    chiffres = ChiffresBlock()
    liste = ListeBlock()
    citation = CitationBlock()
    bouton = BoutonBlock()


class MediathequeBlock(blocks.StreamBlock):
    documents = DocumentsBlock()
    galerie = GalerieBlock()
    paragraphe = blocks.RichTextBlock(features=RICHTEXT_FEATURES, template="blocks/paragraphe.html")
