# Generated by Django 3.1.7 on 2021-09-01 17:14

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Activities',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('activity', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True, max_length=250, null=True)),
            ],
            options={
                'verbose_name': 'Activities',
                'ordering': ['service_type'],
            },
        ),
        migrations.CreateModel(
            name='BudgetedHours',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=15)),
                ('value', models.IntegerField(blank=True, default=0, null=True)),
                ('additional_costs', models.IntegerField(blank=True, default=0, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Budgeted Hours',
                'ordering': ['code'],
            },
        ),
        migrations.CreateModel(
            name='Categories',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(max_length=100)),
            ],
            options={
                'verbose_name': 'Categories',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('client', models.CharField(max_length=100)),
            ],
            options={
                'verbose_name': 'Client',
                'ordering': ['client'],
            },
        ),
        migrations.CreateModel(
            name='Operator',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('operator', models.CharField(max_length=100)),
            ],
            options={
                'verbose_name': 'Operator',
                'ordering': ['operator'],
            },
        ),
        migrations.CreateModel(
            name='ServiceType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('service_type', models.CharField(max_length=100)),
            ],
            options={
                'verbose_name': 'Service type',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Softwares',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('software', models.CharField(max_length=100)),
            ],
            options={
                'verbose_name': 'Softwares',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='TraceabilityBudgetedHours',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sent_at', models.DateTimeField(auto_now_add=True)),
                ('budgeted_hours', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='budgeted_hours.budgetedhours')),
            ],
            options={
                'verbose_name': 'Traceability',
                'ordering': ['budgeted_hours'],
            },
        ),
        migrations.CreateModel(
            name='TraceabilityBudgetedHoursHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reviewed_at', models.DateTimeField(auto_now=True)),
                ('budgeted_hours', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='budgeted_hours.traceabilitybudgetedhours')),
                ('reviewed_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Traceability Budgeted Hours History',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='TemplatesBudgetedHours',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('template_name', models.CharField(max_length=100)),
                ('operator', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='budgeted_hours.operator')),
                ('service_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='budgeted_hours.servicetype')),
            ],
            options={
                'verbose_name': 'Templates',
                'ordering': ['template_name'],
            },
        ),
        migrations.CreateModel(
            name='PriceRequestFormat',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('aa', models.CharField(blank=True, max_length=100, null=True)),
                ('ab', models.CharField(blank=True, max_length=100, null=True)),
                ('ac', models.CharField(blank=True, max_length=100, null=True)),
                ('ad', models.CharField(blank=True, max_length=100, null=True)),
                ('ae', models.CharField(blank=True, max_length=100, null=True)),
                ('af', models.CharField(blank=True, max_length=100, null=True)),
                ('ag', models.CharField(blank=True, max_length=100, null=True)),
                ('ah', models.CharField(blank=True, max_length=100, null=True)),
                ('ai', models.CharField(blank=True, max_length=100, null=True)),
                ('aj', models.CharField(blank=True, max_length=100, null=True)),
                ('ak', models.CharField(blank=True, max_length=100, null=True)),
                ('al', models.CharField(blank=True, max_length=100, null=True)),
                ('am', models.CharField(blank=True, max_length=100, null=True)),
                ('ba', models.IntegerField(blank=True, choices=[(1, 'Sí'), (2, 'No')], null=True)),
                ('bb', models.IntegerField(blank=True, choices=[(1, 'Sí'), (2, 'No')], null=True)),
                ('bc', models.IntegerField(blank=True, choices=[(1, 'Sí'), (2, 'No')], null=True)),
                ('bd', models.IntegerField(blank=True, choices=[(1, 'Sí'), (2, 'No')], null=True)),
                ('be', models.IntegerField(blank=True, choices=[(1, 'Sí'), (2, 'No')], null=True)),
                ('bf', models.IntegerField(blank=True, choices=[(1, 'Sí'), (2, 'No')], null=True)),
                ('bg', models.IntegerField(blank=True, choices=[(1, 'Sí'), (2, 'No')], null=True)),
                ('bh', models.IntegerField(blank=True, choices=[(1, 'Sí'), (2, 'No')], null=True)),
                ('ca', models.IntegerField(blank=True, choices=[(1, 'Sí'), (2, 'No')], null=True)),
                ('cb', models.IntegerField(blank=True, choices=[(1, 'Sí'), (2, 'No')], null=True)),
                ('cc', models.IntegerField(blank=True, choices=[(1, 'Sí'), (2, 'No')], null=True)),
                ('budgeted_hours', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='budgeted_hours.budgetedhours')),
            ],
            options={
                'verbose_name': 'Price Request Format',
                'ordering': ['budgeted_hours'],
            },
        ),
        migrations.CreateModel(
            name='HoursTemplates',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('engineer', models.FloatField(default=0)),
                ('leader', models.FloatField(default=0)),
                ('management', models.FloatField(default=0)),
                ('software_hours', models.FloatField(default=0)),
                ('external', models.FloatField(default=0)),
                ('activity', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='budgeted_hours.activities')),
                ('software', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='budgeted_hours.softwares')),
                ('templates_budgeted_hours', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='budgeted_hours.templatesbudgetedhours')),
            ],
            options={
                'verbose_name': 'Hours Templates',
                'ordering': ['templates_budgeted_hours'],
            },
        ),
        migrations.CreateModel(
            name='Hours',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('engineer', models.FloatField(default=0)),
                ('leader', models.FloatField(default=0)),
                ('management', models.FloatField(default=0)),
                ('software_hours', models.FloatField(default=0)),
                ('external', models.FloatField(default=0)),
                ('version', models.IntegerField(default=1)),
                ('activity', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='budgeted_hours.activities')),
                ('budgeted_hours', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='budgeted_hours.budgetedhours')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='hours', to='budgeted_hours.categories')),
                ('software', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='budgeted_hours.softwares')),
            ],
            options={
                'verbose_name': 'Hours',
                'ordering': ['budgeted_hours'],
            },
        ),
        migrations.CreateModel(
            name='BudgetedHoursHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('budgeted_hours', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='budgeted_hours.budgetedhours')),
                ('updated_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Budgeted Hours History',
                'ordering': ['-id'],
            },
        ),
        migrations.AddField(
            model_name='budgetedhours',
            name='client',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='budgeted_hours.client'),
        ),
        migrations.AddField(
            model_name='budgetedhours',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='budgetedhours',
            name='service_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='budgeted_hours.servicetype'),
        ),
        migrations.AddField(
            model_name='activities',
            name='service_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='budgeted_hours.servicetype'),
        ),
    ]
