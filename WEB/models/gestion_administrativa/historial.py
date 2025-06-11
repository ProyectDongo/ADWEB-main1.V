from django.db import models
from django.conf import settings
from .empresa import RegistroEmpresas
from ..usuarios.usuario import Usuario
from ..gestion_administrativa.transacciones import Pago



class HistorialCambios(models.Model):
    """
    Modelo que representa un registro en el historial de cambios de una empresa.

    Este modelo almacena información sobre modificaciones o acciones realizadas en una
    empresa, incluyendo el usuario que realizó el cambio, la fecha en que se efectuó y una
    descripción detallada del cambio.

    Atributos:
        empresa (ForeignKey): Relación con el modelo RegistroEmpresas, representa la empresa
            a la que corresponde el cambio. Se elimina en cascada.
        usuario (ForeignKey): Relación con el modelo de usuario (settings.AUTH_USER_MODEL) que realizó
            el cambio. Si el usuario es eliminado, se asigna el valor null.
        fecha (DateTimeField): Fecha y hora en que se registra el cambio, asignada automáticamente al crear el registro.
        descripcion (TextField): Descripción detallada del cambio realizado.

    Meta:
        verbose_name: "Historial de Cambios"
        verbose_name_plural: "Historial de Cambios"
        ordering: Lista los registros en orden descendente por fecha.

    Métodos:
        __str__: Retorna una representación en cadena del historial en formato "AAAA-MM-DD HH:MM - usuario".
    """
    empresa = models.ForeignKey(RegistroEmpresas, on_delete=models.CASCADE)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    fecha = models.DateTimeField(auto_now_add=True)
    descripcion = models.TextField()

    class Meta:
        verbose_name = "Historial de Cambios"
        verbose_name_plural = "Historial de Cambios"
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.fecha.strftime('%Y-%m-%d %H:%M')} - {self.usuario}"
