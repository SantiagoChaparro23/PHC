# Generated by Django 3.1.7 on 2021-11-26 17:13

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('budgeted_hours', '0012_budgetedhours_description'),
        ('reported_hours', '0006_usertoreport_email'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReportedHours',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('report_date_at', models.DateField()),
                ('time', models.IntegerField()),
                ('description', models.TextField(blank=True, max_length=250, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('activity', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='budgeted_hours.activities')),
                ('code', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='budgeted_hours.budgetedhours')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Reported Hours',
                'ordering': ['code'],
            },
        ),
    ]
