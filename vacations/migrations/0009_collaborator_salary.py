# Generated by Django 3.1.7 on 2021-12-22 19:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vacations', '0008_merge_20211222_1429'),
    ]

    operations = [
        migrations.AddField(
            model_name='collaborator',
            name='salary',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
