from django.db.models.signals import post_save
from django.dispatch import receiver
from ModuloAsistencia.models import *
from django.utils import timezone
from datetime import datetime, timedelta
import threading

# Crear un objeto thread-local para almacenar el estado
thread_local = threading.local()

@receiver(post_save, sender=RegistroEntrada)
def calcular_retraso_y_horas_extra(sender, instance, created, **kwargs):
    # Verificar si ya estamos dentro del manejador de señales
    if getattr(thread_local, 'inside_signal', False):
        return  # Salir si ya estamos en una llamada recursiva
    
    # Realizar los cálculos
    if instance.trabajador.horario:
        horario = instance.trabajador.horario
        local_tz = timezone.get_current_timezone()
        hora_entrada_local = instance.hora_entrada.astimezone(local_tz)
        entry_date = hora_entrada_local.date()
        
        expected_entry_time = horario.hora_entrada
        expected_entry_dt = datetime.combine(entry_date, expected_entry_time)
        expected_entry_dt = timezone.make_aware(expected_entry_dt, local_tz)
        tolerance_retraso = horario.tolerancia_retraso
        limit_entry_dt = expected_entry_dt + timedelta(minutes=tolerance_retraso)
        
        if hora_entrada_local > limit_entry_dt:
            instance.es_retraso = True
            delta = hora_entrada_local - expected_entry_dt
            instance.minutos_retraso = int(delta.total_seconds() / 60)
        else:
            instance.es_retraso = False
            instance.minutos_retraso = 0
        
        if instance.hora_salida:
            hora_salida_local = instance.hora_salida.astimezone(local_tz)
            expected_exit_time = horario.hora_salida
            if expected_exit_time < expected_entry_time:
                expected_exit_dt = datetime.combine(entry_date + timedelta(days=1), expected_exit_time)
            else:
                expected_exit_dt = datetime.combine(entry_date, expected_exit_time)
            expected_exit_dt = timezone.make_aware(expected_exit_dt, local_tz)
            tolerance_extra = horario.tolerancia_horas_extra
            limit_exit_dt = expected_exit_dt + timedelta(minutes=tolerance_extra)
            
            if hora_salida_local > limit_exit_dt:
                instance.es_horas_extra = True
                delta = hora_salida_local - expected_exit_dt
                instance.minutos_horas_extra = int(delta.total_seconds() / 60)
            else:
                instance.es_horas_extra = False
                instance.minutos_horas_extra = 0
        else:
            instance.es_horas_extra = False
            instance.minutos_horas_extra = 0
    else:
        instance.es_retraso = False
        instance.minutos_retraso = 0
        instance.es_horas_extra = False
        instance.minutos_horas_extra = 0
    
    # Establecer la bandera antes de guardar
    thread_local.inside_signal = True
    try:
        # Guardar los campos calculados
        instance.save(update_fields=['es_retraso', 'minutos_retraso', 'es_horas_extra', 'minutos_horas_extra'])
    finally:
        # Restablecer la bandera después de guardar
        thread_local.inside_signal = False