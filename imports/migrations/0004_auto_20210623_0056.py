# Generated by Django 3.1.7 on 2021-06-23 00:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('imports', '0003_urlsfilesmetrictask_has_error'),
    ]

    operations = [
        migrations.AlterField(
            model_name='urlsfilesmetrictask',
            name='metric',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='imports.metric'),
        ),
    ]
