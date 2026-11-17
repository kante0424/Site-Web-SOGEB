"""Ajoute au site les pages prévues après l'initialisation, sans rien modifier de ce qui existe déjà.

La commande peut être lancée autant de fois qu'on veut : elle ne crée une page que si elle manque.
Elle est appelée par LANCER_LE_SITE.bat, par scripts/deployer.sh et à la fin de initialiser_sogeb.
"""
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.home.contenu_par_defaut import MISSIONS
from apps.pages.models import OrganigrammePage, StandardPage


def _section(titre, *paragraphes):
    return ("section", {"titre": titre, "texte": "".join(f"<p>{p}</p>" for p in paragraphes)})


def _texte_image(titre, texte, illustration, a_droite=True):
    return ("texte_image", {"titre": titre, "texte": f"<p>{texte}</p>", "image": None,
                            "illustration": illustration, "image_a_droite": a_droite})


class Command(BaseCommand):
    help = "Ajoute les pages « Nos missions » et « Organigramme » sous « La SOGEB » si elles manquent."

    @transaction.atomic
    def handle(self, *args, **options):
        sogeb = StandardPage.objects.filter(slug="la-sogeb").first()
        if not sogeb:
            self.stdout.write("Page « La SOGEB » introuvable : rien à compléter.")
            return
        enfants = sogeb.get_children()

        if not enfants.filter(slug="missions").exists():
            missions = StandardPage(
                title="Nos missions", slug="missions", show_in_menus=True,
                seo_title="Missions de la SOGEB – Backbone national et data center",
                search_description="Gérer, exploiter, commercialiser et connecter : les missions de la SOGEB au "
                                   "service de la connectivité de la Guinée.",
                introduction="La SOGEB a pour rôle de faire du Backbone national à fibre optique une infrastructure "
                             "fiable, ouverte et utile à tout le pays.",
                corps=[
                    ("missions", {"titre": "", "missions": [
                        {"icone": i, "titre": t, "texte": x} for i, t, x in MISSIONS]}),
                    _texte_image(
                        "Gérer et exploiter le Backbone national",
                        "La SOGEB assure la gestion, l'exploitation et la maintenance du réseau de fibre optique qui "
                        "relie les 8 gouvernorats, les 33 préfectures et plus de 45 localités, ainsi que les liaisons "
                        "vers les pays voisins.", "fibre", True),
                    _texte_image(
                        "Héberger et protéger les données",
                        "Avec son data center Tier III, la SOGEB offre aux opérateurs, aux entreprises et aux "
                        "institutions un hébergement sécurisé et des services cloud supervisés en continu.",
                        "datacenter", False),
                    _texte_image(
                        "Accompagner la transformation numérique",
                        "En commercialisant les capacités du réseau auprès des opérateurs et fournisseurs d'accès, "
                        "la SOGEB contribue à rendre les services numériques accessibles sur tout le territoire.",
                        "reseau", True),
                ],
            )
            sogeb.add_child(instance=missions)
            missions.save_revision().publish()
            self.stdout.write(self.style.SUCCESS("Page « Nos missions » créée et publiée."))

        if not OrganigrammePage.objects.exists():
            organigramme = OrganigrammePage(
                title="Organigramme", slug="organigramme", show_in_menus=True, live=False,
                seo_title="Organigramme de la SOGEB",
                search_description="L'organisation de la SOGEB : Direction générale et directions.",
                introduction="L'organisation de la SOGEB autour de sa Direction générale.",
                directions=[
                    ("direction", {"intitule": "Direction marketing et communication", "sigle": "",
                                   "responsable": "", "photo": None, "services": []}),
                    ("direction", {"intitule": "DSSI", "sigle": "", "responsable": "", "photo": None, "services": []}),
                ],
            )
            sogeb.add_child(instance=organigramme)
            organigramme.save_revision()  # brouillon : à compléter et publier après accord de la Direction
            self.stdout.write(self.style.SUCCESS(
                "Page « Organigramme » créée en brouillon (à compléter puis publier dans l'administration)."))
