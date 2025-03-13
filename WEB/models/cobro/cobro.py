from django.db import models
from django.db.models import Sum
from ..empresa.empresa import RegistroEmpresas,VigenciaPlan


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
    ultima_actualizacion = models.DateTimeField(auto_now=True)
    
    def planes_asociados(self):
        if self.vigencia_plan:
            return [self.vigencia_plan]
        return self.vigencias_planes.all()
    vigencias_planes = models.ManyToManyField(VigenciaPlan, related_name='cobros_planes', blank=True)
    
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
 
    