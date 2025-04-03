from django.db import models
#from django.contrib.gis.db import models 
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from WEB.models import RegistroEmpresas



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

    metodo = models.CharField(max_length=20, choices=METODOS_REGISTRO)
    hora_entrada = models.DateTimeField(auto_now_add=True)
    hora_salida = models.DateTimeField(null=True, blank=True)
    latitud = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitud = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    firma_digital = models.TextField(null=True, blank=True)
    huella_id = models.CharField(max_length=100, null=True, blank=True)

    huella_validada = models.BooleanField(default=False)

    empresa = models.ForeignKey(RegistroEmpresas, on_delete=models.CASCADE, related_name='registros_asistencia',null=True, blank=True)

    #ubicacion = models.PointField(srid=4326, null=True, blank=True)
    precision = models.FloatField(null=True, blank=True)  # Precisión en metros

    class Meta:
        permissions = [
            ('registro_asistencia', 'Acceso al módulo de asistencia'),
        ]
    def esta_dentro_rango(self, empresa):
        if not self.ubicacion or not empresa.radio_permitido:
            return False
            
        return self.ubicacion.distance(empresa.ubicacion_central) * 100000 <= empresa.radio_permitido
    
    def clean(self):
        # Solo validar para nuevas entradas (creación)
        if not self.pk:  
            if self.empresa is None:
                raise ValidationError("Debe asociar una empresa al registro de entrada.")
            
            # Validación del plan solo aplica a nuevas entradas
            tiene_plan_asistencia = self.empresa.vigencias.filter(
                plan__nombre__iexact='asistencia',
                estado='indefinido'
            ).exists()
            
            if not tiene_plan_asistencia:
                raise ValidationError("La empresa no tiene un plan de asistencia activo")
            
            if self.empresa.usuarios.count() >= self.empresa.limite_usuarios:
                raise ValidationError("Límite de usuarios excedido para este plan")
            
    def save(self, *args, **kwargs):
        self.empresa = self.trabajador.empresa
        super().save(*args, **kwargs)
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
#_________________________________________________________________________________________________
