# Generated by Django 3.1.7 on 2021-10-26 23:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('budgeted_hours', '0010_auto_20211021_1744'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Versions',
            new_name='CategoriesVersions',
        ),
        migrations.RenameField(
            model_name='hours',
            old_name='version',
            new_name='category_version',
        ),
    ]