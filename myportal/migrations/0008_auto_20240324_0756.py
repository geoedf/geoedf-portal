# Generated by Django 3.2.24 on 2024-03-24 07:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myportal', '0007_resource_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='resource',
            name='keywords',
            field=models.CharField(max_length=1024, null=True),
        ),
        migrations.AddField(
            model_name='resource',
            name='publication_type',
            field=models.CharField(default='Geospatial Files', max_length=50),
        ),
    ]