"""
Crée l'arborescence du site, les contenus officiels de départ, les rôles et le circuit de validation.

Usage : python manage.py initialiser_sogeb
À lancer une seule fois sur une base neuve (après « migrate »). Les textes viennent des documents
officiels transmis par la Direction marketing et communication ; ils restent modifiables dans l'administration.
"""
import json

from django.contrib.auth.models import Group, Permission
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from wagtail.models import (
    Collection, GroupApprovalTask, GroupCollectionPermission, GroupPagePermission, Page, Site,
    Workflow, WorkflowPage, WorkflowTask,
)

from apps.actualites.models import NewsIndexPage
from apps.contact.models import ContactPage, FormField
from apps.core.models import ChiffreCle, SiteSettings, Valeur
from apps.home.contenu_par_defaut import ACCROCHE, missions_stream
from apps.home.models import HomePage
from apps.medias.models import MediaPage
from apps.pages.models import InfrastructurePage, StandardPage
from apps.services.models import ServiceIndexPage, ServicePage


def corps(*blocs):
    """Construit la valeur d'un StreamField à partir de tuples (type, valeur)."""
    return json.dumps([{"type": t, "value": v} for t, v in blocs])


def section(titre, *paragraphes):
    return ("section", {"titre": titre, "texte": "".join(f"<p>{p}</p>" for p in paragraphes)})


def liste(titre, elements):
    return ("liste", {"titre": titre, "elements": elements})


CHIFFRES = [
    ("4 500", "km", "de fibre optique"),
    ("33", "", "préfectures raccordées"),
    ("62", "", "points d'interconnexion nationaux"),
    ("1 000", "To", "de stockage au data center"),
]

VALEURS = [
    ("Passion", "Faire du client l'ADN de nos clients", "passion"),
    ("Disponibilité", "Une présence continue pour nos partenaires", "disponibilite"),
    ("Rapidité", "Des interventions efficaces et réactives", "rapidite"),
    ("Fiabilité", "Des infrastructures sûres et sécurisées", "fiabilite"),
    ("Solidarité", "Une collaboration forte en interne et en externe", "solidarite"),
    ("Responsabilité sociale", "Un engagement durable pour la Guinée", "responsabilite"),
]

SERVICES = [
    ("backbone", "Liaisons louées nationales", "liaisons-louees-nationales",
     "Des capacités de transmission point à point, de 50 Mbps à 200 Gbps, entre deux sites du territoire national.",
     "Opérateurs de télécommunications, fournisseurs d'accès Internet, entités autorisées par l'ARPT",
     [section("Le service",
              "Le service de liaisons louées nationales met à disposition des capacités de transmission de données "
              "entre deux sites géographiques de la République de Guinée, sur les infrastructures de transport à fibre "
              "optique de la SOGEB. Il permet de transporter de la voix, des données, de la vidéo et du trafic Internet "
              "avec un débit symétrique et constant, une qualité de service élevée et une supervision continue."),
      liste("Usages typiques", ["Interconnexion de commutateurs, routeurs, data centers et nœuds techniques",
                                "Transport de trafic entre réseaux métropolitains et cœur national",
                                "Collecte des flux de trafic mobile ou Internet",
                                "Hébergement de services managés (VPN, MPLS)"]),
      liste("Technologies", ["SDH (STM-1 à STM-64)", "DWDM jusqu'à 200 Gbps", "Ethernet / IP / MPLS"])]),
    ("backbone", "Capacité internationale et transit IP", "capacite-internationale-transit-ip",
     "Un accès à la capacité internationale et au transit IP grâce aux interconnexions transfrontalières du Backbone.",
     "Opérateurs, fournisseurs d'accès Internet",
     [section("Le service",
              "Le Backbone national est interconnecté aux réseaux des pays voisins : Guinée-Bissau, Sénégal, Mali, "
              "Côte d'Ivoire, Libéria et Sierra Leone. La SOGEB propose l'accès à la capacité internationale et le "
              "transit IP international aux opérateurs autorisés.")]),
    ("backbone", "Colocation et partage d'infrastructures", "colocation-partage-infrastructures",
     "L'hébergement d'équipements dans les sites techniques de la SOGEB et le partage d'infrastructures entre opérateurs.",
     "Opérateurs, fournisseurs d'accès Internet",
     [section("Le service",
              "La colocation d'interconnexion permet aux opérateurs d'installer leurs équipements dans les points "
              "d'interconnexion de la SOGEB, avec l'énergie sécurisée et la supervision du NOC. Le service de "
              "cross-connexion relie directement les équipements de deux opérateurs présents sur un même site.")]),
    ("datacenter", "Colocation de racks", "colocation-racks",
     "Des espaces sécurisés au data center Tier III pour héberger vos serveurs et équipements réseau.",
     "Entreprises, institutions, opérateurs",
     [section("Le service",
              "Le data center SOGEB de niveau Tier III accueille les équipements de ses clients dans des salles "
              "sécurisées, avec une alimentation électrique redondante, le refroidissement des serveurs et un accès "
              "au réseau à très haut débit.")]),
    ("datacenter", "Cloud et virtualisation", "cloud-virtualisation",
     "Des serveurs virtuels, du stockage et des ressources cloud évolutives, hébergés en Guinée.",
     "Entreprises, administrations, startups",
     [liste("Services proposés", ["Cloud hosting", "Virtualisation", "Serveurs privés virtuels (VPS)",
                                  "Stockage et partage de fichiers", "Bases de données", "Hébergement de startups"])]),
    ("datacenter", "Hébergement et services collaboratifs", "hebergement-services-collaboratifs",
     "Hébergement de sites web, messagerie professionnelle, visioconférence et outils de travail collaboratif.",
     "Entreprises, administrations, institutions",
     [liste("Services proposés", ["Hébergement de sites web", "Messagerie professionnelle et instantanée",
                                  "Serveurs VoIP et visioconférence", "Plateformes collaboratives",
                                  "GED, GEC, CRM, CMS", "DNS", "Streaming"])]),
    ("datacenter", "Services managés SOC et NOC", "services-manages-soc-noc",
     "Supervision 24 h/24 et 7 j/7 de vos réseaux et protection de vos systèmes par nos équipes.",
     "Entreprises, institutions, opérateurs",
     [section("Le service",
              "Le centre de supervision réseau (NOC) surveille en continu les liens, serveurs et équipements. "
              "Le centre de sécurité (SOC) contrôle le trafic et prévient les intrusions grâce à des pare-feu de "
              "dernière génération, une protection anti-DDoS et un pare-feu applicatif.")]),
]


class Command(BaseCommand):
    help = "Crée l'arborescence, les contenus officiels de départ, les rôles et le circuit de validation."

    @transaction.atomic
    def handle(self, *args, **options):
        if HomePage.objects.exists():
            raise CommandError("Le site est déjà initialisé (une page d'accueil SOGEB existe).")

        racine = Page.get_first_root_node()
        accueil = self.creer_pages(racine)
        site = Site.objects.filter(is_default_site=True).first()
        if site:
            ancienne = site.root_page
            site.root_page = accueil
            site.site_name = "SOGEB"
            site.save()
            if ancienne.specific_class is Page and ancienne.depth == 2:
                ancienne.delete()  # page de bienvenue créée par Wagtail
        else:
            site = Site.objects.create(hostname="localhost", port=80, root_page=accueil, is_default_site=True, site_name="SOGEB")

        SiteSettings.for_site(site).save()
        for i, (valeur, unite, libelle) in enumerate(CHIFFRES):
            ChiffreCle.objects.create(valeur=valeur, unite=unite, libelle=libelle, ordre=i)
        for i, (nom, description, icone) in enumerate(VALEURS):
            Valeur.objects.create(nom=nom, description=description, icone=icone, ordre=i)

        self.creer_roles(accueil)
        call_command("completer_sogeb")
        self.stdout.write(self.style.SUCCESS("Site SOGEB initialisé."))

    # ------------------------------------------------------------------ pages
    def creer_pages(self, racine):
        accueil = racine.add_child(instance=HomePage(
            title="Accueil", slug="accueil",
            seo_title="SOGEB – Backbone national à fibre optique et data center en Guinée",
            search_description="La SOGEB exploite le Backbone national à fibre optique et un data center Tier III "
                               "au service des opérateurs, entreprises et institutions de Guinée.",
            accroche=ACCROCHE,
            missions=missions_stream(),
            sous_titre="Près de 4 500 km de fibre optique et un data center Tier III pour transporter et héberger "
                       "les données des opérateurs, des entreprises et des institutions.",
            backbone_texte="Un réseau de fibre optique qui relie les 8 gouvernorats, les 33 préfectures et plus de "
                           "45 localités, interconnecté aux pays voisins.",
            datacenter_texte="Un data center Tier III de plus de 1 000 To, avec une gamme complète de services cloud "
                             "sécurisés et évolutifs.",
        ))

        def ajouter(parent, page):
            return parent.add_child(instance=page)

        ajouter(accueil, StandardPage(
            title="La SOGEB", slug="la-sogeb", show_in_menus=True, afficher_valeurs=True,
            seo_title="La SOGEB – Société de Gestion et d'Exploitation du Backbone National",
            search_description="Présentation, missions et valeurs de la SOGEB, opérateur d'infrastructures du "
                               "Backbone national à fibre optique de Guinée.",
            introduction="La Société de Gestion et d'Exploitation du Backbone National à Fibre Optique (SOGEB) est un "
                         "acteur stratégique au cœur du développement numérique en Guinée.",
            corps=corps(
                section("Qui sommes-nous",
                        "Grâce à son réseau de fibre optique de près de 4 500 km, la SOGEB connecte les 8 gouvernorats, "
                        "les 33 préfectures ainsi que plus de 45 localités à forte importance régionale, facilitant "
                        "l'accès aux services numériques sur l'ensemble du territoire.",
                        "Dotée d'équipements de transmission de dernière génération, la SOGEB garantit des performances "
                        "élevées, une grande fiabilité et une couverture étendue, répondant aux besoins croissants des "
                        "entreprises, des institutions et des opérateurs télécoms.",
                        "En complément de cette infrastructure, la SOGEB dispose d'un data center Tier III, offrant plus "
                        "de 1 000 To de capacité de stockage ainsi qu'une gamme complète de services cloud modernes, "
                        "sécurisés et évolutifs."),
                section("Notre ambition",
                        "Véritable moteur de la transformation digitale, la SOGEB s'impose comme un partenaire de "
                        "confiance pour accompagner la modernisation des services et accélérer la digitalisation en "
                        "République de Guinée."),
            ),
        ))
        backbone = ajouter(accueil, InfrastructurePage(
            title="Backbone national", slug="backbone-national", show_in_menus=True,
            seo_title="Backbone national à fibre optique de Guinée – SOGEB",
            search_description="Le Backbone national exploité par la SOGEB : près de 4 500 km de fibre optique, 62 points "
                               "d'interconnexion et des liaisons vers six pays voisins.",
            introduction="Le Backbone national est le réseau de transport à fibre optique qui relie les grandes villes "
                         "de Guinée entre elles et aux pays voisins.",
            corps=corps(
                ("chiffres", {"titre": "Le réseau en chiffres", "chiffres": [
                    {"valeur": "4 500", "unite": "km", "libelle": "de fibre optique"},
                    {"valeur": "8", "unite": "", "libelle": "gouvernorats"},
                    {"valeur": "33", "unite": "", "libelle": "préfectures"},
                    {"valeur": "6", "unite": "", "libelle": "pays voisins interconnectés"}]}),
                section("Une architecture redondante",
                        "L'infrastructure s'appuie sur une architecture en anneaux redondants (double anneau et "
                        "sous-anneaux), qui assure une haute disponibilité et la continuité du service même en cas "
                        "d'incident. Les équipements critiques sont déployés en configuration redondante 1+1."),
                section("Une énergie sécurisée",
                        "Les sites sont alimentés par une architecture hybride : groupes électrogènes, solutions "
                        "solaires, batteries lithium de 5 à 8 heures d'autonomie et raccordement au réseau EDG. "
                        "L'approvisionnement en carburant est assuré par le service énergie de la SOGEB."),
                section("Sécurité et supervision",
                        "Les sites sont protégés par des agents de sécurité 24 h/24 et 7 j/7. Le réseau est supervisé "
                        "en continu par le NOC, et la sécurité logique repose sur des pare-feu de dernière génération et "
                        "des solutions de protection anti-DDoS."),
                liste("Interconnexions internationales",
                      ["Guinée-Bissau", "Sénégal", "Mali", "Côte d'Ivoire", "Libéria", "Sierra Leone"]),
            ),
        ))
        datacenter = ajouter(accueil, InfrastructurePage(
            title="Data center", slug="data-center", show_in_menus=True,
            seo_title="Data center Tier III en Guinée – SOGEB",
            search_description="Le data center Tier III de la SOGEB : colocation, cloud, hébergement et services "
                               "managés, supervisés 24 h/24 et 7 j/7.",
            introduction="Le data center SOGEB de niveau Tier III est un site sécurisé qui héberge des services "
                         "numériques nécessitant une haute disponibilité.",
            corps=corps(
                section("Des salles sécurisées",
                        "Le data center comprend des salles sécurisées pour les baies et les serveurs, des équipements "
                        "réseau qui les interconnectent, et des infrastructures techniques qui assurent la continuité "
                        "de l'alimentation, le refroidissement et l'accès au réseau très haut débit."),
                section("Sécurité",
                        "Supervision 24 h/24 et 7 j/7, pare-feu et prévention d'intrusion, protection anti-DDoS, "
                        "pare-feu applicatif, accès distant sécurisé et vidéosurveillance."),
                section("Énergie",
                        "Une capacité électrique de 240 kW, une ligne EDG avec transformateur dédié, deux groupes "
                        "électrogènes de 1 100 kVA et des onduleurs pour garantir la continuité du service."),
                section("Supervision",
                        "Le NOC supervise l'énergie, l'environnement, les liens, les serveurs et les équipements réseau. "
                        "Le SOC contrôle le trafic et prévient les intrusions."),
            ),
        ))
        services = ajouter(accueil, ServiceIndexPage(
            title="Services", slug="services", show_in_menus=True,
            seo_title="Services de transport et d'hébergement de données – SOGEB",
            search_description="Liaisons louées, capacité internationale, colocation, cloud et services managés : "
                               "les services de la SOGEB pour les opérateurs, entreprises et institutions.",
            introduction="La SOGEB propose des services de transport de données sur le Backbone national et "
                         "d'hébergement de données dans son data center. Les conditions et tarifs sont communiqués sur demande.",
        ))
        for pilier, titre, slug, resume, publics, blocs in SERVICES:
            services.add_child(instance=ServicePage(
                title=titre, slug=slug, pilier=pilier, resume=resume, publics=publics, corps=corps(*blocs),
                search_description=resume[:155],
            ))
        ajouter(accueil, NewsIndexPage(
            title="Actualités", slug="actualites", show_in_menus=True,
            seo_title="Actualités et communiqués – SOGEB",
            search_description="Les actualités, communiqués et la vie de l'entreprise SOGEB.",
            introduction="Les actualités, communiqués et événements de la SOGEB.",
        ))
        medias = MediaPage(
            title="Documents et médias", slug="documents-medias", show_in_menus=True,
            search_description="Documents publics et photothèque de la SOGEB.",
            introduction="Documents publics à télécharger et photographies des infrastructures et des équipes.",
        )
        accueil.add_child(instance=medias)
        medias.unpublish()  # publiée quand des documents et photos validés seront ajoutés
        contact = ContactPage(
            title="Contact", slug="contact", show_in_menus=True,
            seo_title="Contacter la SOGEB",
            search_description="Coordonnées de la SOGEB et formulaire de contact pour toute demande d'information ou d'offre.",
            introduction="Pour toute demande d'information ou d'offre, contactez-nous par téléphone, par courriel ou "
                         "à l'aide du formulaire ci-dessous.",
            to_address="", from_address="", subject="Nouveau message depuis le site SOGEB",
        )
        accueil.add_child(instance=contact)
        champs = [
            ("Nom et prénom", "singleline", True, ""),
            ("Organisation", "singleline", False, ""),
            ("Courriel", "email", True, ""),
            ("Téléphone", "singleline", False, ""),
            ("Objet de la demande", "dropdown", True,
             "Demande d'information\nDemande d'offre – Backbone\nDemande d'offre – Data center\nPartenariat\nAutre"),
            ("Message", "multiline", True, ""),
        ]
        for i, (label, type_, requis, choix) in enumerate(champs):
            FormField.objects.create(page=contact, sort_order=i, label=label, field_type=type_, required=requis, choices=choix)

        for titre, slug in [("Mentions légales", "mentions-legales"), ("Politique de confidentialité", "confidentialite")]:
            page = StandardPage(title=titre, slug=slug,
                                introduction="À compléter avec les informations légales validées (raison sociale, RCCM, "
                                             "directeur de la publication, hébergeur).")
            accueil.add_child(instance=page)
            page.unpublish()  # brouillon : publié une fois les informations légales fournies

        accueil.bouton_page = services
        accueil.backbone_page = backbone
        accueil.datacenter_page = datacenter
        accueil.save_revision().publish()
        return accueil

    # ------------------------------------------------------------------ rôles
    def creer_roles(self, accueil):
        acces_admin = Permission.objects.get(content_type__app_label="wagtailadmin", codename="access_admin")

        def perm(app, codename):
            return Permission.objects.get(content_type__app_label=app, codename=codename)

        editeurs, _ = Group.objects.get_or_create(name="Éditeurs")
        contributeurs, _ = Group.objects.get_or_create(name="Contributeurs")
        for groupe in (editeurs, contributeurs):
            groupe.permissions.add(acces_admin)

        # Pages : le contributeur rédige, l'éditeur publie
        for code in ["add_page", "change_page"]:
            GroupPagePermission.objects.get_or_create(group=contributeurs, page=accueil, permission=perm("wagtailcore", code))
        for code in ["add_page", "change_page", "publish_page", "lock_page", "unlock_page", "bulk_delete_page"]:
            GroupPagePermission.objects.get_or_create(group=editeurs, page=accueil, permission=perm("wagtailcore", code))

        # Images et documents
        racine = Collection.get_first_root_node()
        for code, app in [("add_image", "wagtailimages"), ("choose_image", "wagtailimages"),
                          ("add_document", "wagtaildocs"), ("choose_document", "wagtaildocs")]:
            for groupe in (editeurs, contributeurs):
                GroupCollectionPermission.objects.get_or_create(group=groupe, collection=racine, permission=perm(app, code))
        for code, app in [("change_image", "wagtailimages"), ("delete_image", "wagtailimages"),
                          ("change_document", "wagtaildocs"), ("delete_document", "wagtaildocs")]:
            GroupCollectionPermission.objects.get_or_create(group=editeurs, collection=racine, permission=perm(app, code))

        # Paramètres du site, chiffres clés, valeurs, redirections : éditeurs uniquement
        editeurs.permissions.add(
            perm("core", "change_sitesettings"),
            *[perm("core", f"{a}_{m}") for m in ("chiffrecle", "valeur") for a in ("add", "change", "delete", "view")],
            *[perm("wagtailredirects", f"{a}_redirect") for a in ("add", "change", "delete")],
        )

        # Circuit de validation : toute modification soumise doit être approuvée par un éditeur
        tache = GroupApprovalTask.objects.create(name="Relecture par la communication")
        tache.groups.set([editeurs])
        workflow = Workflow.objects.create(name="Validation communication")
        WorkflowTask.objects.create(workflow=workflow, task=tache.task_ptr, sort_order=0)
        WorkflowPage.objects.update_or_create(page=accueil, defaults={"workflow": workflow})
