# Generated by Django 3.1.7 on 2022-09-02 22:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0002_auto_20220902_1639'),
    ]

    operations = [
        migrations.AddField(
            model_name='connectionstudies',
            name='title',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='consultancies',
            name='title',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='electricalstudies',
            name='title',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='marketstudies',
            name='title',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='protectioncoordinationstudies',
            name='title',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
