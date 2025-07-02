from django.db import models
from django.db.models import Sum
from WEB.models import RegistroEmpresas,VigenciaPlan
from users.models import Usuario


class Cobro(models.Model):
    empresa = models.ForeignKey(RegistroEmpresas, on_delete=models.CASCADE, related_name='cobros')
    vigencia_plan = models.ForeignKey(
        VigenciaPlan, 
        on_delete=models.CASCADE, 
        related_name='cobros_relacionados',  
        null=True, 
        blank=True
    )
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
           
class HistorialPagos(models.Model):
    pago = models.ForeignKey(Pago, on_delete=models.CASCADE, related_name='historial')
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)
    descripcion = models.TextField()

    def __str__(self):
        return f"Historial Pago {self.pago.id} - {self.fecha.strftime('%Y-%m-%d %H:%M')}"
    

    