# Generated by Django 3.1.7 on 2021-06-23 00:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('imports', '0002_urlsfilesmetrictask'),
    ]

    operations = [
        migrations.AddField(
            model_name='urlsfilesmetrictask',
            name='has_error',
            field=models.BooleanField(default=False),
        ),
    ]
