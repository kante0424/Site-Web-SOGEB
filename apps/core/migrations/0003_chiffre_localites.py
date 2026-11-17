from django.db import migrations

LIBELLE = "localités d'importance économique"


def ajouter(apps, schema_editor):
    """Ajoute « plus de 45 localités d'importance économique » juste après les 33 préfectures, si absent."""
    ChiffreCle = apps.get_model("core", "ChiffreCle")
    if not ChiffreCle.objects.exists() or ChiffreCle.objects.filter(libelle__icontains="localités").exists():
        return
    prefectures = ChiffreCle.objects.filter(libelle__icontains="préfecture").first()
    rang = prefectures.ordre + 1 if prefectures else ChiffreCle.objects.count()
    for c in ChiffreCle.objects.filter(ordre__gte=rang).exclude(pk=getattr(prefectures, "pk", None)):
        c.ordre += 1
        c.save(update_fields=["ordre"])
    ChiffreCle.objects.create(valeur="+45", unite="", libelle=LIBELLE, ordre=rang)


class Migration(migrations.Migration):
    dependencies = [("core", "0002_mission_vision")]
    operations = [migrations.RunPython(ajouter, migrations.RunPython.noop)]
