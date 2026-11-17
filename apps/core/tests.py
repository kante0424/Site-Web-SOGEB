"""Tests de base : lancer avec « python manage.py test »."""
from django.contrib.auth.models import Group, User
from django.core import mail
from django.core.management import call_command
from django.test import TestCase, override_settings
from wagtail.contrib.forms.models import FormSubmission
from wagtail.models import Page, Workflow

from apps.contact.models import ContactPage


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend", AXES_ENABLED=False)
class SiteTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("initialiser_sogeb", verbosity=0)

    def test_pages_publiques(self):
        for url in ["/", "/la-sogeb/", "/backbone-national/", "/data-center/", "/services/",
                    "/services/liaisons-louees-nationales/", "/actualites/", "/contact/", "/sitemap.xml", "/robots.txt"]:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_brouillons_non_publies(self):
        for url in ["/mentions-legales/", "/confidentialite/", "/documents-medias/"]:
            self.assertEqual(self.client.get(url).status_code, 404)

    def test_un_seul_h1_par_page(self):
        for url in ["/", "/la-sogeb/", "/services/", "/contact/"]:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).content.decode().count("<h1"), 1)

    def test_formulaire_contact(self):
        page = ContactPage.objects.get()
        page.to_address = "communication@example.org"
        page.save_revision().publish()
        donnees = {"nom_et_prenom": "Test", "courriel": "test@example.org",
                   "objet_de_la_demande": "Demande d'information", "message": "Bonjour"}
        reponse = self.client.post("/contact/", donnees)
        self.assertEqual(reponse.status_code, 200)
        self.assertEqual(FormSubmission.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 1)

    def test_champ_piege_bloque_les_robots(self):
        self.client.post("/contact/", {"nom_et_prenom": "Robot", "courriel": "r@example.org",
                                       "objet_de_la_demande": "Autre", "message": "spam", "site_web": "http://spam"})
        self.assertEqual(FormSubmission.objects.count(), 0)

    def test_roles_et_validation(self):
        self.assertTrue(Group.objects.filter(name="Éditeurs").exists())
        self.assertTrue(Group.objects.filter(name="Contributeurs").exists())
        accueil = Page.objects.get(slug="accueil")
        self.assertEqual(accueil.get_workflow(), Workflow.objects.get(name="Validation communication"))

    def test_contributeur_ne_peut_pas_publier(self):
        user = User.objects.create_user("contrib", password="motdepasse-solide-2026")
        user.groups.add(Group.objects.get(name="Contributeurs"))
        page = Page.objects.get(slug="la-sogeb")
        perms = page.permissions_for_user(user)
        self.assertTrue(perms.can_edit())
        self.assertFalse(perms.can_publish())

    def test_missions_et_organigramme(self):
        from apps.pages.models import OrganigrammePage

        call_command("completer_sogeb", verbosity=0)  # relancer ne doit rien dupliquer
        self.assertEqual(OrganigrammePage.objects.count(), 1)
        self.assertEqual(self.client.get("/la-sogeb/missions/").status_code, 200)
        organigramme = OrganigrammePage.objects.get()
        self.assertFalse(organigramme.live)  # brouillon tant que la Direction n'a pas validé
        self.assertEqual(self.client.get("/la-sogeb/organigramme/").status_code, 404)
        organigramme.save_revision().publish()
        reponse = self.client.get("/la-sogeb/organigramme/")
        self.assertContains(reponse, "Direction générale")
        self.assertContains(reponse, "<h1", count=1)
