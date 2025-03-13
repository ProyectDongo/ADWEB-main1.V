from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

class RegistroEntrada(models.Model):
    METODOS_REGISTRO = [
        ('firma', 'Firma Digital'),
        ('huella', 'Huella Digital'),
        ('geo', 'Geolocalización'),
    ]
    
    trabajador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='entradas'
    )
    metodo = models.CharField(max_length=20, choices=METODOS_REGISTRO,default='firma')
    hora_entrada = models.DateTimeField(auto_now_add=True)
    hora_salida = models.DateTimeField(null=True, blank=True)
    
    # Campos específicos por método
    latitud = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitud = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    firma_digital = models.ImageField(upload_to='firmas/', null=True, blank=True)
    huella_id = models.CharField(max_length=100, null=True, blank=True)

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