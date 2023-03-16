# Generated by Django 3.1.7 on 2022-02-07 20:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('budgeted_hours', '0017_auto_20220207_0928'),
    ]

    operations = [
        migrations.AddField(
            model_name='traceabilitybudgetedhourshistory',
            name='stages',
            field=models.IntegerField(choices=[(1, 'En revisión comercial'), (2, 'En revisión técnica'), (3, 'En revisión financiero'), (4, 'Finalizado')], default=1),
        ),
    ]