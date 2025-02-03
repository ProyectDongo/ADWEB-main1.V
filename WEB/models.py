from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db.models.signals import post_save
from django.dispatch import receiver

# estos son los registro de las empresas
class RegistroEmpresas(models.Model):
    rut= models.CharField(max_length=12, unique=True,default="00000000-0")
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=200, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    limite_supervisores = models.PositiveIntegerField(default=5)
    limite_trabajadores = models.PositiveIntegerField(default=50)

    def __str__(self):
        return self.nombre
    
#estos los registros todos

class Usuario(AbstractUser):
    ROLES = (
        ('admin', 'Administrador'),
        ('supervisor', 'Supervisor'),
        ('trabajador', 'Trabajador'),
    )
    role = models.CharField(max_length=20, choices=ROLES, default='trabajador')
    empresa = models.ForeignKey("RegistroEmpresas", on_delete=models.CASCADE, null=True, blank=True, related_name="usuarios")
    permisos = models.ManyToManyField("RegistroPermisos", blank=True, related_name='usuarios')  # Nueva relación

    # Evitar conflicto con auth.User
    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        related_name='usuario_groups'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        related_name='usuario_permissions'
    )
    

    def __str__(self):
        return f"{self.username} ({self.get_rol_display()})"
    
    
#estos son los registros de los permisos   
class RegistroPermisos(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre
    
# estos son los registros de las entradas
class RegistroEntrada(models.Model):
    trabajador = models.ForeignKey('Usuario', on_delete=models.CASCADE, related_name='entradas')
    hora_entrada = models.DateTimeField(auto_now_add=True)
    hora_salida = models.DateTimeField(null=True, blank=True)
    permitir_otra_entrada = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.trabajador.username} - Entrada: {self.hora_entrada} - Salida: {self.hora_salida}"

@receiver(post_save, sender=RegistroEntrada)
def notificar_registro_entrada(sender, instance, created, **kwargs):
    if created:
        print(f"Entrada registrada para {instance.trabajador.username} a las {instance.hora_entrada}")