# Generated by Django 3.1.7 on 2022-06-10 20:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vacations', '0018_auto_20220110_2112'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='collaborator',
            options={'ordering': ['entry_at'], 'verbose_name': 'Collaborator'},
        ),
    ]