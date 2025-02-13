from wsgiref.validate import validator
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Max
from django.utils import timezone
from django.conf import settings
from .validators import validar_rut



class Region(models.Model):
    nombre = models.CharField(max_length=100)
    
    def __str__(self):
        return self.nombre

class Provincia(models.Model):
    nombre = models.CharField(max_length=100)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.nombre} ({self.region})"

class Comuna(models.Model):
    nombre = models.CharField(max_length=100)
    provincia = models.ForeignKey(Provincia, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.nombre} ({self.provincia})"

class Plan(models.Model):
    ESTADOS_CHOICES = [
        ('habilitado', 'Habilitado'),
        ('suspendido', 'Plan Suspendido'),
    ]
    estado = models.CharField(max_length=20, choices=ESTADOS_CHOICES, default='habilitado')
    nombre = models.CharField(max_length=100)
    max_usuarios = models.PositiveIntegerField()
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    codigo = models.CharField(max_length=20, unique=True)
    activo = models.BooleanField(default=True)
    descripcion = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Plan"
        verbose_name_plural = "Planes"

    def __str__(self):
        return f"{self.nombre} (U: {self.max_usuarios})"

class RegistroEmpresas(models.Model):
    ESTADO_CHOICES = [
        ('aldia', 'Al día'),
        ('atrasado', 'Atrasado'),
        ('suspendido', 'Plan Suspendido'),
    ]
    
    codigo_cliente = models.CharField(max_length=20, unique=True)
    fecha_ingreso = models.DateField(auto_now_add=True)
    rut = models.CharField(max_length=13, unique=True)
    nombre = models.CharField(max_length=100)
    giro = models.CharField(max_length=100)
    direccion = models.CharField(max_length=200)
    numero = models.CharField(max_length=20)
    oficina = models.CharField(max_length=20, blank=True)
    region = models.ForeignKey(Region, on_delete=models.PROTECT)
    provincia = models.ForeignKey(Provincia, on_delete=models.PROTECT)
    comuna = models.ForeignKey(Comuna, on_delete=models.PROTECT)
    telefono = models.CharField(max_length=20)
    celular = models.CharField(max_length=20, blank=True)
    email = models.EmailField()
    web = models.URLField(blank=True)
    vigente = models.BooleanField(default=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='aldia')
    
    rut_representante = models.CharField(max_length=12,validators=[validar_rut])
    nombre_representante = models.CharField(max_length=100)
    
    nombre_contacto = models.CharField(max_length=100)
    celular_contacto = models.CharField(max_length=20)
    mail_contacto = models.EmailField()
    
    plan_contratado = models.ForeignKey(Plan, on_delete=models.PROTECT, related_name='empresas')
    limite_usuarios = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Empresa"
        verbose_name_plural = "Empresas"

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        if not self.codigo_cliente:
            ultimo_id = RegistroEmpresas.objects.aggregate(Max('id'))['id__max'] or 0
            self.codigo_cliente = f"CLI-{ultimo_id + 1:06d}"
        
        if self.plan_contratado:
            self.limite_usuarios = self.plan_contratado.max_usuarios
            
        super().save(*args, **kwargs)

class Usuario(AbstractUser):
    ROLES = (
        ('admin', 'Administrador'),
        ('supervisor', 'Supervisor'),
        ('trabajador', 'Trabajador'),
    )
    role = models.CharField(max_length=20, choices=ROLES, default='trabajador')
    empresa = models.ForeignKey(
        RegistroEmpresas, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name="usuarios"
    )
    permisos = models.ManyToManyField("RegistroPermisos", blank=True, related_name='usuarios')
    rut = models.CharField(max_length=12, unique=True)
    
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

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

class RegistroPermisos(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

class RegistroEntrada(models.Model):
    trabajador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='entradas'
    )
    hora_entrada = models.DateTimeField(auto_now_add=True)
    hora_salida = models.DateTimeField(null=True, blank=True)
    permitir_otra_entrada = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Registro de Entrada"
        verbose_name_plural = "Registros de Entrada"
        ordering = ['-hora_entrada']

    def __str__(self):
        return f"{self.trabajador.username} - {self.hora_entrada.strftime('%Y-%m-%d %H:%M')}"

@receiver(post_save, sender=RegistroEntrada)
def notificar_registro_entrada(sender, instance, created, **kwargs):
    if created:
        print(f"Entrada registrada para {instance.trabajador.username} a las {instance.hora_entrada}")

class VigenciaPlan(models.Model):
    TIPO_DURACION = [
        ('indefinido', 'Indefinido'),
        ('mensual', 'Mensual'),
    ]
    empresa = models.ForeignKey(
        RegistroEmpresas,
        on_delete=models.CASCADE,
        related_name='vigencias'
    )
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT)
    fecha_inicio = models.DateField(default=timezone.now)
    fecha_fin = models.DateField(null=True, blank=True)
    monto_plan = models.DecimalField(max_digits=10, decimal_places=2)
    descuento = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    monto_final = models.DecimalField(max_digits=10, decimal_places=2)
    codigo_plan = models.CharField(max_length=50, unique=True)
    
    class Meta:
        verbose_name = "Vigencia de Plan"
        verbose_name_plural = "Vigencias de Planes"
        ordering = ['-fecha_inicio']

    def __str__(self):
        return f"{self.empresa} - {self.plan.nombre} ({self.fecha_inicio})"

    def calcular_monto(self):
        if self.plan.valor is None:
            raise ValueError("El plan no tiene un valor definido.")

        descuento_decimal = self.descuento / 100
        self.monto_plan = self.plan.valor
        self.monto_final = self.monto_plan * (1 - descuento_decimal)
        return self.monto_final

    def save(self, *args, **kwargs):
        self.calcular_monto()
        super().save(*args, **kwargs)

class HistorialCambios(models.Model):
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
    
