from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from WEB.models.empresa.empresa import RegistroEmpresas
from WEB.views.scripts import validar_rut
from WEB.models import *
from django.core.validators import MinValueValidator, MaxValueValidator




class Horario(models.Model):
    TIPO_HORARIO = [
        ('diurno', 'Diurno'),
        ('nocturno', 'Nocturno'),
        ('mixto', 'Mixto'),
    ]
    nombre = models.CharField(max_length=100)
    hora_entrada = models.TimeField()
    hora_salida = models.TimeField()
    tolerancia_retraso = models.IntegerField(default=20, validators=[MinValueValidator(0), MaxValueValidator(60)])  # in minutes
    tolerancia_horas_extra = models.IntegerField(default=20, validators=[MinValueValidator(0), MaxValueValidator(60)])
    tipo_horario = models.CharField(max_length=20, choices=TIPO_HORARIO, default='diurno') 
    empresa = models.ForeignKey('RegistroEmpresas', on_delete=models.CASCADE, related_name='horarios')

    def __str__(self):
        return f"{self.nombre} ({self.hora_entrada} - {self.hora_salida}) - {self.get_tipo_horario_display()}"

class Turno(models.Model):
    nombre = models.CharField(max_length=100)
    dias_trabajo = models.IntegerField()
    dias_descanso = models.IntegerField()
    inicio_turno = models.DateField(null=True, blank=True) 
    empresa = models.ForeignKey('RegistroEmpresas', on_delete=models.CASCADE, related_name='turnos')

    def __str__(self):
        return f"{self.nombre} ({self.dias_trabajo}x{self.dias_descanso})"



class Usuario(AbstractUser):
    ROLES = (
        ('admin', 'Administrador'),
        ('supervisor', 'Supervisor'),
        ('trabajador', 'Trabajador'),
    )
    METODOS_REGISTRO = [
        ('firma', 'Firma Digital'),
        ('huella', 'Huella Digital'),
        ('geo', 'Geolocalización'),
    ]
    role = models.CharField(max_length=20, choices=ROLES, default='admin')
    empresa = models.ForeignKey(
        'RegistroEmpresas', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name="usuarios"
    )
    rut = models.CharField(max_length=12, unique=True, blank=True)  # Assuming validar_rut is defined
    celular = models.CharField(max_length=20, blank=True)
    email = models.EmailField()
    vigencia_plan = models.ForeignKey('VigenciaPlan', on_delete=models.CASCADE, related_name='usuarios', null=True, blank=True)
    
    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        related_name='usuarios',
        help_text='Grupos a los que pertenece el usuario'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        related_name='usuarios',
        help_text='Permisos específicos para este usuario'
    )
    is_locked = models.BooleanField(
        default=False,
        verbose_name="Cuenta bloqueada",
        help_text="Indica si la cuenta está bloqueada por seguridad"
    )
    failed_login_attempts = models.PositiveIntegerField(
        default=0,
        verbose_name="Intentos fallidos"
    )
    last_failed_login = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Último intento fallido"
    )
    horario = models.ForeignKey(Horario, on_delete=models.SET_NULL, null=True, blank=True, related_name='usuarios')
    turno = models.ForeignKey(Turno, on_delete=models.SET_NULL, null=True, blank=True, related_name='usuarios')
    metodo_registro_permitido = models.CharField(
        max_length=20,
        choices=[('firma', 'Firma Digital'), ('huella', 'Huella Digital'), ('geo', 'Geolocalización')],
        default='firma'
    )

    @property
    def has_huella(self):
        """Verifica si el usuario tiene una huella asociada."""
        return hasattr(self, 'huellas')

    def debe_trabajar(self, fecha):
        if not self.turno or not self.turno.inicio_turno:
            return True 
        ciclo_total = self.turno.dias_trabajo + self.turno.dias_descanso
        dias_desde_inicio = (fecha - self.turno.inicio_turno).days % ciclo_total
        return dias_desde_inicio < self.turno.dias_trabajo

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        permissions = [
            ("eliminar_trabajador", "Permiso para eliminar trabajadores"),
            ("eliminar_supervisor", "Permiso para eliminar supervisores"),
            ("eliminar_admin", "Permiso para eliminar administradores"),
            ("crear_admin", "Permiso para crear administradores"),
            ("crear_supervisor", "Permiso para crear supervisores"),
            ("crear_trabajador", "Permiso para crear trabajadores"),
            ("editar_supervisor", "permiso para editar supervisores"),
            ("editar_trabajador", "permiso para editar trabajadores"),
        ]

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    














    
class AuditoriaAcceso(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    exito = models.BooleanField(default=False)
    motivo = models.TextField(blank=True)