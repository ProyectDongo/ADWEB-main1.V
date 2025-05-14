from WEB.models import *
from django.shortcuts import render, redirect
from WEB.views.scripts import *
from django.contrib.auth.decorators import login_required
from django.db.models.functions import TruncMonth
from django.db.models import Count, Sum
from datetime import datetime
import pytz
from collections import defaultdict
from django.conf import settings


@login_required
@permiso_requerido("WEB.vista_estadisticas")
def home_estadisticas(request):
    return render(request, 'admin/estadisticas/home/home.html')




@login_required
@permiso_requerido("WEB.vista_estadisticas")
def estadisticas_empresas(request):
    empresas_por_mes = RegistroEmpresas.objects.annotate(
        mes=TruncMonth('fecha_ingreso')
    ).values('mes').annotate(
        total=Count('id')
    ).order_by('mes')
    context = {
        'empresas_por_mes': list(empresas_por_mes),
    }
    return render(request, 'admin/estadisticas/empresas/empresas.html', context)






@login_required
@permiso_requerido("WEB.vista_estadisticas")
def estadisticas_pagos(request):
    # Obtener la zona horaria desde los ajustes
    tz = pytz.timezone(settings.TIME_ZONE)
    
    # Recuperar todos los pagos
    pagos = Pago.objects.all()
    
    # Diccionario para agrupar pagos por mes
    pagos_por_mes = defaultdict(lambda: {'cantidad': 0, 'monto_total': 0})
    
    # Procesar cada pago
    for pago in pagos:
        # Convertir fecha_pago de UTC a la zona horaria local
        local_fecha = pago.fecha_pago.astimezone(tz)
        # Crear clave basada en año y mes local
        key = (local_fecha.year, local_fecha.month)
        pagos_por_mes[key]['cantidad'] += 1
        pagos_por_mes[key]['monto_total'] += float(pago.monto)
    
    # Preparar lista para la plantilla
    pagos_list = []
    for (year, month), data in pagos_por_mes.items():
        # Crear objeto datetime para el primer día del mes en la zona horaria local
        mes_date = datetime(year, month, 1, tzinfo=tz)
        pagos_list.append({
            'mes': mes_date.isoformat(),  # Formato ISO: 'YYYY-MM-DDTHH:MM:SS-03:00'
            'cantidad': data['cantidad'],
            'monto_total': data['monto_total']
        })
    
    # Ordenar por mes
    pagos_list.sort(key=lambda x: x['mes'])
    
    # Contexto para la plantilla
    context = {
        'pagos_por_mes': pagos_list,
    }
    return render(request, 'admin/estadisticas/pagos/pagos.html', context)



