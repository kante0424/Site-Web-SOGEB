import json
import uuid

from django.db import migrations

ACCROCHE = "Le réseau qui *relie* la Guinée"
ANCIENNE_ACCROCHE = "L'infrastructure numérique nationale au service de la connectivité de la Guinée"
MISSIONS = [
    ("reglages", "Gérer", "Assurer la gestion du Backbone national à fibre optique, infrastructure publique de l'État."),
    ("activite", "Exploiter", "Exploiter et maintenir le réseau et le data center pour garantir leur disponibilité."),
    ("poignee", "Commercialiser", "Proposer les capacités du réseau aux opérateurs, FAI, entreprises et institutions."),
    ("globe", "Connecter", "Relier les régions de Guinée entre elles et aux pays voisins par la fibre optique."),
]


def remplir(apps, schema_editor):
    """Met à jour une page d'accueil existante, sans toucher aux textes déjà modifiés par la communication."""
    HomePage = apps.get_model("home", "HomePage")
    Revision = apps.get_model("wagtailcore", "Revision")
    for page in HomePage.objects.all():
        modifie = False
        if page.accroche == ANCIENNE_ACCROCHE:
            page.accroche = ACCROCHE
            modifie = True
        if not page.missions.raw_data:
            page.missions = [
                {"type": "mission", "value": {"icone": i, "titre": t, "texte": x}, "id": str(uuid.uuid4())}
                for i, t, x in MISSIONS
            ]
            modifie = True
        if modifie:
            page.save(update_fields=["accroche", "missions"])
            # L'administration affiche la dernière révision : on la met à jour aussi.
            if page.latest_revision_id:
                rev = Revision.objects.filter(pk=page.latest_revision_id).first()
                if rev and isinstance(rev.content, dict):
                    if rev.content.get("accroche") == ANCIENNE_ACCROCHE:
                        rev.content["accroche"] = ACCROCHE
                    if not rev.content.get("missions") or rev.content.get("missions") in ("[]", []):
                        rev.content["missions"] = json.dumps(list(page.missions.raw_data))
                    rev.save(update_fields=["content"])


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0002_accueil_surtitre_missions"),
        ("wagtailcore", "0097_baselogentry_uuid_action_timestamp_indexes"),
    ]
    operations = [migrations.RunPython(remplir, migrations.RunPython.noop)]
