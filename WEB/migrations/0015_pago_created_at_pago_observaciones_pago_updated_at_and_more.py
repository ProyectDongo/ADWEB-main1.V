# Generated by Django 5.1.5 on 2025-03-03 13:19

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WEB', '0014_emailnotification'),
    ]

    operations = [
        migrations.AddField(
            model_name='pago',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='pago',
            name='observaciones',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='pago',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='pago',
            name='metodo',
            field=models.CharField(choices=[('automatico', 'Automático'), ('cheque', 'Cheque'), ('tarjeta', 'Tarjeta'), ('credito', 'Crédito'), ('debito', 'Débito'), ('abono', 'Abono'), ('efectivo', 'Efectivo'), ('cobranza', 'Cobranza')], max_length=20),
        ),
        migrations.CreateModel(
            name='HistorialPagos',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateTimeField(auto_now_add=True)),
                ('descripcion', models.TextField()),
                ('pago', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='historial', to='WEB.pago')),
                ('usuario', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
