# Generated by Django 3.1.7 on 2022-03-11 16:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('budgeted_hours', '0022_auto_20220304_1956'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='budgetedhours',
            name='document_url',
        ),
        migrations.RemoveField(
            model_name='budgetedhours',
            name='duration_deliverables',
        ),
        migrations.RemoveField(
            model_name='budgetedhours',
            name='start_at',
        ),
    ]