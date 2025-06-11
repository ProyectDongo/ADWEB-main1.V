# your_app/utils.py
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from WEB.models.gestion_administrativa.empresa import  RegistroEmpresas, VigenciaPlan
from WEB.models.gestion_administrativa.transacciones import  Pago

def hay_pagos_atrasados(empresa, vigencia_plan):
    # Obtener el último pago real (monto > 0)
    ultimo_pago = Pago.objects.filter(
        vigencia_planes=vigencia_plan,
        monto__gt=0
    ).order_by('-fecha_pago').first()

    # Establecer la fecha base
    if not ultimo_pago:
        fecha_base = vigencia_plan.fecha_inicio
    else:
        fecha_base = ultimo_pago.fecha_pago.date()

    frecuencia = empresa.frecuencia_pago or 'mensual'

    if frecuencia == 'mensual':
        proxima_fecha_pago = fecha_base + relativedelta(months=1)
    elif frecuencia == 'anual':
        proxima_fecha_pago = fecha_base + relativedelta(years=1)
    else:
        return False

    fecha_limite = proxima_fecha_pago + relativedelta(days=5)

    if timezone.now().date() > fecha_limite:
        hay_pagos_posteriores = Pago.objects.filter(
            vigencia_planes=vigencia_plan,
            fecha_pago__gt=fecha_base,
            monto__gt=0
        ).exists()
        if not hay_pagos_posteriores:
            return True
    return False