from django.db import models
from django.conf import settings
from WEB.models import RegistroEmpresas
from users.models import Usuario


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
    vigencia_plan = models.ForeignKey('VigenciaPlan', on_delete=models.SET_NULL, null=True, blank=True)  # Relación añadida

    class Meta:
        verbose_name_plural = "Historial de Notificaciones"
        ordering = ['-fecha_envio']


class Notificacion(models.Model):
    TIPO_CHOICES = [
        ('entrada', 'Entrada'),
        ('salida', 'Salida'),
        ('retraso', 'Retraso'),
    ]
    worker = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notificaciones'
    )
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    leido = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.worker.get_full_name()} - {self.get_tipo_display()} - {self.timestamp}"
