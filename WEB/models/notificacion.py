from django.db import models
from .empresa import RegistroEmpresas
from .usuario import Usuario

class EmailNotification(models.Model):
    subject = models.CharField(max_length=255)
    sender = models.CharField(max_length=255)
    received_date = models.DateTimeField()
    procesado = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.subject} - {self.sender}"

class HistorialNotificaciones(models.Model):
    empresa = models.ForeignKey(RegistroEmpresas, on_delete=models.CASCADE)
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    fecha_envio = models.DateTimeField(auto_now_add=True)
    estado = models.BooleanField(default=True)
    
    class Meta:
        verbose_name_plural = "Historial de Notificaciones"
        ordering = ['-fecha_envio']