# Generated by Django 3.1.7 on 2022-07-21 23:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('configuration_sddp', '0003_auto_20220721_1731'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='file',
            field=models.FileField(upload_to='static/static/configuration_sddp'),
        ),
    ]
