# Generated by Django 3.1.7 on 2021-09-16 21:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('budgeted_hours', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BudgetedHoursHistoryData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=15)),
                ('value', models.IntegerField(blank=True, default=0, null=True)),
                ('additional_costs', models.IntegerField(blank=True, default=0, null=True)),
                ('budgeted_hours_history', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='budgeted_hours.budgetedhourshistory')),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='budgeted_hours.client')),
            ],
            options={
                'verbose_name': 'Budgeted Hours History Data',
                'ordering': ['-id'],
            },
        ),
    ]
