# Generated by Django 5.1.5 on 2025-02-21 03:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WEB', '0011_remove_vigenciaplan_activo_alter_vigenciaplan_estado'),
    ]

    operations = [
        migrations.AddField(
            model_name='registroempresas',
            name='eliminada',
            field=models.BooleanField(default=False, verbose_name='Eliminada'),
        ),
    ]
