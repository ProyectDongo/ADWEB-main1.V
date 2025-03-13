# Generated by Django 5.1.5 on 2025-03-13 17:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WEB', '0007_alter_pago_options_alter_plan_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='registroentrada',
            options={},
        ),
        migrations.RemoveField(
            model_name='registroentrada',
            name='permitir_otra_entrada',
        ),
        migrations.AddField(
            model_name='registroentrada',
            name='firma_digital',
            field=models.ImageField(blank=True, null=True, upload_to='firmas/'),
        ),
        migrations.AddField(
            model_name='registroentrada',
            name='huella_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='registroentrada',
            name='latitud',
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True),
        ),
        migrations.AddField(
            model_name='registroentrada',
            name='longitud',
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True),
        ),
        migrations.AddField(
            model_name='registroentrada',
            name='metodo',
            field=models.CharField(choices=[('firma', 'Firma Digital'), ('huella', 'Huella Digital'), ('geo', 'Geolocalización')], default='firma', max_length=20),
        ),
    ]
