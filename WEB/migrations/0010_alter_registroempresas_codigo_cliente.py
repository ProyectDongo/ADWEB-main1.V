# Generated by Django 5.1.5 on 2025-02-06 17:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WEB', '0009_alter_registroempresas_vigente'),
    ]

    operations = [
        migrations.AlterField(
            model_name='registroempresas',
            name='codigo_cliente',
            field=models.CharField(max_length=20, unique=True),
        ),
    ]
