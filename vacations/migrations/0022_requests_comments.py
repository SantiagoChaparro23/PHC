# Generated by Django 3.1.7 on 2022-05-12 02:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vacations', '0021_auto_20220404_1843'),
    ]

    operations = [
        migrations.AddField(
            model_name='requests',
            name='comments',
            field=models.TextField(blank=True, max_length=1000, null=True),
        ),
    ]
