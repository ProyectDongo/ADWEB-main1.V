# Generated by Django 5.1.5 on 2025-02-10 14:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WEB', '0011_historialcambios'),
    ]

    operations = [
        migrations.AddField(
            model_name='vigenciaplan',
            name='codigo_plan',
            field=models.CharField(default=1000, max_length=20, unique=True),
            preserve_default=False,
        ),
    ]
