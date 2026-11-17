import re

from django.db import migrations

ANCIEN = "fournisseurs d'accès Internet"


def nouveaux_publics(publics):
    """« FAI » juste après les opérateurs, comme demandé par la communication."""
    if not publics or re.search(r"\bFAI\b", publics):
        return publics
    if ANCIEN in publics:
        return publics.replace(ANCIEN, "FAI")
    # « …, opérateurs » ou « Opérateurs, … » : on insère « FAI » juste après.
    return re.sub(r"\b([Oo]pérateurs(?: de télécommunications)?)\b", r"\1, FAI", publics, count=1)


def appliquer(apps, schema_editor):
    ServicePage = apps.get_model("services", "ServicePage")
    Revision = apps.get_model("wagtailcore", "Revision")
    for page in ServicePage.objects.all():
        nouveau = nouveaux_publics(page.publics)
        if nouveau == page.publics:
            continue
        page.publics = nouveau
        page.save(update_fields=["publics"])
        # L'administration affiche la dernière révision : on la met à jour aussi.
        rev = Revision.objects.filter(pk=page.latest_revision_id).first() if page.latest_revision_id else None
        if rev and isinstance(rev.content, dict) and "publics" in rev.content:
            rev.content["publics"] = nouveaux_publics(rev.content["publics"])
            rev.save(update_fields=["content"])


class Migration(migrations.Migration):
    dependencies = [
        ("services", "0002_alter_servicepage_corps"),
        ("wagtailcore", "0097_baselogentry_uuid_action_timestamp_indexes"),
    ]
    operations = [migrations.RunPython(appliquer, migrations.RunPython.noop)]
