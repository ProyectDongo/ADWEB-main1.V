# Generated by Django 5.1.7 on 2025-07-02 16:15

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('WEB', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Cobro',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ultima_actualizacion', models.DateTimeField(auto_now=True)),
                ('monto_total', models.DecimalField(decimal_places=2, max_digits=10)),
                ('fecha_inicio', models.DateField()),
                ('fecha_fin', models.DateField()),
                ('estado', models.CharField(choices=[('pendiente', 'Pendiente'), ('pagado', 'Pagado')], default='pendiente', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('empresa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cobros', to='WEB.registroempresas')),
                ('vigencia_plan', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='cobros_relacionados', to='WEB.vigenciaplan')),
                ('vigencias_planes', models.ManyToManyField(blank=True, related_name='cobros_planes', to='WEB.vigenciaplan')),
            ],
        ),
        migrations.CreateModel(
            name='Pago',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('monto', models.DecimalField(decimal_places=2, max_digits=10)),
                ('fecha_pago', models.DateTimeField()),
                ('metodo', models.CharField(choices=[('automatico', 'Automático'), ('cheque', 'Cheque'), ('tarjeta', 'Tarjeta'), ('credito', 'Crédito'), ('debito', 'Débito'), ('abono', 'Abono'), ('efectivo', 'Efectivo')], max_length=20)),
                ('comprobante', models.FileField(blank=True, null=True, upload_to='comprobantes/')),
                ('pagado', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('observaciones', models.TextField(blank=True, null=True)),
                ('cobro', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='pagos', to='transacciones.cobro')),
                ('empresa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pagos', to='WEB.registroempresas')),
                ('vigencia_planes', models.ManyToManyField(related_name='pagos_asociados', to='WEB.vigenciaplan')),
            ],
            options={
                'permissions': [('Registrar_pago', 'permite registar un pago')],
            },
        ),
        migrations.CreateModel(
            name='HistorialPagos',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateTimeField(auto_now_add=True)),
                ('descripcion', models.TextField()),
                ('usuario', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('pago', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='historial', to='transacciones.pago')),
            ],
        ),
    ]
