# Generated by Django 3.2.16 on 2023-11-20 08:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myportal', '0005_fileinfo'),
    ]

    operations = [
        migrations.AddField(
            model_name='resource',
            name='description',
            field=models.CharField(max_length=1024, null=True),
        ),
        migrations.AddField(
            model_name='resource',
            name='extra_info',
            field=models.CharField(max_length=1024, null=True),
        ),
    ]