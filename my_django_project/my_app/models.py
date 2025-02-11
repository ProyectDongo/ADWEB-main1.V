from django.db import models

class VigenciaPlan(models.Model):
    empresa = models.ForeignKey('Empresa', on_delete=models.CASCADE)
    plan = models.ForeignKey('Plan', on_delete=models.CASCADE)
    codigo_plan = models.CharField(max_length=100)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)
    descuento = models.DecimalField(max_digits=5, decimal_places=2)
    precio_original = models.DecimalField(max_digits=10, decimal_places=2)
    precio_final = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.empresa} - {self.plan} ({self.fecha_inicio})"