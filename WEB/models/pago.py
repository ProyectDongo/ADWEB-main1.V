from django.db import models
from .empresa import RegistroEmpresas, VigenciaPlan
from .cobro import Cobro

    
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
