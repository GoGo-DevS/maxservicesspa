from django.db import migrations

GRUPOS = ("Panel cotizaciones", "Responde cotizaciones")


def crear(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    for nombre in GRUPOS:
        Group.objects.get_or_create(name=nombre)


def nada(apps, schema_editor):
    """Al revertir no se borran grupos: pueden tener personas adentro."""


class Migration(migrations.Migration):
    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        ("cotizaciones", "0001_inicial"),
    ]

    operations = [migrations.RunPython(crear, nada)]
