from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Max
from django.utils import timezone

# clase para las regiones, provincias y comunas
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

# estos son los registros de los planes
class Plan(models.Model):
    nombre = models.CharField(max_length=100)
    max_supervisores = models.PositiveIntegerField()
    max_trabajadores = models.PositiveIntegerField()
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    codigo = models.CharField(max_length=20, unique=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} (S: {self.max_supervisores}, T: {self.max_trabajadores})"

# estos son los registro de las empresas
class RegistroEmpresas(models.Model):
    ESTADO_CHOICES = [
        ('aldia', 'Al día'),
        ('atrasado', 'Atrasado'),
        ('suspendido', 'Plan Suspendido'),
    ]
    
    # Información principal
    codigo_cliente = models.CharField(max_length=20, unique=True, blank=True)
    fecha_ingreso = models.DateField(auto_now_add=True)
    rut = models.CharField(max_length=12, unique=True, default='00000000-0')
    nombre = models.CharField(max_length=100, default='Nombre Empresa')
    giro = models.CharField(max_length=100, default='Giro Empresa')
    direccion = models.CharField(max_length=200, default='Dirección Empresa')
    numero = models.CharField(max_length=20, default='0')
    oficina = models.CharField(max_length=20, blank=True, default='Oficina')
    region = models.ForeignKey(Region, on_delete=models.PROTECT)
    provincia = models.ForeignKey(Provincia, on_delete=models.PROTECT)
    comuna = models.ForeignKey(Comuna, on_delete=models.PROTECT)
    telefono = models.CharField(max_length=20, default='0000000230')
    celular = models.CharField(max_length=20, blank=True, default='000000012')
    email = models.EmailField(blank=True, default='email@empresa.com')
    web = models.URLField(blank=True, default='http://www.empresa.com')
    vigente = models.BooleanField(default=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='aldia')
    
    # Representante Legal
    rut_representante = models.CharField(max_length=12, default='00000000-0')
    nombre_representante = models.CharField(max_length=100, default='Nombre Representante')
    
    # Contacto
    nombre_contacto = models.CharField(max_length=100, default='Nombre Contacto')
    celular_contacto = models.CharField(max_length=20, default='000000001')
    mail_contacto = models.EmailField(default='contacto@empresa.com')
    
    # Plan
    plan_contratado = models.ForeignKey(Plan, on_delete=models.PROTECT, related_name='empresas', default=1)
    
    # Límites
    limite_supervisores = models.PositiveIntegerField(default=0)
    limite_trabajadores = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        if not self.codigo_cliente:
            ultimo_id = RegistroEmpresas.objects.all().aggregate(Max('id'))['id__max'] or 0
            self.codigo_cliente = f"CLI-{ultimo_id + 1:06d}"
        
        # Asignar límites según el plan contratado
        if self.plan_contratado:
            self.limite_supervisores = self.plan_contratado.max_supervisores
            self.limite_trabajadores = self.plan_contratado.max_trabajadores
        
        super().save(*args, **kwargs)


    
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

#plan vigencia
class VigenciaPlan(models.Model):
    TIPO_DURACION = [
        ('indefinido', 'Indefinido'),
        ('mensual', 'Mensual'),
    ]
    
    empresa = models.ForeignKey(RegistroEmpresas, on_delete=models.CASCADE, related_name='vigencias')
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT)
    fecha_inicio = models.DateField(default=timezone.now)
    fecha_fin = models.DateField(null=True, blank=True)
    indefinido = models.BooleanField(default=False)
    monto_plan = models.DecimalField(max_digits=10, decimal_places=2)
    descuento = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    monto_final = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.empresa} - {self.plan} ({self.fecha_inicio} al {self.fecha_fin or 'Indefinido'})"
    
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