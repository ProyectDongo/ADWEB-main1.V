# Generated by Django 5.1.5 on 2025-03-17 13:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('WEB', '0012_alter_registroempresas_options_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cobro',
            name='vigencias_planes',
        ),
    ]
