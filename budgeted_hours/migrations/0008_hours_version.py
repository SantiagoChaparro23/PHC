# Generated by Django 3.1.7 on 2021-10-21 16:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('budgeted_hours', '0007_auto_20211021_1141'),
    ]

    operations = [
        migrations.AddField(
            model_name='hours',
            name='version',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='budgeted_hours.versions'),
            preserve_default=False,
        ),
    ]