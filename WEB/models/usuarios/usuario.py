from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from WEB.models.empresa.empresa import *
from WEB.views.scripts import *


class Usuario(AbstractUser):
    """
    Modelo que extiende AbstractUser para representar a un usuario en el sistema.

    Este modelo incorpora campos adicionales a los definidos en AbstractUser para
    manejar roles específicos (Administrador, Supervisor, Trabajador), la asociación
    a una empresa y permisos adicionales personalizados.

    Atributos:
        role (CharField): Rol del usuario, con opciones:
            - 'admin' para Administrador,
            - 'supervisor' para Supervisor,
            - 'trabajador' para Trabajador.
            Valor por defecto: 'trabajador'.
        empresa (ForeignKey): Relación con el modelo RegistroEmpresas, que define la empresa
            a la que pertenece el usuario. Este campo es opcional.
        permisos (ManyToManyField): Relación con el modelo RegistroPermisos para asignar
            permisos personalizados al usuario.
        rut (CharField): RUT del usuario, debe ser único y se valida mediante la función 'validar_rut'.
            Se permite que esté en blanco.
        apellidoM (CharField): Apellido materno del usuario (opcional).
        nombre (CharField): Nombre del usuario.
        celular (CharField): Número de celular del usuario (opcional).
        email (EmailField): Correo electrónico del usuario.
        groups (ManyToManyField): Grupos a los que pertenece el usuario.
        user_permissions (ManyToManyField): Permisos específicos asignados al usuario.

    Meta:
        verbose_name: "Usuario"
        verbose_name_plural: "Usuarios"

    Métodos:
        __str__: Retorna una representación en cadena del usuario, que incluye el nombre
                 de usuario y la descripción de su rol.
    """
    ROLES = (
        ('admin', 'Administrador'),
        ('supervisor', 'Supervisor'),
        ('trabajador', 'Trabajador'),
    )
    role = models.CharField(max_length=20, choices=ROLES, default='admin')
    empresa = models.ForeignKey(
        RegistroEmpresas, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name="usuarios"
    )
    
    rut = models.CharField(max_length=12, unique=True, validators=[validar_rut], blank=True)
    apellidoM = models.CharField(max_length=12, blank=True)
    nombre = models.CharField(max_length=100)
    celular = models.CharField(max_length=20, blank=True)
    email = models.EmailField()

    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        related_name='usuario_groups',
        help_text='Grupos a los que pertenece el usuario'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        related_name='usuario_permissions',
        help_text='Permisos específicos para este usuario'
    )
    #seguridad 
    is_locked = models.BooleanField(
        default=False,
        verbose_name="Cuenta bloqueada",
        help_text="Indica si la cuenta está bloqueada por seguridad"
    )
    
    #  campo para seguimiento de intentos fallidos
    failed_login_attempts = models.PositiveIntegerField(
        default=0,
        verbose_name="Intentos fallidos"
    )
    
    # Fecha del último intento fallido
    last_failed_login = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Último intento fallido"
    )
    

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
        """
        Retorna una representación en cadena del usuario.

        :return: Cadena con el formato "username (Rol)", donde Rol es la descripción del rol.
        """
        return f"{self.username} ({self.get_role_display()})"
    


#modelo parafurutro uso
class AuditoriaAcceso(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    exito = models.BooleanField(default=False)
    motivo = models.TextField(blank=True)