# Generated by Django 3.1.7 on 2021-12-30 22:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('vacations', '0014_auto_20211228_2205'),
    ]

    operations = [
        migrations.AlterField(
            model_name='settings',
            name='final_acceptor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
