# Generated by Django 3.1.7 on 2022-02-25 23:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('budgeted_hours', '0020_auto_20220225_1804'),
    ]

    operations = [
        migrations.RenameField(
            model_name='budgetedhours',
            old_name='start_project_at',
            new_name='start_at',
        ),
    ]
