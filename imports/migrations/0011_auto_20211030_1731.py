# Generated by Django 3.1.7 on 2021-10-30 17:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('imports', '0010_auto_20210828_1037'),
    ]

    operations = [
        migrations.AlterField(
            model_name='urlsfilesmetric',
            name='last_update',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
