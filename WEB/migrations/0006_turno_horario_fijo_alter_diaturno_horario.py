# Generated by Django 5.1.7 on 2025-06-16 14:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WEB', '0005_remove_turno_dias_descanso_remove_turno_dias_trabajo_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='turno',
            name='horario_fijo',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='WEB.horario'),
        ),
        migrations.AlterField(
            model_name='diaturno',
            name='horario',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='WEB.horario'),
        ),
    ]
