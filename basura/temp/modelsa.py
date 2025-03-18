
from math import perm
from django.db import models
from WEB.models.ubicacion.region import Region, Provincia, Comuna
from WEB.views.scripts  import *
from django.utils import timezone



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
    firma_digital = models.ImageField(upload_to='firmas/', null=True, blank=True)
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
        if not self.empresa.vigencia_plan.plan.nombre.lower() == 'asistencia':
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


#-----------------------------------------------------------------------------------------------------------------
class Cobro(models.Model):
    empresa = models.ForeignKey(RegistroEmpresas, on_delete=models.CASCADE, related_name='cobros')
    vigencia_plan = models.ForeignKey(
        VigenciaPlan, 
        on_delete=models.CASCADE, 
        related_name='cobros_relacionados',  # Cambiado para evitar conflicto de nombres
        null=True, 
        blank=True
    )
    # Agregar campo ManyToMany para asociar múltiples planes
    vigencias_planes = models.ManyToManyField(  
        VigenciaPlan, 
        related_name='cobros_planes',
        blank=True
    )
    ultima_actualizacion = models.DateTimeField(auto_now=True)
    
    def planes_asociados(self):
        if self.vigencia_plan:
            return [self.vigencia_plan]
        return self.vigencias_planes.all()
    
    monto_total = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    estado = models.CharField(
        max_length=20,
        choices=[('pendiente', 'Pendiente'), ('pagado', 'Pagado')],
        default='pendiente'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def monto_pagado(self):
        return self.pagos.aggregate(total=Sum('monto'))['total'] or 0

    def monto_restante(self):
        return self.monto_total - self.monto_pagado()
    
    def actualizar_estado(self):
        if self.monto_restante() <= 0:
            self.estado = 'pagado'
            self.save()

    def __str__(self):
        return f"Cobro {self.id} - {self.vigencia_plan.plan.nombre if self.vigencia_plan else 'Todos'}"
#---------------------------------------------------------------------------------------------------------------------------

class Pago(models.Model):
    """
    Modelo que representa un pago realizado por una empresa.
    Se registran distintos métodos de pago (incluyendo abono y cobranza) y se añaden
    campos de auditoría y observaciones para un registro detallado.
    """
    METODO_PAGO_CHOICES = [
        ('automatico', 'Automático'),
        ('cheque', 'Cheque'),
        ('tarjeta', 'Tarjeta'),
        ('credito', 'Crédito'),
        ('debito', 'Débito'),
        ('abono', 'Abono'),
        ('efectivo', 'Efectivo'),  
    
    ]
    empresa = models.ForeignKey(RegistroEmpresas, on_delete=models.CASCADE, related_name='pagos')
    vigencia_planes = models.ManyToManyField(VigenciaPlan, related_name='pagos_asociados')
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_pago = models.DateTimeField() 
    metodo = models.CharField(max_length=20, choices=METODO_PAGO_CHOICES)
    comprobante = models.FileField(upload_to='comprobantes/', blank=True, null=True)
    pagado = models.BooleanField(default=False)
    cobro = models.ForeignKey(Cobro, on_delete=models.CASCADE, related_name='pagos', null=True)
    
    # CAMBIO: Campos de auditoría para tener un registro detallado
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # CAMBIO: Campo de observaciones para comentarios internos o incidencias
    observaciones = models.TextField(blank=True, null=True)
    def save(self, *args, **kwargs):
        if self.cobro and not self.pk:
            self.empresa = self.cobro.empresa
        super().save(*args, **kwargs)
    def __str__(self):
        return f"Pago {self.id} - {self.empresa.nombre} ({self.fecha_pago})"
    class Meta:
           permissions = [
                ('Registrar_pago', 'permite registar un pago')
        ]


