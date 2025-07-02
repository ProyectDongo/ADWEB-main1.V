from django.db import models
from WEB.models import RegistroEmpresas

# Modelo para representar un ítem de inventario
class ItemInventario(models.Model):
    empresa = models.ForeignKey(RegistroEmpresas, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    codigo = models.CharField(max_length=50)
    categoria = models.CharField(max_length=50)
    stock = models.IntegerField()