# your_app/utils.py
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from WEB.models.gestion_administrativa.empresa import  RegistroEmpresas, VigenciaPlan
from WEB.models.gestion_administrativa.transacciones import  Pago, Cobro
from django.db.models import Sum

def hay_pagos_atrasados(empresa, vigencia_plan):
    # Obtener todos los cobros pendientes para esta vigencia
    cobros_pendientes = Cobro.objects.filter(
        vigencia_plan=vigencia_plan,
        estado='pendiente'
    )
    
    # Iterar sobre cada cobro pendiente
    for cobro in cobros_pendientes:
        # Verificar si el cobro tiene fecha_fin definida
        if cobro.fecha_fin:
            # Calcular la fecha límite (fecha_fin + 5 días)
            fecha_limite = cobro.fecha_fin + relativedelta(days=5)
            # Si la fecha actual es posterior a la fecha límite
            if timezone.now().date() > fecha_limite:
                # Calcular el total de pagos asociados a este cobro
                pagos_total = Pago.objects.filter(cobro=cobro).aggregate(total=Sum('monto'))['total'] or 0
                # Si el total de pagos es menor al monto del cobro, hay atraso
                if pagos_total < cobro.monto_total:
                    return True
    
    # Si no hay cobros atrasados, retornar False
    return False