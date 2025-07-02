
from django.utils import timezone
from datetime import timedelta, datetime


def calcular_retraso(entrada, horario):
    entrada_time = entrada.hora_entrada.time()
    scheduled_start = horario.hora_entrada
    tolerance = timedelta(minutes=horario.tolerancia_retraso)
    scheduled_start_dt = timezone.make_aware(datetime.combine(entrada.hora_entrada.date(), scheduled_start))
    if entrada.hora_entrada > scheduled_start_dt + tolerance:
        entrada.es_retraso = True
        retraso = (entrada.hora_entrada - scheduled_start_dt).total_seconds() / 60
        entrada.minutos_retraso = int(retraso)




def calcular_horas_extra(entrada, horario):
    if entrada.hora_salida:
        scheduled_end = datetime.combine(entrada.hora_entrada.date(), horario.hora_salida)
        scheduled_end = timezone.make_aware(scheduled_end)
        tolerance_extra = timedelta(minutes=horario.tolerancia_horas_extra)
        if entrada.hora_salida > scheduled_end + tolerance_extra:
            entrada.es_horas_extra = True
            extra = (entrada.hora_salida - scheduled_end).total_seconds() / 60
            entrada.minutos_horas_extra = int(extra)