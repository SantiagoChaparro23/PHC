# Generated by Django 3.1.7 on 2022-02-21 12:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('sddp', '0002_auto_20210618_1431'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='Project_created_by', to=settings.AUTH_USER_MODEL),
        ),
    ]
