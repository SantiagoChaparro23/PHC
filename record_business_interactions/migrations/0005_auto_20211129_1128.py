# Generated by Django 3.1.7 on 2021-11-29 16:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('record_business_interactions', '0004_settings'),
    ]

    operations = [
        migrations.AlterField(
            model_name='visitrecord',
            name='phc_code',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
