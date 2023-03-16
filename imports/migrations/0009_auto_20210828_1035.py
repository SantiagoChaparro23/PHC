# Generated by Django 3.1.7 on 2021-08-28 15:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('imports', '0008_monthlyreserves_reservoir'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='monthlyreserves',
            constraint=models.UniqueConstraint(fields=('date', 'hydrological_region', 'reservoir'), name='unique_MonthlyReserves'),
        ),
    ]
