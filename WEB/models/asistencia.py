import datetime
from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

class RegistroEntrada(models.Model):
    """
    Modelo que representa el registro de entrada y salida de un trabajador.

    Este modelo almacena la hora en la que un trabajador inicia y finaliza su jornada,
    y permite indicar si se permite registrar otra entrada (por ejemplo, en caso de turnos múltiples).

    Atributos:
        trabajador (ForeignKey): Relación con el usuario (trabajador) que realiza el registro.
                                  Se asocia mediante settings.AUTH_USER_MODEL y se elimina en cascada.
        hora_entrada (DateTimeField): Fecha y hora en que se registra la entrada.
                                      Se asigna automáticamente al crearse el registro.
        hora_salida (DateTimeField): Fecha y hora en que se registra la salida. Es opcional.
        permitir_otra_entrada (BooleanField): Indica si se permite registrar otra entrada para el mismo trabajador.
    """
    trabajador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='entradas'
    )
    hora_entrada = models.DateTimeField(auto_now_add=True)
    hora_salida = models.DateTimeField(null=True, blank=True)
    permitir_otra_entrada = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Registro de Entrada"
        verbose_name_plural = "Registros de Entrada"
        ordering = ['-hora_entrada']

    def __str__(self):
        """
        Retorna una representación en cadena del registro de entrada.

        :return: Cadena con el formato "username - AAAA-MM-DD HH:MM", donde 'username' es el nombre
                 de usuario del trabajador y la fecha/hora corresponde a 'hora_entrada'.
        """
        return f"{self.trabajador.username} - {self.hora_entrada.strftime('%Y-%m-%d %H:%M')}"


@receiver(post_save, sender=RegistroEntrada)
def notificar_registro_entrada(sender, instance, created, **kwargs):
    """
    Función receptora para la señal post_save del modelo RegistroEntrada.

    Cuando se crea un nuevo registro de entrada, esta función notifica (mediante un print)
    que se ha registrado la entrada para el trabajador asociado, mostrando el nombre de usuario
    y la hora de entrada.

    Parámetros:
        sender: La clase del modelo que envió la señal (RegistroEntrada).
        instance: La instancia del modelo RegistroEntrada que se acaba de guardar.
        created (bool): Indica si la instancia fue creada (True) o actualizada (False).
        **kwargs: Argumentos adicionales de la señal.
    """
    if created:
        print(f"Entrada registrada para {instance.trabajador.username} a las {instance.hora_entrada}")