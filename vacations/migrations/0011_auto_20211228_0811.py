# Generated by Django 3.1.7 on 2021-12-28 13:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('vacations', '0010_auto_20211222_1437'),
    ]

    operations = [
        migrations.AlterField(
            model_name='requests',
            name='final_acceptor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='final_acceptor', to='vacations.collaborator'),
        ),
        migrations.AlterField(
            model_name='requests',
            name='leader',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='leader', to='vacations.collaborator'),
        ),
        migrations.AlterField(
            model_name='requests',
            name='request_completed',
            field=models.BooleanField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='settings',
            name='final_acceptor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='vacations.collaborator'),
        ),
    ]
