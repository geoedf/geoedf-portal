# Generated by Django 3.2.16 on 2023-09-24 23:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myportal', '0004_auto_20230506_2245'),
    ]

    operations = [
        migrations.CreateModel(
            name='FileInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('path', models.URLField()),
                ('info', models.CharField(max_length=255)),
            ],
        ),
    ]
