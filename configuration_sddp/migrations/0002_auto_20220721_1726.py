# Generated by Django 3.1.7 on 2022-07-21 22:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('configuration_sddp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='file',
            field=models.FileField(upload_to='uploads/'),
        ),
    ]