# Generated by Django 3.1.7 on 2022-11-29 20:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('budgeted_hours', '0025_budgetedhours_compromise_delivery_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='budgetedhours',
            name='category_version',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='budgeted_hours.categoriesversions'),
        ),
    ]
