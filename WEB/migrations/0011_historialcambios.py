# Generated by Django 5.1.5 on 2025-02-07 15:14

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WEB', '0010_alter_registroempresas_codigo_cliente'),
    ]

    operations = [
        migrations.CreateModel(
            name='HistorialCambios',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateTimeField(auto_now_add=True)),
                ('descripcion', models.TextField()),
                ('empresa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='WEB.registroempresas')),
                ('usuario', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Historial de Cambios',
                'ordering': ['-fecha'],
            },
        ),
    ]
