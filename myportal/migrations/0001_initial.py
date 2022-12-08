from django.db import migrations, models


def update_site_forward(apps, schema_editor):
    """
    Write the domain in migrations
    """
    Site = apps.get_model("sites", "Site")
    site = Site.objects.get(id=1)
    site.domain = '127.0.0.1'
    site.name = '127.0.0.1'
    site.save()


class Migration(migrations.Migration):
    dependencies = [
        # ('sites', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(update_site_forward),
    ]
