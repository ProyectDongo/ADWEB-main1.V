from django.db import models
# from django.contrib.gis.db import models  # Línea comentada, posiblemente para usar funcionalidades de geolocalización avanzada en el futuro
from django.conf import settings  # Importa configuraciones globales de Django, como el modelo de usuario personalizado
from django.db.models.signals import post_save  # Para conectar señales que se ejecutan tras guardar un objeto
from django.dispatch import receiver  # Decorador para manejar señales
from django.core.exceptions import ValidationError  # Excepción para validaciones personalizadas
from WEB.models import RegistroEmpresas,VigenciaPlan  # Importa el modelo RegistroEmpresas desde la app WEB
from django.utils import timezone  # Utilidad para manejar zonas horarias
from datetime import datetime, timedelta  # Para operaciones con fechas y horas





class RegistroEntrada(models.Model):
    """
    Modelo para registrar las entradas y salidas de los trabajadores.
    Permite diferentes métodos de registro como firma digital, huella digital o geolocalización.
    """

    # Constantes que definen los métodos de registro permitidos
    METODOS_REGISTRO = [
        ('firma', 'Firma Digital'),  # Opción para registrar con firma digital
        ('huella', 'Huella Digital'),  # Opción para registrar con huella digital
        ('geo', 'Geolocalización'),  # Opción para registrar con geolocalización
    ]

    # Campos del modelo
    trabajador = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,  # Si el trabajador es eliminado, se eliminan sus registros
        related_name='entradas'  # Permite acceder a los registros de entrada desde el objeto trabajador (ej. trabajador.entradas)
    )
    """
    Define la relación con el trabajador que registra su entrada.
    """

    metodo = models.CharField(max_length=20, choices=METODOS_REGISTRO)
    """
    Campo que almacena el método de registro usado.
    - Limita las opciones a las definidas en METODOS_REGISTRO.
    """

    hora_entrada = models.DateTimeField(auto_now_add=True)
    """
    Registra automáticamente la fecha y hora en que se crea el objeto.
    - Útil para marcar la entrada del trabajador.
    """

    hora_salida = models.DateTimeField(null=True, blank=True)
    """
    Registra la hora de salida del trabajador.
    - Es opcional (puede ser null), ya que se puede actualizar más tarde.
    """

    latitud = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitud = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    """
    Campos para almacenar las coordenadas de geolocalización (latitud y longitud).
    - Usados cuando el método es 'geo'.
    - Precisión de 6 decimales para mayor exactitud (aproximadamente 11 cm).
    - Opcionales, ya que no todos los métodos los requieren.
    """

    firma_digital = models.TextField(null=True, blank=True)
    """
    Almacena la firma digital del trabajador.
    - Usado cuando el método es 'firma'.
    - Opcional, ya que depende del método seleccionado.
    """

    huella_id = models.CharField(max_length=100, null=True, blank=True)
    """
    Identificador único de la huella digital del trabajador.
    - Usado cuando el método es 'huella'.
    - Opcional, según el método de registro.
    """

    huella_validada = models.BooleanField(default=False)
    """
    Indica si la huella digital ha sido validada correctamente.
    - Por defecto es False hasta que se confirme la validación.
    """

    empresa = models.ForeignKey(
        'RegistroEmpresas',  # Relación con el modelo RegistroEmpresas (usando string para evitar problemas de importación)
        on_delete=models.CASCADE,  # Si la empresa es eliminada, se eliminan los registros asociados
        related_name='registros_asistencia',  # Permite acceder a los registros desde el objeto empresa (ej. empresa.registros_asistencia)
        null=True, blank=True  # Opcional en la definición, pero se asigna automáticamente en save()
    )
    """
    Relación con la empresa a la que pertenece el trabajador.
    """

    precision = models.FloatField(null=True, blank=True)
    """
    Almacena la precisión de la geolocalización (en metros, por ejemplo).
    - Opcional, usado solo con el método 'geo'.
    """

    es_retraso = models.BooleanField(default=False)
    """
    Indica si la entrada se considera un retraso.
    - Por defecto False, se actualiza según lógica de negocio.
    """

    minutos_retraso = models.IntegerField(default=0)
    """
    Cantidad de minutos de retraso, si es_retraso es True.
    - Por defecto 0.
    """

    es_horas_extra = models.BooleanField(default=False)
    """
    Indica si el registro incluye horas extras trabajadas.
    - Por defecto False.
    """

    minutos_horas_extra = models.IntegerField(default=0)
    """
    Cantidad de minutos de horas extras trabajadas.
    - Por defecto 0.
    """

    class Meta:
        """
        Clase interna para definir metadatos del modelo.
        """
        permissions = [
            ('registro_asistencia', 'Acceso al módulo de asistencia'),  # Permiso personalizado para controlar acceso al módulo
        ]
        """
        Define permisos adicionales para el modelo en el sistema de autenticación de Django.
        """

    def esta_dentro_rango(self, empresa):
        """
        Método para verificar si la ubicación del registro está dentro del rango permitido por la empresa.
        - Recibe el objeto empresa como parámetro.
        - Actualmente retorna False (parece no estar implementado aún).
        """
        return False

    def clean(self):
        """
        Método para realizar validaciones personalizadas antes de guardar el objeto.
        - Se ejecuta automáticamente en formularios o al llamar a full_clean().
        """
        if not self.pk:  # Solo aplica a objetos nuevos (sin ID asignado)
            if self.empresa is None:
                raise ValidationError("Debe asociar una empresa al registro de entrada.")  # Valida que haya una empresa
            # Verifica si la empresa tiene un plan de asistencia activo
            tiene_plan_asistencia = self.empresa.vigencias.filter(
                plan__nombre__iexact='asistencia',  # Busca un plan llamado 'asistencia' (insensible a mayúsculas)
                estado='indefinido'  # Estado indefinido indica que está activo
            ).exists()
            if not tiene_plan_asistencia:
                raise ValidationError("La empresa no tiene un plan de asistencia activo")  # Error si no hay plan
            # Verifica si se excede el límite de usuarios de la empresa
            if self.empresa.usuarios.count() >= self.empresa.limite_usuarios:
                raise ValidationError("Límite de usuarios excedido para este plan")  # Error si se supera el límite

    def save(self, *args, **kwargs):
        """
        Sobrescribe el método save() para asignar automáticamente la empresa del trabajador.
        """
        self.empresa = self.trabajador.empresa  # Asigna la empresa asociada al trabajador
        super().save(*args, **kwargs)  # Llama al método save() original para guardar el objeto

@receiver(post_save, sender=RegistroEntrada)
def notificar_registro_entrada(sender, instance, created, **kwargs):
    """
    Función que se ejecuta después de guardar un RegistroEntrada (conectada a la señal post_save).
    - sender: Modelo que dispara la señal (RegistroEntrada).
    - instance: Instancia del objeto guardado.
    - created: Booleano que indica si el objeto fue creado (True) o actualizado (False).
    """
    if created:  # Solo se ejecuta al crear un nuevo registro
        # Imprime un mensaje en la consola (esto podría ser un placeholder para una notificación real)
        print(f"Entrada registrada para {instance.trabajador.username} a las {instance.hora_entrada}")

