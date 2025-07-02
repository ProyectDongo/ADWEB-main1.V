from django.db import models
from WEB.models import RegistroEmpresas
# Create your models here.
# Modelo para representar una transacción financiera
class Transaccion(models.Model):
    empresa = models.ForeignKey(RegistroEmpresas, on_delete=models.CASCADE)
    fecha = models.DateField()
    descripcion = models.TextField()
    tipo = models.CharField(max_length=10)  # Ej: 'Ingreso', 'Egreso'
    monto = models.DecimalField(max_digits=10, decimal_places=2)