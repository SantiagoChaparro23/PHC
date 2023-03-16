# Generated by Django 3.1.7 on 2022-02-28 18:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('imports', '0011_auto_20211030_1731'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='commercialdemandnotregulatedbyciiu',
            name='unique_CommercialDemandNotRegulatedByCIIU',
        ),
        migrations.AddConstraint(
            model_name='commercialdemandnotregulatedbyciiu',
            constraint=models.UniqueConstraint(fields=('date', 'ciiu', 'subactivity'), name='unique_CommercialDemandNotRegulatedByCIIU'),
        ),
    ]
